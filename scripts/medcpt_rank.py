
import json
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

INPUT_FILE = Path("input/pubmed_candidates.json")
OUTPUT_FILE = Path("output/ranked_articles.json")
MODEL_NAME = "ncbi/MedCPT-Cross-Encoder"


def main():
    with INPUT_FILE.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    claim = data["user_claim"]
    articles = data["articles"]

    print(f"Claim: {claim}")
    print(f"Articles received: {len(articles)}")
    print("Loading MedCPT model...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME
    )
    model.eval()

    ranked_articles = []

    for i, article in enumerate(articles, start=1):
        title = article.get("title", "")
        abstract = article.get("abstract", "")
        text = f"{title}. {abstract}".strip()

        inputs = tokenizer(
            claim,
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = model(**inputs)
            score = outputs.logits.reshape(-1)[0].item()

        result = dict(article)
        result["medcpt_score"] = score
        ranked_articles.append(result)

        if i % 10 == 0 or i == len(articles):
            print(f"Scored {i}/{len(articles)} articles")

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
