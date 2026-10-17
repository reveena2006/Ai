
import os
import json
import gc
from pathlib import Path

from sentence_transformers import CrossEncoder


# --------------------------------------------------
# Configuration: low-memory hosting
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
    """Load JSON and return the original data structure."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_json(path, data):
    """Write JSON safely using a temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    os.replace(temporary_path, path)


def extract_records(data, source_name):
    """Support lists and common project JSON wrapper formats."""
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        raise ValueError(
            f"{source_name} input must be a JSON list or object."
        )

    candidate_keys = (
        "results",
        "ranked_factchecks",
        "ranked_articles",
        "articles",
        "factchecks",
        "claims",
        "records",
        "data",
    )

    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, list):
            return value

    # A single record is accepted, but an unexpected wrapper is not
    # silently treated as evidence.
    if any(key in data for key in ("title", "abstract", "claim_text")):
        return [data]

    raise ValueError(
        f"Could not find a record list in {source_name}. "
        f"Available keys: {list(data.keys())}"
    )


def extract_user_claim(data):
    """Read the original user claim from a ranking file."""
    if isinstance(data, dict):
        claim = data.get("user_claim")
        if isinstance(claim, str) and claim.strip():
            return claim.strip()
    return ""


def get_text(record, keys):
    """Return the first non-empty string among the supplied fields."""
    if not isinstance(record, dict):
        return ""

    for key in keys:
        value = record.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


# --------------------------------------------------
# Claim and evidence extraction
# --------------------------------------------------

def get_claim_text(record, user_claim=""):
    """
    Always use the original user claim when available.

    A retrieved fact-check's claim_text is not necessarily the
    same claim the user submitted.
    """
    if isinstance(user_claim, str) and user_claim.strip():
        return user_claim.strip()

    # Fallback for standalone use when no original claim is available.
    return get_text(
        record,
        (
            "claim",
            "claim_text",
            "query",
            "health_claim",
            "statement",
            "original_claim",
        ),
    )


def get_evidence_text(record):
    """Extract evidence from PubMed or Google Fact Check records."""
    if not isinstance(record, dict):
        return ""

    parts = []

    # PubMed article fields.
    title = get_text(record, ("title",))
    abstract = get_text(record, ("abstract", "summary"))

    if title:
        parts.append(title)

    if abstract and abstract != title:
        parts.append(abstract)

    # Google Fact Check ranking output.
    claim_text = get_text(record, ("claim_text",))
    if claim_text and claim_text not in parts:
        parts.append("Fact-check claim: " + claim_text)

    reviews = record.get("claim_reviews")
    if not isinstance(reviews, list):
        reviews = record.get("claimReview")

    if isinstance(reviews, list):
        for review in reviews[:3]:
            if not isinstance(review, dict):
                continue

            review_title = get_text(review, ("title",))
            rating = get_text(
                review,
                ("textualRating", "textual_rating", "rating"),
            )
            review_text = get_text(
                review,
                ("text", "snippet", "description", "summary"),
            )

            publisher = review.get("publisher", {})
            publisher_name = (
                get_text(publisher, ("name",))
                if isinstance(publisher, dict)
                else ""
            )

            if review_title and review_title not in parts:
                parts.append("Review title: " + review_title)

            if rating:
                prefix = (
                    f"Fact-check rating from {publisher_name}: "
                    if publisher_name
                    else "Fact-check rating: "
                )
                parts.append(prefix + rating)

            if review_text:
                parts.append(review_text)

    # Support other common evidence schemas.
    if not parts:
        fallback = get_text(
            record,
            ("text", "snippet", "content", "description"),
        )
        if fallback:
            parts.append(fallback)

    # Some records retain their source data in original_record.
    if not parts:
        original = record.get("original_record")
        if isinstance(original, dict):
            parts.append(get_evidence_text(original))

    text = "\n".join(part for part in parts if part.strip())
    return text[:MAX_EVIDENCE_CHARS].strip()


# --------------------------------------------------
# NLI label helpers
# --------------------------------------------------

def normalize_label(label):
    """Convert recognized model labels to standard NLI classes."""
    label = str(label).strip().lower()

    if "contradiction" in label:
        return "contradiction"

    if "entailment" in label:
        return "entailment"

    if "neutral" in label:
        return "neutral"

    # Do not silently interpret unknown labels as NLI classes.
    return label


def get_label_names(model):
    """Read the NLI model's configured class labels."""
    try:
        config = model.model.config
        id2label = getattr(config, "id2label", {}) or {}

        labels = {}
        for index, label in id2label.items():
            try:
                labels[int(index)] = normalize_label(label)
            except (TypeError, ValueError):
                continue

        # Use the model's labels only if they identify the three
        # NLI classes unambiguously.
        required = {"contradiction", "neutral", "entailment"}
        if required.issubset(set(labels.values())):
            return labels

        print(
            "[WARNING] Model config labels were not recognizable "
            "as the three NLI classes."
        )

    except Exception as exc:
        print(f"[WARNING] Could not read model labels: {exc}")

    # Fallback for cross-encoder/nli-deberta-v3-base.
    return {
        0: "contradiction",
        1: "entailment",
        2: "neutral",
    }


# --------------------------------------------------
# Classification
# --------------------------------------------------

def classify_records(records, model, label_names, source_name, user_claim):
    """Classify evidence against the original user claim."""
    if not records:
        print(f"[INFO] No {source_name} records to classify.")
        return []

    records = records[:MAX_RECORDS_PER_SOURCE]
    output_by_index = {}
    claim_pairs = []
    valid_indices = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        claim = get_claim_text(record, user_claim)
        evidence = get_evidence_text(record)

        updated = dict(record)
        updated["user_claim"] = claim
        updated["nli_evidence_text"] = evidence

        if not claim or not evidence:
            updated["nli_label"] = "unavailable"
            updated["nli_confidence"] = None
            updated["nli_scores"] = {}
            updated["nli_error"] = (
                "Missing original user claim or usable evidence text."
            )
            output_by_index[index] = updated
            continue

        # NLI input order: premise = evidence, hypothesis = user claim.
        claim_pairs.append([evidence, claim])
        valid_indices.append(index)
        output_by_index[index] = updated

    print(
        f"[INFO] {source_name}: {len(claim_pairs)} usable evidence pairs "
        f"out of {len(records)} records."
    )

    for start in range(0, len(claim_pairs), BATCH_SIZE):
        batch_pairs = claim_pairs[start:start + BATCH_SIZE]

        predictions = model.predict(
            batch_pairs,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
            apply_softmax=True,
        )

        for offset, scores in enumerate(predictions):
            original_index = valid_indices[start + offset]
            score_values = [float(value) for value in scores]

            label_scores = {
                label_names.get(i, f"label_{i}"): score
                for i, score in enumerate(score_values)
            }

            if not score_values:
                output_by_index[original_index].update({
                    "nli_label": "unavailable",
                    "nli_confidence": None,
                    "nli_scores": {},
                })
                continue

            best_index = max(
                range(len(score_values)),
                key=lambda i: score_values[i],
            )
            predicted_label = label_names.get(
                best_index,
                f"label_{best_index}",
            )

            output_by_index[original_index].update({
                "nli_label": predicted_label,
                "nli_confidence": score_values[best_index],
                "nli_scores": label_scores,
            })

        del predictions
        del batch_pairs
        gc.collect()

    output = [
        output_by_index[index]
        for index in range(len(records))
        if index in output_by_index
    ]

    counts = {}
    for item in output:
        label = item.get("nli_label", "unavailable")
        counts[label] = counts.get(label, 0) + 1

    print(f"[INFO] Finished {source_name}: {len(output)} records.")
    print(f"[INFO] Label counts: {counts}")

    return output


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] Loading ranked evidence files...")

    factcheck_data = load_json(FACTCHECK_INPUT)
    article_data = load_json(ARTICLE_INPUT)

    factchecks = extract_records(factcheck_data, "Fact-check")
    articles = extract_records(article_data, "PubMed")

    factcheck_claim = extract_user_claim(factcheck_data)
    article_claim = extract_user_claim(article_data)

    # Both rankers should refer to the same user-submitted claim.
    if (
        factcheck_claim
        and article_claim
        and factcheck_claim.casefold() != article_claim.casefold()
    ):
        raise ValueError(
            "The fact-check and PubMed ranking files contain "
            "different user claims. Rerun the ranking pipeline."
        )

    user_claim = factcheck_claim or article_claim

    if not user_claim:
        raise ValueError(
            "The original user claim is missing from both ranking files. "
            "The NLI classifier cannot safely infer it from retrieved "
            "fact-checks or article titles."
        )

    print(f"[INFO] User claim: {user_claim}")
    print(f"[INFO] Fact-check records: {len(factchecks)}")
    print(f"[INFO] PubMed article records: {len(articles)}")

    if not factchecks and not articles:
        raise ValueError("No ranked evidence records were found.")

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
        "Fact-check",
        user_claim,
    )

    save_json(
        FACTCHECK_OUTPUT,
        {
            "user_claim": user_claim,
            "source": "Google Fact Check",
            "results": factcheck_results,
        },
    )
    print(f"[INFO] Saved: {FACTCHECK_OUTPUT}")

    # Release temporary memory before classifying PubMed evidence.
    gc.collect()

    article_results = classify_records(
        articles,
        model,
        label_names,
        "PubMed article",
        user_claim,
    )

    save_json(
        ARTICLE_OUTPUT,
        {
            "user_claim": user_claim,
            "source": "PubMed",
            "results": article_results,
        },
    )
    print(f"[INFO] Saved: {ARTICLE_OUTPUT}")

    print("[INFO] NLI classification completed.")


if __name__ == "__main__":
    main()
