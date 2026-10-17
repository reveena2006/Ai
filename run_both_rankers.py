import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests
from sbert_ranker import rank_factchecks
from pubmed_retriever import run_pubmed_retrieval

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

FACTCHECK_FILE = BASE_DIR / "factcheck_results.json"
SBERT_OUTPUT_FILE = BASE_DIR / "ranked_factchecks.json"
TOP10_SBERT_FILE = BASE_DIR / "top10_ranked_factchecks.json"
PUBMED_FILE = BASE_DIR / "pubmed_candidates.json"

MEDCPT_INPUT_FILE = BASE_DIR / "input" / "pubmed_candidates.json"
MEDCPT_SCRIPT = BASE_DIR / "scripts" / "medcpt_rank.py"
MEDCPT_OUTPUT_FILE = OUTPUT_DIR / "ranked_articles.json"
TOP10_MEDCPT_FILE = OUTPUT_DIR / "top10_ranked_articles.json"

NLI_SCRIPT = BASE_DIR / "nli_classifier.py"
NLI_FACTCHECK_OUTPUT = OUTPUT_DIR / "nli_factchecks.json"
NLI_ARTICLE_OUTPUT = OUTPUT_DIR / "nli_articles.json"
DECISION_ENGINE_SCRIPT = BASE_DIR / "decision_engine.py"
FINAL_VERDICT_FILE = OUTPUT_DIR / "final_verdict.json"

GOOGLE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
TOP_N = 10
MIN_GOOGLE_RESULTS = 3
MIN_PUBMED_RESULTS = 5
REQUEST_TIMEOUT = 30


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def records(data, *keys):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            if isinstance(data.get(key), list):
                return data[key]
    return []


def norm(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def item_key(item, source):
    if not isinstance(item, dict):
        return "text:" + norm(item)

    fields = (
        ("pmid", "PMID", "doi", "DOI", "pubmed_url")
        if source == "article"
        else ("url", "source_url", "doi", "DOI")
    )
    for field in fields:
        if item.get(field):
            return field + ":" + norm(item[field])

    if source == "factcheck":
        reviews = item.get("claimReview", [])
        if isinstance(reviews, dict):
            reviews = [reviews]
        for review in reviews:
            if isinstance(review, dict) and review.get("url"):
                return "url:" + norm(review["url"])

    text = item.get("title") or item.get("text") or item.get("claim") or item.get("abstract") or ""
    return "text:" + norm(text)


def merge(existing, new, source):
    result, seen = [], set()
    for item in list(existing or []) + list(new or []):
        key = item_key(item, source)
        if key == "text:":
            result.append(item)
        elif key not in seen:
            seen.add(key)
            result.append(item)
    return result


def make_queries(claim):
    claim = re.sub(r"\s+", " ", claim).strip()
    if not claim:
        return []
    queries = [claim]
    simplified = re.sub(
        r"^(is|are|does|do|can|could|will|should|what|why|how)\s+",
        "", claim, flags=re.IGNORECASE
    ).strip(" ?.")
    if simplified and simplified.lower() != claim.lower():
        queries.append(simplified)

    stop = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "being", "does", "do", "did", "can", "could", "will", "would",
        "should", "of", "to", "for", "and", "or", "in", "on", "with",
        "about", "it", "this", "that", "generally", "people", "person",
        "cause", "causes", "causing"
    }
    words = re.findall(r"[A-Za-z0-9-]+", simplified)
    keywords = [w for w in words if w.lower() not in stop and len(w) > 2]
    if keywords:
        keyword_query = " ".join(keywords[:8])
        if keyword_query.lower() not in {q.lower() for q in queries}:
            queries.append(keyword_query)

    unique, seen = [], set()
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)
    return unique[:3]


def google_search(query):
    api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
    if not api_key:
        print("  Warning: GOOGLE_FACT_CHECK_API_KEY is not configured.")
        return []
    try:
        response = requests.get(
            GOOGLE_URL,
            params={
                "query": query,
                "languageCode": "en",
                "pageSize": 100,
                "key": api_key,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("claims", []) if isinstance(data.get("claims", []), list) else []
    except (requests.RequestException, ValueError) as exc:
        print(f"  Google search failed for {query!r}: {exc}")
        return []


def retrieve_factchecks(claim, expanded=False):
    queries = make_queries(claim) if expanded else [claim]
    found = []
    for query in queries:
        print(f"  Google Fact Check query: {query}")
        found.extend(google_search(query))
        time.sleep(0.15)
    return merge([], found, "factcheck")


def pubmed_one_query(query):
    # Existing retriever writes to pubmed_candidates.json, so read it
    # immediately before another query overwrites that file.
    try:
        run_pubmed_retrieval(query)
        data = load_json(PUBMED_FILE, {})
        return records(data, "articles", "results", "records", "items")
    except Exception as exc:
        print(f"  PubMed retrieval failed for {query!r}: {exc}")
        return []


def retrieve_pubmed(claim, expanded=False):
    queries = make_queries(claim) if expanded else [claim]
    articles = []
    for query in queries:
        print(f"  PubMed query: {query}")
        current = pubmed_one_query(query)
        print(f"  Records from this query: {len(current)}")
        articles = merge(articles, current, "article")
        time.sleep(0.2)

    save_json(PUBMED_FILE, {
        "user_claim": claim,
        "source": "PubMed",
        "retrieval_method": "Expanded queries with deduplication" if expanded else "Initial query",
        "articles_fetched": len(articles),
        "articles": articles,
    })
    return articles


def save_top10(source_file, output_file, key, ranker, claim):
    data = load_json(source_file, {})
    ranked = data if isinstance(data, list) else records(data, key)
    save_json(output_file, {
        "user_claim": claim,
        "ranker": ranker,
        "source_file": Path(source_file).name,
        "total_ranked_items": len(ranked),
        "top_n": min(TOP_N, len(ranked)),
        "results": ranked[:TOP_N],
    })


def run_sbert(claim, factchecks):
    print("\nRanking Google fact-checks with SBERT...")
    try:
        ranked = rank_factchecks(claim, factchecks) if factchecks else []
        save_json(SBERT_OUTPUT_FILE, {
            "user_claim": claim,
            "source": "Google Fact Check API",
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "ranking_method": "SBERT cosine similarity",
            "total_input_records": len(factchecks),
            "ranked_records": len(ranked),
            "results": ranked,
        })
        save_top10(SBERT_OUTPUT_FILE, TOP10_SBERT_FILE, "results", "SBERT", claim)
        print(f"  SBERT ranked {len(ranked)} records.")
        return True
    except Exception as exc:
        print(f"  SBERT failed: {exc}")
        save_json(TOP10_SBERT_FILE, {"user_claim": claim, "results": [], "top_n": 0})
        return False


def run_medcpt(claim, articles):
    print("\nRanking PubMed articles with MedCPT...")
    if not articles:
        print("  No PubMed articles to rank.")
        save_json(TOP10_MEDCPT_FILE, {"user_claim": claim, "results": [], "top_n": 0})
        return False
    if not MEDCPT_SCRIPT.exists():
        print(f"  Missing script: {MEDCPT_SCRIPT}")
        return False

    save_json(PUBMED_FILE, {
        "user_claim": claim,
        "source": "PubMed",
        "articles_fetched": len(articles),
        "articles": articles,
    })
    MEDCPT_INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PUBMED_FILE, MEDCPT_INPUT_FILE)

    try:
        if MEDCPT_OUTPUT_FILE.exists():
            MEDCPT_OUTPUT_FILE.unlink()
        subprocess.run(
            [sys.executable, str(MEDCPT_SCRIPT)],
            cwd=str(BASE_DIR), check=True
        )
        data = load_json(MEDCPT_OUTPUT_FILE)
        ranked = data if isinstance(data, list) else records(
            data, "ranked_articles", "results", "articles", "ranked_records"
        )
        save_json(TOP10_MEDCPT_FILE, {
            "user_claim": claim,
            "ranker": "MedCPT",
            "total_ranked_items": len(ranked),
            "top_n": min(TOP_N, len(ranked)),
            "results": ranked[:TOP_N],
        })
        print(f"  MedCPT ranked {len(ranked)} records.")
        return True
    except Exception as exc:
        print(f"  MedCPT failed: {exc}")
        return False


def run_nli(claim):
    print("\nRunning NLI...")
    for path in (TOP10_SBERT_FILE, TOP10_MEDCPT_FILE):
        data = load_json(path, {})
        if not isinstance(data, dict) or data.get("user_claim") != claim:
            print(f"  NLI stopped: {path.name} is missing or belongs to another claim.")
            return False

    for path in (NLI_FACTCHECK_OUTPUT, NLI_ARTICLE_OUTPUT):
        if path.exists():
            path.unlink()

    result = subprocess.run(
        [sys.executable, str(NLI_SCRIPT)],
        cwd=str(BASE_DIR), capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("  NLI failed:")
        print((result.stderr or result.stdout or "No error details.")[-3000:])
        return False
    if not NLI_FACTCHECK_OUTPUT.exists() or not NLI_ARTICLE_OUTPUT.exists():
        print("  NLI did not create both output files.")
        return False
    print("  NLI completed.")
    return True


def all_usable_nli_neutral():
    items = []
    for path in (NLI_FACTCHECK_OUTPUT, NLI_ARTICLE_OUTPUT):
        try:
            data = load_json(path, {})
        except (OSError, json.JSONDecodeError):
            continue
        items.extend(records(data, "results"))

    labels = [
        norm(item.get("nli_label"))
        for item in items
        if isinstance(item, dict)
        and item.get("nli_label")
        and norm(item.get("nli_label")) != "insufficient_text"
    ]
    return bool(labels) and all(label == "neutral" for label in labels)


def run_decision_engine():
    """Run decision_engine.py automatically after NLI completes."""
    print("\nRunning decision engine...")

    if not DECISION_ENGINE_SCRIPT.exists():
        print(f"  ERROR: Missing decision engine: {DECISION_ENGINE_SCRIPT}")
        print("  Save decision_engine.py beside run_both_rankers_updated.py.")
        return False

    # Remove any old verdict so an earlier run cannot look like a new result.
    if FINAL_VERDICT_FILE.exists():
        FINAL_VERDICT_FILE.unlink()

    result = subprocess.run(
        [sys.executable, str(DECISION_ENGINE_SCRIPT)],
        cwd=str(BASE_DIR), capture_output=True, text=True, check=False
    )

    if result.stdout:
        print(result.stdout.strip())

    if result.returncode != 0:
        print("  Decision engine failed:")
        print((result.stderr or "No error details.")[-3000:])
        return False

    if not FINAL_VERDICT_FILE.exists():
        print("  ERROR: Decision engine finished but did not create final_verdict.json.")
        if result.stderr:
            print(result.stderr[-3000:])
        return False

    try:
        verdict_data = load_json(FINAL_VERDICT_FILE, {})
        print(f"  Final verdict: {verdict_data.get('verdict', 'Verdict field not found')}")
        print(f"  Saved to: {FINAL_VERDICT_FILE}")
    except Exception as exc:
        print(f"  Verdict file was created but could not be read: {exc}")
        return False

    return True


def main():
    print("=" * 60)
    print(" HEALTH MISINFORMATION VERIFICATION SYSTEM")
    print("=" * 60)
    claim = input("\nEnter a health claim to verify: ").strip()
    if not claim:
        print("No claim entered. Exiting.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (
        TOP10_SBERT_FILE, TOP10_MEDCPT_FILE,
        NLI_FACTCHECK_OUTPUT, NLI_ARTICLE_OUTPUT, FINAL_VERDICT_FILE
    ):
        if path.exists():
            path.unlink()

    print("\n[1] Initial retrieval...")
    factchecks = retrieve_factchecks(claim, expanded=False)
    articles = retrieve_pubmed(claim, expanded=False)
    print(f"Initial Google records: {len(factchecks)}")
    print(f"Initial PubMed records: {len(articles)}")

    if len(factchecks) < MIN_GOOGLE_RESULTS or len(articles) < MIN_PUBMED_RESULTS:
        print("\nOne or both sources returned few records. Expanding searches...")
        factchecks = merge(
            factchecks, retrieve_factchecks(claim, expanded=True), "factcheck"
        )
        articles = merge(
            articles, retrieve_pubmed(claim, expanded=True), "article"
        )

    save_json(FACTCHECK_FILE, {
        "user_claim": claim,
        "source": "Google Fact Check API",
        "total_records": len(factchecks),
        "claims": factchecks,
    })
    save_json(PUBMED_FILE, {
        "user_claim": claim,
        "source": "PubMed",
        "articles_fetched": len(articles),
        "articles": articles,
    })

    print(f"\nMerged fact-check records: {len(factchecks)}")
    print(f"Merged PubMed records: {len(articles)}")
    run_sbert(claim, factchecks)
    run_medcpt(claim, articles)

    if not run_nli(claim):
        print("Pipeline stopped because NLI did not complete.")
        return

    # A single optional retry if every usable NLI label is neutral.
    if all_usable_nli_neutral():
        print("\nAll usable NLI labels are neutral; performing one expanded retry.")
        factchecks = merge(
            factchecks, retrieve_factchecks(claim, expanded=True), "factcheck"
        )
        articles = merge(
            articles, retrieve_pubmed(claim, expanded=True), "article"
        )
        save_json(FACTCHECK_FILE, {
            "user_claim": claim,
            "source": "Google Fact Check API",
            "total_records": len(factchecks),
            "claims": factchecks,
        })
        save_json(PUBMED_FILE, {
            "user_claim": claim,
            "source": "PubMed",
            "articles_fetched": len(articles),
            "articles": articles,
        })
        run_sbert(claim, factchecks)
        run_medcpt(claim, articles)
        if not run_nli(claim):
            print("Second NLI pass failed. No fresh final verdict will be produced.")
            return

    # Automatically call decision_engine.py after the NLI stage.
    verdict_ok = run_decision_engine()
    if verdict_ok:
        print("\nPipeline finished successfully, including the final decision step.")
    else:
        print("\nPipeline finished, but the final verdict step needs attention.")
        print("Check the message above and confirm decision_engine.py is in the project folder.")


if __name__ == "__main__":
    main()
