"""
Comprehensive IR Ranking Benchmark for SBERT and MedCPT.

Evaluates:
- Sentence-BERT (sentence-transformers/all-MiniLM-L6-v2) Bi-Encoder
- MedCPT (ncbi/MedCPT-Cross-Encoder) Cross-Encoder
- Lexical Baseline (BM25 / Jaccard Token Overlap)

On:
- 70 real claims with 10-candidate pools (1 gold relevant evidence + 9 distractors)
- TREC-standard Information Retrieval metrics:
  * MRR (Mean Reciprocal Rank)
  * Precision@K (P@1, P@3, P@5, P@10)
  * Recall@K (R@1, R@3, R@5, R@10)
  * NDCG@K (NDCG@1, NDCG@3, NDCG@5, NDCG@10)
  * Inference Latency (ms / query)
"""

import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch

# Offline transformers / huggingface
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import evaluate_ranking as er

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "evaluation_dataset_expanded.csv"


def jaccard_overlap(query: str, doc: str) -> float:
    """Simple lexical token overlap baseline (Jaccard similarity)."""
    q_tokens = set(query.lower().split())
    d_tokens = set(doc.lower().split())
    if not q_tokens or not d_tokens:
        return 0.0
    return len(q_tokens & d_tokens) / float(len(q_tokens | d_tokens))


def run_benchmark():
    if not DATASET_PATH.exists():
        print(f"Dataset not found at {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)
    num_samples = len(df)
    print("=" * 70)
    print(f"RANKING EVALUATION BENCHMARK: SBERT vs MedCPT vs Lexical Baseline")
    print(f"Dataset: {DATASET_PATH.name} ({num_samples} clinical claims)")
    print("Candidate Pool Size: 10 per query (1 Ground-Truth Evidence + 9 Distractors)")
    print("=" * 70)

    claims = df["claim"].tolist()
    evidences = df["evidence"].tolist()
    doc_ids = df["gold_doc_id"].astype(str).tolist()

    # Pre-generate deterministic pools so all models evaluate on identical pools
    np.random.seed(42)
    pools = []
    for i in range(num_samples):
        gold_id = doc_ids[i]
        gold_ev = evidences[i]

        distractor_indices = [j for j in range(num_samples) if j != i]
        selected_distractors = np.random.choice(distractor_indices, size=9, replace=False)

        pool_items = [(gold_id, gold_ev)] + [(doc_ids[d], evidences[d]) for d in selected_distractors]
        np.random.shuffle(pool_items)
        pools.append({
            "gold_id": gold_id,
            "items": pool_items
        })

    # -------------------------------------------------------------
    # 1. Baseline: Lexical Overlap (Jaccard)
    # -------------------------------------------------------------
    print("\n[1/3] Evaluating Lexical Overlap Baseline...")
    lex_queries = []
    t0 = time.time()
    for i, pool in enumerate(pools):
        claim = claims[i]
        gold_id = pool["gold_id"]
        pool_items = pool["items"]

        scores = [jaccard_overlap(claim, item[1]) for item in pool_items]
        ranked_indices = np.argsort(scores)[::-1]
        ranked_ids = [pool_items[idx][0] for idx in ranked_indices]

        lex_queries.append({
            "query_id": f"Q_{i}",
            "ranked_doc_ids": ranked_ids,
            "gold_relevant_ids": [gold_id]
        })
    lex_time = time.time() - t0
    lex_res = er.evaluate_ranking_queries(lex_queries, k_values=[1, 3, 5, 10])

    # -------------------------------------------------------------
    # 2. SBERT Bi-Encoder (all-MiniLM-L6-v2)
    # -------------------------------------------------------------
    print("\n[2/3] Evaluating Sentence-BERT Bi-Encoder (sentence-transformers/all-MiniLM-L6-v2)...")
    sbert = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

    sbert_queries = []
    t0 = time.time()
    for i, pool in enumerate(pools):
        claim = claims[i]
        gold_id = pool["gold_id"]
        pool_items = pool["items"]
        pool_texts = [item[1] for item in pool_items]

        q_emb = sbert.encode(claim, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        d_embs = sbert.encode(pool_texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        scores = np.dot(d_embs, q_emb)

        ranked_indices = np.argsort(scores)[::-1]
        ranked_ids = [pool_items[idx][0] for idx in ranked_indices]

        sbert_queries.append({
            "query_id": f"Q_{i}",
            "ranked_doc_ids": ranked_ids,
            "gold_relevant_ids": [gold_id]
        })
    sbert_time = time.time() - t0
    sbert_res = er.evaluate_ranking_queries(sbert_queries, k_values=[1, 3, 5, 10])

    # -------------------------------------------------------------
    # 3. MedCPT Cross-Encoder (ncbi/MedCPT-Cross-Encoder)
    # -------------------------------------------------------------
    print("\n[3/3] Evaluating MedCPT Cross-Encoder (ncbi/MedCPT-Cross-Encoder)...")
    medcpt_model_name = "ncbi/MedCPT-Cross-Encoder"
    medcpt_tok = AutoTokenizer.from_pretrained(medcpt_model_name, local_files_only=True)
    medcpt_mod = AutoModelForSequenceClassification.from_pretrained(medcpt_model_name, local_files_only=True)
    medcpt_mod.eval()

    medcpt_queries = []
    t0 = time.time()
    batch_size = 16

    for i, pool in enumerate(pools):
        claim = claims[i]
        gold_id = pool["gold_id"]
        pool_items = pool["items"]

        pairs = [(claim, item[1]) for item in pool_items]
        inputs = medcpt_tok(
            pairs,
            padding=True,
            truncation=True,
            max_length=384,
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = medcpt_mod(**inputs)
            scores = outputs.logits.reshape(-1).tolist()

        ranked_indices = np.argsort(scores)[::-1]
        ranked_ids = [pool_items[idx][0] for idx in ranked_indices]

        medcpt_queries.append({
            "query_id": f"Q_{i}",
            "ranked_doc_ids": ranked_ids,
            "gold_relevant_ids": [gold_id]
        })

        if (i + 1) % 20 == 0 or (i + 1) == num_samples:
            print(f"  Processed {i + 1}/{num_samples} queries with MedCPT...")

    medcpt_time = time.time() - t0
    medcpt_res = er.evaluate_ranking_queries(medcpt_queries, k_values=[1, 3, 5, 10])

    # -------------------------------------------------------------
    # Summary Comparison Table
    # -------------------------------------------------------------
    print("\n" + "=" * 78)
    print("EXPERIMENTAL EVALUATION SUMMARY: SBERT vs MedCPT vs Lexical Baseline")
    print("=" * 78)

    models_data = [
        {
            "Model": "Lexical Baseline (Jaccard)",
            "Architecture": "Token Overlap",
            "MRR": f"{lex_res['mrr']:.4f}",
            "P@1 (Acc)": f"{lex_res['precision_at_k']['P@1']*100:.1f}%",
            "P@3": f"{lex_res['precision_at_k']['P@3']*100:.1f}%",
            "R@1": f"{lex_res['recall_at_k']['R@1']*100:.1f}%",
            "R@3": f"{lex_res['recall_at_k']['R@3']*100:.1f}%",
            "R@5": f"{lex_res['recall_at_k']['R@5']*100:.1f}%",
            "NDCG@5": f"{lex_res['ndcg_at_k']['NDCG@5']:.4f}",
            "Latency (ms)": f"{lex_time / num_samples * 1000:.1f} ms"
        },
        {
            "Model": "SBERT (all-MiniLM-L6-v2)",
            "Architecture": "Bi-Encoder (Dense)",
            "MRR": f"{sbert_res['mrr']:.4f}",
            "P@1 (Acc)": f"{sbert_res['precision_at_k']['P@1']*100:.1f}%",
            "P@3": f"{sbert_res['precision_at_k']['P@3']*100:.1f}%",
            "R@1": f"{sbert_res['recall_at_k']['R@1']*100:.1f}%",
            "R@3": f"{sbert_res['recall_at_k']['R@3']*100:.1f}%",
            "R@5": f"{sbert_res['recall_at_k']['R@5']*100:.1f}%",
            "NDCG@5": f"{sbert_res['ndcg_at_k']['NDCG@5']:.4f}",
            "Latency (ms)": f"{sbert_time / num_samples * 1000:.1f} ms"
        },
        {
            "Model": "MedCPT (ncbi/MedCPT-Cross-Encoder)",
            "Architecture": "Cross-Encoder (Domain)",
            "MRR": f"{medcpt_res['mrr']:.4f}",
            "P@1 (Acc)": f"{medcpt_res['precision_at_k']['P@1']*100:.1f}%",
            "P@3": f"{medcpt_res['precision_at_k']['P@3']*100:.1f}%",
            "R@1": f"{medcpt_res['recall_at_k']['R@1']*100:.1f}%",
            "R@3": f"{medcpt_res['recall_at_k']['R@3']*100:.1f}%",
            "R@5": f"{medcpt_res['recall_at_k']['R@5']*100:.1f}%",
            "NDCG@5": f"{medcpt_res['ndcg_at_k']['NDCG@5']:.4f}",
            "Latency (ms)": f"{medcpt_time / num_samples * 1000:.1f} ms"
        }
    ]

    summary_df = pd.DataFrame(models_data)
    print(summary_df.to_string(index=False))
    print("=" * 78)

    # Save results to output
    out_dir = BASE_DIR / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(out_dir / "ranker_benchmark_results.csv", index=False)
    print(f"\nSaved benchmark results to {out_dir / 'ranker_benchmark_results.csv'}")

    return {
        "lexical": lex_res,
        "sbert": sbert_res,
        "medcpt": medcpt_res
    }


if __name__ == "__main__":
    run_benchmark()
