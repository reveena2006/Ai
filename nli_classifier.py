
import os
import json
import gc
from pathlib import Path

import torch
from sentence_transformers import CrossEncoder


# --------------------------------------------------
# Configuration for low-memory hosting
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

FACTCHECK_INPUT = BASE_DIR / "top10_ranked_factchecks.json"
ARTICLE_INPUT = OUTPUT_DIR / "top10_ranked_articles.json"

FACTCHECK_OUTPUT = OUTPUT_DIR / "nli_factchecks.json"
ARTICLE_OUTPUT = OUTPUT_DIR / "nli_articles.json"

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"

BATCH_SIZE = 2
MAX_EVIDENCE_CHARS = 1200
MAX_RECORDS_PER_SOURCE = 10
MAX_LENGTH = 384


# --------------------------------------------------
# JSON helpers
# --------------------------------------------------

def load_json(path):
    """Load a JSON file safely."""
    if not path.exists():
        print(f"[WARNING] File not found: {path}")
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ("results", "records", "articles", "factchecks", "data"):
                if isinstance(data.get(key), list):
                    return data[key]

            return [data]

        return []

    except (json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] Could not read {path}: {exc}")
        return []


def save_json(path, data):
    """Write JSON output, creating the output directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(path.suffix + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    os.replace(temporary_path, path)


def get_text(record, keys):
    """Return the first usable text field from a record."""
    for key in keys:
        value = record.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def get_evidence_text(record):
    """Extract and shorten evidence text to limit memory use."""
    text = get_text(
        record,
        (
            "text",
            "snippet",
            "content",
            "abstract",
            "description",
            "summary",
            "claim",
            "title",
        ),
    )

    if not text:
        text = str(record.get("title", ""))

    return text[:MAX_EVIDENCE_CHARS]


def get_claim_text(record):
    """Extract the health claim being checked."""
    return get_text(
        record,
        (
            "claim",
            "query",
            "health_claim",
            "statement",
            "original_claim",
        ),
    )


# --------------------------------------------------
# NLI label helpers
# --------------------------------------------------

def normalize_label(label):
    """Normalize model labels into standard NLI classes."""
    label = str(label).strip().lower()

    if "contradiction" in label:
        return "contradiction"

    if "entailment" in label:
        return "entailment"

    if "neutral" in label:
        return "neutral"

    return label


def get_label_names(model):
    """Read class labels from the loaded model configuration."""
    try:
        config = model.model.config
        id2label = getattr(config, "id2label", {}) or {}

        labels = {}

        for index, label in id2label.items():
            try:
                labels[int(index)] = normalize_label(label)
            except (TypeError, ValueError):
                continue

        if labels:
            return labels

    except Exception as exc:
        print(f"[WARNING] Could not read model labels: {exc}")

    # Fallback for the common DeBERTa NLI label mapping.
    return {
        0: "contradiction",
        1: "neutral",
        2: "entailment",
    }


# --------------------------------------------------
# Classification
# --------------------------------------------------

def classify_records(records, model, label_names, source_name):
    """Classify evidence records in small batches."""
    if not records:
        print(f"[INFO] No {source_name} records to classify.")
        return []

    records = records[:MAX_RECORDS_PER_SOURCE]
    results = []

    claim_pairs = []
    valid_indices = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        claim = get_claim_text(record)
        evidence = get_evidence_text(record)

        if not claim or not evidence:
            updated = dict(record)
            updated["nli_label"] = "unavailable"
            updated["nli_confidence"] = None
            updated["nli_scores"] = {}
            updated["nli_evidence_text"] = evidence
            results.append((index, updated))
            continue

        # Premise = evidence; hypothesis = claim.
        claim_pairs.append([evidence, claim])
        valid_indices.append(index)

    predictions_by_index = {}

    if claim_pairs:
        print(
            f"[INFO] Classifying {len(claim_pairs)} "
            f"{source_name} records with batch size {BATCH_SIZE}."
        )

        # Process small chunks instead of predicting everything at once.
        for start in range(0, len(claim_pairs), BATCH_SIZE):
            end = start + BATCH_SIZE
            batch_pairs = claim_pairs[start:end]

            predictions = model.predict(
                batch_pairs,
                batch_size=BATCH_SIZE,
                show_progress_bar=False,
                convert_to_numpy=True,
                apply_softmax=True,
            )

            for offset, scores in enumerate(predictions):
                original_index = valid_indices[start + offset]

                score_values = [
                    float(value) for value in scores
                ]

                label_scores = {
                    label_names.get(i, f"label_{i}"): score
                    for i, score in enumerate(score_values)
                }

                if score_values:
                    best_index = max(
                        range(len(score_values)),
                        key=lambda i: score_values[i],
                    )

                    predicted_label = label_names.get(
                        best_index,
                        f"label_{best_index}",
                    )

                    confidence = score_values[best_index]
                else:
                    predicted_label = "unavailable"
                    confidence = None

                predictions_by_index[original_index] = {
                    "nli_label": predicted_label,
                    "nli_confidence": confidence,
                    "nli_scores": label_scores,
                }

            del predictions
            del batch_pairs
            gc.collect()

    # Preserve input order and original record fields.
    output = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        updated = dict(record)
        prediction = predictions_by_index.get(index)

        if prediction:
            updated.update(prediction)
            updated["nli_evidence_text"] = get_evidence_text(record)

        elif "nli_label" not in updated:
            updated["nli_label"] = "unavailable"
            updated["nli_confidence"] = None
            updated["nli_scores"] = {}
            updated["nli_evidence_text"] = get_evidence_text(record)

        output.append(updated)

    print(f"[INFO] Finished {source_name}: {len(output)} records.")
    return output


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] Loading ranked evidence files...")

    factchecks = load_json(FACTCHECK_INPUT)
    articles = load_json(ARTICLE_INPUT)

    print(f"[INFO] Fact-check records: {len(factchecks)}")
    print(f"[INFO] Article records: {len(articles)}")

    if not factchecks and not articles:
        print(
            "[ERROR] No ranked evidence found. "
            "Check the input paths and run the ranking pipeline first."
        )
        return

    # CPU inference avoids GPU allocation and is more predictable on
    # Streamlit Community Cloud, although it may take longer.
    print(f"[INFO] Loading NLI model: {MODEL_NAME}")

    model = CrossEncoder(
        MODEL_NAME,
        device="cpu",
        max_length=MAX_LENGTH,
    )

    label_names = get_label_names(model)
    print(f"[INFO] Model labels: {label_names}")

    factcheck_results = classify_records(
        factchecks,
        model,
        label_names,
        "fact-check",
    )

    save_json(FACTCHECK_OUTPUT, factcheck_results)
    print(f"[INFO] Saved: {FACTCHECK_OUTPUT}")

    # Release temporary objects before processing the second source.
    gc.collect()

    article_results = classify_records(
        articles,
        model,
        label_names,
        "PubMed article",
    )

    save_json(ARTICLE_OUTPUT, article_results)
    print(f"[INFO] Saved: {ARTICLE_OUTPUT}")

    del model
    gc.collect()

    print("[SUCCESS] NLI classification completed.")


if __name__ == "__main__":
    main()
