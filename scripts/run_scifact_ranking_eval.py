"""
SciFact Document Ranking Evaluation.
Evaluates MedCPT Cross-Encoder document ranking quality on SciFact benchmark claims
where gold cited PubMed PMIDs are explicitly annotated.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import pandas as pd
import evaluate_ranking as er
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "ncbi/MedCPT-Cross-Encoder"

# Load SciFact claims from expanded dataset
df = pd.read_csv("evaluation_dataset_expanded.csv")
scifact_df = df[df["source_dataset"] == "SciFact (EMNLP 2020)"].copy()

print(f"Loaded {len(scifact_df)} SciFact benchmark claims for ranking evaluation.")

# Build synthetic candidate pools for each claim consisting of the gold abstract + distractor abstracts
# from other SciFact claims to form a 10-document candidate ranking pool per claim.
candidate_pool = []
for _, row in scifact_df.iterrows():
    candidate_pool.append({
        "pmid": str(row["gold_doc_id"]).strip(),
        "text": row["evidence"].strip(),
    })

print("Loading MedCPT Cross-Encoder...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

eval_queries = []

for idx, row in scifact_df.iterrows():
    claim = row["claim"].strip()
    gold_pmid = str(row["gold_doc_id"]).strip()

    # Score all candidate pool articles against this claim
    scores = []
    with torch.no_grad():
        for article in candidate_pool:
            inputs = tokenizer(
                claim,
                article["text"],
                return_tensors="pt",
                truncation=True,
                max_length=512,
            )
            score = model(**inputs).logits.reshape(-1)[0].item()
            scores.append((article["pmid"], score))

    # Rank descending by MedCPT score
    scores.sort(key=lambda x: x[1], reverse=True)
    ranked_pmids = [item[0] for item in scores]

    eval_queries.append({
        "query_id": row["example_id"],
        "claim": claim,
        "ranked_doc_ids": ranked_pmids,
        "gold_relevant_ids": [gold_pmid],
    })

results = er.evaluate_ranking_queries(eval_queries, k_values=[1, 3, 5, 10])
er.print_ranking_report(results, "MEDCPT RANKING EVALUATION ON SCIFACT BENCHMARK")
