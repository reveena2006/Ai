
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
MIN_CONFIDENCE = 0.45
MIN_MARGIN = 0.05


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


def get_study_weight(item, source_name):
    confidence = float(item.get("nli_confidence") or 1.0)
    title = (evidence_text(item) or "").lower()
    multiplier = 1.0
    if "systematic review" in title or "meta-analysis" in title:
        multiplier = 1.5
    elif "clinical trial" in title or "randomized" in title:
        multiplier = 1.3
    elif source_name == "Google Fact Check":
        multiplier = 1.2
    return round(confidence * multiplier, 4)


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

        weight = get_study_weight(item, source_name)
        accepted.append({
            "source": source_name,
            "title": evidence_text(item),
            "relationship": relationship,
            "confidence": item.get("nli_confidence"),
            "weight": weight,
            "scores": item.get("nli_scores", {}),
            "evidence_text": item.get("nli_evidence_text", ""),
        })

    return summary, accepted, rejected


def determine_verdict(evidence):
    """
    Determine the canonical health claim verdict from accepted evidence items.

    Uses a ratio/weighted consensus threshold:
    - Eliminates the 9-vs-1 consensus vulnerability by recognizing supermajority consensus.
    - Only declares 'Mixed evidence' when evidence is genuinely divided down the middle.
    - Prioritizes medical safety via the Contradiction-Precedent rule.
    - Accurately assigns all 4 canonical verdicts:
      1. 'Potentially refuted'
      2. 'Potentially supported'
      3. 'Mixed evidence'
      4. 'Insufficient evidence'
    """
    support_items = [
        item for item in evidence
        if item.get("relationship") == "support"
    ]
    contradiction_items = [
        item for item in evidence
        if item.get("relationship") == "contradiction"
    ]
    mixed_items = [
        item for item in evidence
        if item.get("relationship") in {"mixed", "conflicting"}
    ]

    support = len(support_items)
    contradiction = len(contradiction_items)
    total_active = support + contradiction

    # Calculate confidence weights
    weight_support = sum(float(item.get("weight") or item.get("confidence") or 1.0) for item in support_items)
    weight_contra = sum(float(item.get("weight") or item.get("confidence") or 1.0) for item in contradiction_items)
    total_weight = weight_support + weight_contra

    # 1. No active supporting or contradicting evidence (zero active or only neutral context)
    if total_active == 0:
        if len(mixed_items) >= 1:
            return (
                "Mixed evidence",
                "Retrieved evidence documents conflicting clinical outcomes. "
                "Scientists are actively divided on this health topic.",
            )
        return (
            "Insufficient evidence",
            "No evidence passed the configured rules for support or contradiction. "
            "Available studies provide only neutral background context or no published trials exist.",
        )

    # 2. Pure Contradiction (Unanimous Refutation)
    if contradiction >= 1 and support == 0:
        return (
            "Potentially refuted",
            f"Retrieved scientific evidence contradicts the claim ({contradiction} refuting source(s), "
            f"0 supporting). The claim is contradicted by available research.",
        )

    # 3. Pure Support (Unanimous Support)
    if support >= 1 and contradiction == 0:
        return (
            "Potentially supported",
            f"Retrieved scientific evidence supports the claim ({support} supporting source(s), "
            f"0 contradicting). Reputable research confirms this assertion.",
        )

    # 4. Both Support and Contradiction exist (support >= 1 and contradiction >= 1)
    # Calculate contradiction and support ratios
    ratio_contra = weight_contra / total_weight if total_weight > 0 else (contradiction / total_active)
    ratio_support = weight_support / total_weight if total_weight > 0 else (support / total_active)

    # 4a. Scientific Consensus to REFUTE (e.g., 9 vs 1, 8 vs 2, or >= 67% refutation)
    # Contradiction-Precedent Safety: A supermajority of refuting evidence takes priority.
    if ratio_contra >= 0.67 or (contradiction >= 2 * support and contradiction >= 2):
        return (
            "Potentially refuted",
            f"Strong scientific consensus contradicts the claim ({contradiction} refuting vs "
            f"{support} supporting source(s), refutation consensus ratio: {ratio_contra:.1%}). "
            f"Under the contradiction-precedent safety rule, overwhelming refuting evidence takes priority.",
        )

    # 4b. Scientific Consensus to SUPPORT (e.g., 9 vs 1, 8 vs 2, or >= 70% support)
    # Support requires clear supermajority with no substantial safety contradiction.
    if ratio_support >= 0.70 or (support >= 2.5 * contradiction and support >= 3):
        return (
            "Potentially supported",
            f"Strong scientific consensus supports the claim ({support} supporting vs "
            f"{contradiction} contradicting source(s), support consensus ratio: {ratio_support:.1%}).",
        )

    # 4c. Genuinely Divided Down the Middle (Mixed Evidence)
    # Neither side reaches a consensus supermajority (e.g. 5 vs 5, 4 vs 5, 3 vs 2, 2 vs 2, 1 vs 1)
    return (
        "Mixed evidence",
        f"Retrieved clinical evidence shows conflicting findings ({support} supporting vs "
        f"{contradiction} contradicting source(s), split: {ratio_support:.1%} support / {ratio_contra:.1%} refute). "
        f"Scientists and clinical trials are genuinely divided on this topic.",
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

    support_items = [x for x in accepted if x.get("relationship") == "support"]
    contra_items = [x for x in accepted if x.get("relationship") == "contradiction"]
    w_sup = sum(float(x.get("weight") or x.get("confidence") or 1.0) for x in support_items)
    w_con = sum(float(x.get("weight") or x.get("confidence") or 1.0) for x in contra_items)
    total_w = w_sup + w_con
    r_sup = round(w_sup / total_w, 4) if total_w > 0 else 0.0
    r_con = round(w_con / total_w, 4) if total_w > 0 else 0.0

    result = {
        "consensus_metrics": {
            "support_count": len(support_items),
            "contradiction_count": len(contra_items),
            "total_active_evidence": len(support_items) + len(contra_items),
            "support_weight": round(w_sup, 3),
            "contradiction_weight": round(w_con, 3),
            "support_ratio": r_sup,
            "contradiction_ratio": r_con,
            "consensus_threshold_met": bool(r_con >= 0.67 or r_sup >= 0.70),
        },
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
