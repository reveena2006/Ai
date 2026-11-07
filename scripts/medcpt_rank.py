import json
import os
from pathlib import Path

# Prefer local cached models to avoid network stalls
if os.environ.get("HF_HUB_OFFLINE") is None:
    os.environ["HF_HUB_OFFLINE"] = "1"
if os.environ.get("TRANSFORMERS_OFFLINE") is None:
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

INPUT_FILE = Path("input/pubmed_candidates.json")
OUTPUT_FILE = Path("output/ranked_articles.json")
MODEL_NAME = "ncbi/MedCPT-Cross-Encoder"
BATCH_SIZE = 8
MAX_LENGTH = 384


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with INPUT_FILE.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    claim = data.get("user_claim", "").strip()
    articles = data.get("articles", [])

    print(f"Claim: {claim}")
    print(f"Articles received: {len(articles)}")

    if not articles:
        print("No articles to rank.")
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump({"user_claim": claim, "ranking_method": "MedCPT Cross-Encoder", "articles_ranked": 0, "articles": []}, f)
        return

    print("Loading MedCPT model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, local_files_only=True)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

    model.eval()

    ranked_articles = []
    # Rank candidates in efficient batches
    pairs = []
    valid_articles = []
    for article in articles:
        title = article.get("title", "")
        abstract = article.get("abstract", "")
        text = f"{title}. {abstract}".strip()
        if text:
            pairs.append((claim, text))
            valid_articles.append(article)

    print(f"Scoring {len(pairs)} candidate articles with MedCPT (batch size = {BATCH_SIZE})...")

    scores = []
    for i in range(0, len(pairs), BATCH_SIZE):
        batch_pairs = pairs[i:i + BATCH_SIZE]
        inputs = tokenizer(
            batch_pairs,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = model(**inputs)
            batch_scores = outputs.logits.reshape(-1).tolist()
            if isinstance(batch_scores, float):
                batch_scores = [batch_scores]
            scores.extend(batch_scores)

        scored_count = min(i + BATCH_SIZE, len(pairs))
        if scored_count % 16 == 0 or scored_count == len(pairs):
            print(f"  Scored {scored_count}/{len(pairs)} articles")

    for article, score in zip(valid_articles, scores):
        res = dict(article)
        res["medcpt_score"] = float(score)
        ranked_articles.append(res)

    ranked_articles.sort(
        key=lambda item: item["medcpt_score"],
        reverse=True,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    result_data = {
        "user_claim": claim,
        "ranking_method": "MedCPT Cross-Encoder",
        "articles_ranked": len(ranked_articles),
        "articles": ranked_articles,
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            result_data,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\nRanking completed!")
    print("\nTop 5 relevant articles:")
    for rank, article in enumerate(ranked_articles[:5], 1):
        print(f"\n{rank}. {article.get('title', 'No title')}")
        print(f"   PMID: {article.get('pmid', 'N/A')}")
        print(f"   MedCPT score: {article['medcpt_score']:.4f}")

    print(f"\nFull results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
