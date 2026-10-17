
import os
import json
import requests
import contextlib
import io

from sbert_ranker import rank_factchecks
from pubmed_retriever import run_pubmed_retrieval

GOOGLE_FACT_CHECK_URL = (
    "https://factchecktools.googleapis.com/v1alpha1/claims:search"
)

FACTCHECK_FILE = "factcheck_results.json"
SBERT_OUTPUT_FILE = "ranked_factchecks.json"


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def retrieve_factchecks(user_claim):
    api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")

    if not api_key:
        print("  Google Fact Check API key missing.")
        return []

    queries = [user_claim]

    # Add a shorter keyword query.
    import re

    stop_words = {
        "a", "an", "the", "is", "are", "was", "were",
        "do", "does", "did", "can", "could", "should",
        "would", "will", "may", "might", "in", "on", "at",
        "to", "for", "of", "with", "by", "from", "and",
        "or", "but", "if", "every", "each", "all", "any",
        "person", "people", "it", "this", "that", "have",
        "has", "had", "directly", "indirectly", "consuming",
        "consume", "consumed", "causes", "cause", "causing",
        "caused", "grow", "growth", "growing"
    }

    words = re.findall(r"\b[a-zA-Z]+\b", user_claim.lower())
    keywords = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    if keywords:
        queries.append(" ".join(keywords))

    core_terms = [
        word for word in keywords
        if word not in {
            "increase", "increases", "increased",
            "increasing", "affect", "affects"
        }
    ]

    if len(core_terms) >= 2:
        queries.append(" ".join(core_terms))

    queries = list(dict.fromkeys(queries))

    all_records = []
    seen = set()

    for query in queries:
        try:
            response = requests.get(
                GOOGLE_FACT_CHECK_URL,
                params={
                    "query": query,
                    "key": api_key,
                    "pageSize": 100
                },
                timeout=30
            )
            response.raise_for_status()

            for record in response.json().get("claims", []):
                key = (
                    record.get("text", "").strip().lower(),
                    tuple(sorted(
                        review.get("url", "")
                        for review in record.get("claimReview", [])
                    ))
                )

                if key not in seen:
                    seen.add(key)
                    all_records.append(record)

        except (requests.RequestException, ValueError):
            continue

    return all_records


def main():
    print("=" * 50)
    print(" HEALTH MISINFORMATION VERIFICATION SYSTEM")
    print("=" * 50)

    user_claim = input("Enter a health claim to verify: ").strip()

    if not user_claim:
        print("No claim entered. Exiting.")
        return

    print("\n[1/4] Retrieving fact-check records...")
    factchecks = retrieve_factchecks(user_claim)

    save_json(FACTCHECK_FILE, {
        "user_claim": user_claim,
        "source": "Google Fact Check API",
        "total_records": len(factchecks),
        "claims": factchecks
    })

    print(f"      Fact-check records retrieved: {len(factchecks)}")

    print("\n[2/4] Ranking fact-check records with SBERT...")

    try:
        # Hide model loading and progress-bar output.
        with contextlib.redirect_stdout(io.StringIO()):
            ranked = rank_factchecks(user_claim, factchecks)

        save_json(SBERT_OUTPUT_FILE, {
            "user_claim": user_claim,
            "source": "Google Fact Check API",
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "ranking_method": "SBERT cosine similarity",
            "total_input_records": len(factchecks),
            "ranked_records": len(ranked),
            "results": ranked
        })

        print(f"      Records ranked: {len(ranked)}")

    except Exception as error:
        print(f"      SBERT ranking failed: {error}")

    print("\n[3/4] Retrieving research articles from PubMed...")

    try:
        # Hide internal PubMed query and retrieval logs.
        with contextlib.redirect_stdout(io.StringIO()):
            run_pubmed_retrieval(user_claim)

        with open("pubmed_candidates.json", "r", encoding="utf-8") as file:
            pubmed_data = json.load(file)

        print(
            "      Unique candidate PMIDs: "
            f"{pubmed_data.get('unique_candidate_pmids', 0)}"
        )
        print(
            "      Articles fetched: "
            f"{pubmed_data.get('articles_fetched', 0)}"
        )

        if pubmed_data.get("error"):
            print("      PubMed reported an error; check the JSON output.")

    except Exception as error:
        print(f"      PubMed retrieval failed: {error}")

    print("\n[4/4] Saving results...")
    print("      factcheck_results.json")
    print("      ranked_factchecks.json")
    print("      pubmed_candidates.json")

    print("\n" + "=" * 50)
    print(" PROCESS FINISHED")
    print("=" * 50)


if __name__ == "__main__":
    main()
