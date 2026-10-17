
import json
from pathlib import Path

import numpy as np
from sentence_transformers import CrossEncoder


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

FACTCHECK_INPUT = BASE_DIR / "top10_ranked_factchecks.json"
ARTICLE_INPUT = OUTPUT_DIR / "top10_ranked_articles.json"

FACTCHECK_OUTPUT = OUTPUT_DIR / "nli_factchecks.json"
ARTICLE_OUTPUT = OUTPUT_DIR / "nli_articles.json"

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"
MAX_EVIDENCE_CHARS = 2500
BATCH_SIZE = 16


def load_json(path):
    if not path.exists():
        print(f"Input file not found: {path}")
        return {}

    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_records(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "results",
            "ranked_records",
            "ranked_articles",
            "articles",
            "claims",
            "records",
            "items",
        ):
            if isinstance(data.get(key), list):
                return data[key]

    return []


def clean_text(value):
    if not isinstance(value, str):
        return ""

    return " ".join(value.split()).strip()


def extract_evidence(item):
    """Extract the most informative available text."""

    if not isinstance(item, dict):
        return clean_text(str(item))

    parts = []

    # Fact-check records often contain claimReview.
    reviews = item.get("claimReview", [])
    if isinstance(reviews, dict):
        reviews = [reviews]

    if isinstance(reviews, list):
        for review in reviews:
            if not isinstance(review, dict):
                continue

            for key in (
                "title",
                "textualRating",
                "reviewBody",
                "publisher",
            ):
                value = clean_text(review.get(key))
                if value:
                    parts.append(value)

    # Medical article records.
    for key in (
        "title",
        "abstract",
        "snippet",
        "summary",
        "text",
        "evidence",
    ):
        value = clean_text(item.get(key))
        if value:
            parts.append(value)

    # Some records store evidence in nested dictionaries.
    for key in ("article", "metadata"):
        nested = item.get(key)

        if isinstance(nested, dict):
            for nested_key in ("title", "abstract", "snippet", "text"):
                value = clean_text(nested.get(nested_key))
                if value:
                    parts.append(value)

    # Deduplicate repeated pieces while preserving their order.
    unique_parts = list(dict.fromkeys(parts))

    return " ".join(unique_parts)[:MAX_EVIDENCE_CHARS]


def get_label_mapping(model):
    """Read the actual model label names when available."""

    config = getattr(model.model, "config", None)
    id2label = getattr(config, "id2label", None)

    if isinstance(id2label, dict) and id2label:
        mapping = {}

        for index, label in id2label.items():
            try:
                mapping[int(index)] = str(label).lower()
            except (ValueError, TypeError):
                continue

        if mapping:
            return mapping

    # This fallback matches the commonly used NLI model ordering.
    # Verify it against the installed model configuration.
    print(
        "Warning: model label mapping unavailable; "
        "using the documented fallback ordering."
    )

    return {
        0: "contradiction",
        1: "entailment",
        2: "neutral",
    }


def normalize_label(label):
    label = str(label).lower()

    if "contrad" in label:
        return "contradiction"

    if "entail" in label or "support" in label:
        return "entailment"

    if "neutral" in label:
        return "neutral"

    return "unknown"


def classify_records(claim, items, model, label_mapping):
    prepared = []

    for item in items:
        evidence = extract_evidence(item)

        if len(evidence) < 20:
            continue

        prepared.append((item, evidence))

    if not prepared:
        return []

    # NLI pair order:
    # premise = retrieved evidence
    # hypothesis = claim being evaluated
    pairs = [
        (evidence, claim)
        for _, evidence in prepared
    ]

    raw_scores = model.predict(
        pairs,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        apply_softmax=True,
    )

    raw_scores = np.asarray(raw_scores)

    if raw_scores.ndim == 1:
        raw_scores = raw_scores.reshape(1, -1)

    results = []

    for (item, evidence), scores in zip(prepared, raw_scores):
        scores = scores.tolist()

        score_map = {}
        for index, score in enumerate(scores):
            raw_label = label_mapping.get(index, f"label_{index}")
            label = normalize_label(raw_label)

            if label != "unknown":
                score_map[label] = float(score)

        if not score_map:
            predicted_label = "unknown"
            confidence = None
        else:
            predicted_label = max(
                score_map,
                key=score_map.get,
            )
            confidence = score_map[predicted_label]

        output_item = dict(item) if isinstance(item, dict) else {
            "original_record": str(item)
        }

        output_item.update({
            "nli_label": predicted_label,
            "nli_confidence": confidence,
            "nli_scores": score_map,
            "nli_evidence_text": evidence,
        })

        results.append(output_item)

    return results


def main():
    print("=" * 55)
    print("NLI EVIDENCE CLASSIFIER")
    print("=" * 55)

    factcheck_data = load_json(FACTCHECK_INPUT)
    article_data = load_json(ARTICLE_INPUT)

    factchecks = get_records(factcheck_data)
    articles = get_records(article_data)

    claim = ""

    for data in (factcheck_data, article_data):
        if isinstance(data, dict) and data.get("user_claim"):
            claim = clean_text(data["user_claim"])
            break

    if not claim:
        claim = clean_text(input("Enter the health claim: "))

    if not claim:
        print("No claim supplied. Exiting.")
        return

    if not factchecks and not articles:
        print("No ranked records found. Run retrieval and ranking first.")
        return

    print(f"\nClaim: {claim}")
    print(f"Fact-check records: {len(factchecks)}")
    print(f"Article records: {len(articles)}")

    print(f"\nLoading model: {MODEL_NAME}")
    model = CrossEncoder(MODEL_NAME)

    label_mapping = get_label_mapping(model)
    print("Model labels:", label_mapping)

    factcheck_results = classify_records(
        claim, factchecks, model, label_mapping
    )

    article_results = classify_records(
        claim, articles, model, label_mapping
    )

    save_json(
        FACTCHECK_OUTPUT,
        {
            "user_claim": claim,
            "model": MODEL_NAME,
            "results": factcheck_results,
            "total_input_records": len(factchecks),
            "classified_records": len(factcheck_results),
        },
    )

    save_json(
        ARTICLE_OUTPUT,
        {
            "user_claim": claim,
            "model": MODEL_NAME,
            "results": article_results,
            "total_input_records": len(articles),
            "classified_records": len(article_results),
        },
    )

    print("\nNLI classification completed.")
    print(f"Fact-check output: {FACTCHECK_OUTPUT}")
    print(f"Article output: {ARTICLE_OUTPUT}")
    print(
        "\nRemember: NLI measures textual relationships; "
        "it does not independently verify medical truth."
    )


if __name__ == "__main__":
    main()
