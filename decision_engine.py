
import json
import re
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

FACTCHECK_FILE = OUTPUT_DIR / "nli_factchecks.json"
ARTICLE_FILE = OUTPUT_DIR / "nli_articles.json"
FINAL_FILE = OUTPUT_DIR / "final_verdict.json"

# Initial heuristic settings. Validate these using a labelled
# evaluation dataset before relying on the resulting verdicts.
MIN_CONFIDENCE = 0.70
MIN_MARGIN = 0.15


def load_json(path):
    if not path.exists():
        print(f"Missing file: {path}")
        return {}

    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def get_records(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if isinstance(data.get("results"), list):
            return data["results"]

    return []


def normalize_label(label):
    label = str(label or "").strip().lower()

    if label in {"entailment", "support", "supports", "supported"}:
        return "support"

    if label in {
        "contradiction", "contradicts", "refutes", "refutation"
    }:
        return "contradiction"

    if label in {"neutral", "unknown", "unrelated"}:
        return "neutral"

    return "unknown"


def get_confident_relationship(item):
    """Accept only a clear label with usable probability scores."""

    scores = item.get("nli_scores")

    if not isinstance(scores, dict):
        return None, "Missing probability scores"

    normalized_scores = {}

    for label, value in scores.items():
        relationship = normalize_label(label)

        try:
            probability = float(value)
        except (ValueError, TypeError):
            continue

        if relationship != "unknown":
            normalized_scores[relationship] = probability

    label = normalize_label(item.get("nli_label"))

    if label not in {"support", "contradiction", "neutral"}:
        return None, "Unrecognized label"

    if label not in normalized_scores:
        return None, "Predicted label missing from scores"

    probability = normalized_scores[label]
    other_scores = [
        score
        for other_label, score in normalized_scores.items()
        if other_label != label
    ]

    margin = probability - max(other_scores, default=0.0)

    if probability < MIN_CONFIDENCE:
        return None, "Below confidence threshold"

    if margin < MIN_MARGIN:
        return None, "Prediction margin too small"

    if label == "neutral":
        return "neutral", "Strong neutral prediction"

    return label, "Passed heuristic thresholds"


def evidence_text(item):
    return (
        item.get("title")
        or item.get("claim")
        or item.get("url")
        or item.get("pubmed_url")
        or item.get("pmid")
        or "Untitled evidence"
    )


def dedup_key(item):
    for key in ("pmid", "doi", "url", "pubmed_url"):
        value = item.get(key)

        if value:
            return f"{key}:{str(value).strip().lower()}"

    text = item.get("nli_evidence_text") or evidence_text(item)
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def process_source(items, source_name):
    summary = Counter()
    accepted = []
    rejected = []
    seen = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        key = dedup_key(item)

        if key in seen:
            continue

        seen.add(key)

        relationship, reason = get_confident_relationship(item)

        if relationship is None:
            rejected.append({
                "source": source_name,
                "title": evidence_text(item),
                "reason": reason,
                "nli_label": item.get("nli_label"),
                "nli_scores": item.get("nli_scores", {}),
            })
            continue

        summary[relationship] += 1

        accepted.append({
            "source": source_name,
            "title": evidence_text(item),
            "relationship": relationship,
            "confidence": item.get("nli_confidence"),
            "scores": item.get("nli_scores", {}),
            "evidence_text": item.get("nli_evidence_text", ""),
        })

    return summary, accepted, rejected


def determine_verdict(evidence):
    support = sum(
        item["relationship"] == "support"
        for item in evidence
    )

    contradiction = sum(
        item["relationship"] == "contradiction"
        for item in evidence
    )

    if support and contradiction:
        return (
            "Mixed evidence",
            "Some retrieved evidence supports the claim while "
            "other evidence contradicts it. Review the underlying "
            "sources and their context.",
        )

    if support:
        return (
            "Potentially supported",
            "Retrieved evidence text supports the claim according "
            "to the NLI model. This is not proof that the claim is true.",
        )

    if contradiction:
        return (
            "Potentially refuted",
            "Retrieved evidence text contradicts the claim according "
            "to the NLI model. This is not proof that the claim is false.",
        )

    return (
        "Insufficient evidence",
        "No evidence passed the configured rules for support or "
        "contradiction. The claim remains unresolved by this pipeline.",
    )


def main():
    print("=" * 55)
    print("HEALTH MISINFORMATION DECISION ENGINE")
    print("=" * 55)

    factcheck_data = load_json(FACTCHECK_FILE)
    article_data = load_json(ARTICLE_FILE)

    factchecks = get_records(factcheck_data)
    articles = get_records(article_data)

    claim = (
        factcheck_data.get("user_claim", "")
        if isinstance(factcheck_data, dict)
        else ""
    )

    if not claim and isinstance(article_data, dict):
        claim = article_data.get("user_claim", "")

    if not factchecks and not articles:
        print("No NLI records available. Run the NLI stage first.")
        return

    factcheck_summary, factcheck_evidence, rejected_fc = (
        process_source(factchecks, "Google Fact Check")
    )

    article_summary, article_evidence, rejected_articles = (
        process_source(articles, "PubMed")
    )

    accepted = factcheck_evidence + article_evidence
    rejected = rejected_fc + rejected_articles

    verdict, explanation = determine_verdict(accepted)

    result = {
        "user_claim": claim,
        "verdict": verdict,
        "explanation": explanation,
        "method": "Heuristic aggregation of NLI outputs",
        "thresholds": {
            "minimum_confidence": MIN_CONFIDENCE,
            "minimum_margin": MIN_MARGIN,
        },
        "summary": {
            "factcheck_records_received": len(factchecks),
            "article_records_received": len(articles),
            "accepted_evidence_count": len(accepted),
            "rejected_evidence_count": len(rejected),
            "support_count": sum(
                x["relationship"] == "support" for x in accepted
            ),
            "contradiction_count": sum(
                x["relationship"] == "contradiction" for x in accepted
            ),
            "neutral_count": sum(
                x["relationship"] == "neutral" for x in accepted
            ),
        },
        "source_breakdown": {
            "factchecks": dict(factcheck_summary),
            "pubmed_articles": dict(article_summary),
        },
        "accepted_evidence": accepted,
        "rejected_evidence": rejected,
        "limitations": [
            "NLI scores are not probabilities that a medical claim is true.",
            "Relevance ranking does not establish source quality or correctness.",
            "Duplicate or dependent studies can make evidence appear stronger.",
            "Thresholds are heuristic and require evaluation on verified claims.",
            "This verdict is preliminary and requires review of the cited evidence.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with FINAL_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"\nClaim: {claim}")
    print(f"Verdict: {verdict}")
    print(f"Explanation: {explanation}")
    print(f"Accepted evidence: {len(accepted)}")
    print(f"Rejected evidence: {len(rejected)}")
    print(f"\nSaved to: {FINAL_FILE}")


if __name__ == "__main__":
    main()
