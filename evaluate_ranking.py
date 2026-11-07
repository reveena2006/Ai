"""
Information Retrieval (IR) Ranking Evaluation Module.

Calculates standard document-level ranking metrics:
- Precision@K (K=1, 3, 5, 10)
- Recall@K (K=1, 3, 5, 10)
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG@K)

Evaluates document ranking quality separately from claim classification verdicts,
as required by scientific evaluation methodologies (TREC / BioASQ / MTEB).
"""

import math
from typing import List, Dict, Any, Set
import numpy as np
import pandas as pd


def precision_at_k(ranked_ids: List[str], gold_relevant_ids: Set[str], k: int) -> float:
    """Calculate Precision at rank cut-off K."""
    if k <= 0 or not ranked_ids or not gold_relevant_ids:
        return 0.0
    gold_set = {str(d).strip().lower() for d in gold_relevant_ids}
    cutoff = ranked_ids[:k]
    hits = sum(1 for doc_id in cutoff if str(doc_id).strip().lower() in gold_set)
    return hits / float(k)


def recall_at_k(ranked_ids: List[str], gold_relevant_ids: Set[str], k: int) -> float:
    """Calculate Recall at rank cut-off K."""
    if not gold_relevant_ids or not ranked_ids or k <= 0:
        return 0.0
    gold_set = {str(d).strip().lower() for d in gold_relevant_ids}
    cutoff = ranked_ids[:k]
    hits = sum(1 for doc_id in cutoff if str(doc_id).strip().lower() in gold_set)
    return hits / float(len(gold_set))


def reciprocal_rank(ranked_ids: List[str], gold_relevant_ids: Set[str]) -> float:
    """Calculate Reciprocal Rank (RR): 1 / rank of first relevant document."""
    if not gold_relevant_ids or not ranked_ids:
        return 0.0
    gold_set = {str(d).strip().lower() for d in gold_relevant_ids}
    for rank, doc_id in enumerate(ranked_ids, start=1):
        if str(doc_id).strip().lower() in gold_set:
            return 1.0 / float(rank)
    return 0.0


def dcg_at_k(ranked_ids: List[str], gold_relevant_ids: Set[str], k: int) -> float:
    """Calculate Discounted Cumulative Gain at rank K."""
    if not gold_relevant_ids or not ranked_ids or k <= 0:
        return 0.0
    gold_set = {str(d).strip().lower() for d in gold_relevant_ids}
    dcg = 0.0
    for i, doc_id in enumerate(ranked_ids[:k], start=1):
        rel = 1.0 if str(doc_id).strip().lower() in gold_set else 0.0
        dcg += (2.0 ** rel - 1.0) / math.log2(i + 1)
    return dcg


def ndcg_at_k(ranked_ids: List[str], gold_relevant_ids: Set[str], k: int) -> float:
    """Calculate Normalized Discounted Cumulative Gain at rank K."""
    actual_dcg = dcg_at_k(ranked_ids, gold_relevant_ids, k)
    if actual_dcg == 0.0:
        return 0.0
    # Ideal DCG: all gold relevant items placed at top
    ideal_hits = min(len(gold_relevant_ids), k)
    idcg = sum((2.0 ** 1.0 - 1.0) / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    if idcg == 0.0:
        return 0.0
    return actual_dcg / idcg


def evaluate_ranking_queries(evaluation_items: List[Dict[str, Any]], k_values: List[int] = None) -> Dict[str, Any]:
    """
    Evaluate ranking across a list of query items.
    Each item must contain:
    - 'query_id' or 'claim': Identifier/Text
    - 'ranked_doc_ids': List of retrieved doc IDs in ranked order
    - 'gold_relevant_ids': List or Set of gold relevant doc IDs
    """
    if k_values is None:
        k_values = [1, 3, 5, 10]

    num_queries = len(evaluation_items)
    if num_queries == 0:
        return {"num_queries": 0, "message": "No ranking evaluation queries provided."}

    mrr_list = []
    p_at_k = {k: [] for k in k_values}
    r_at_k = {k: [] for k in k_values}
    ndcg_at_k_dict = {k: [] for k in k_values}

    for item in evaluation_items:
        ranked = [str(d).strip().lower() for d in item.get("ranked_doc_ids", [])]
        gold = {str(d).strip().lower() for d in item.get("gold_relevant_ids", [])}

        mrr_list.append(reciprocal_rank(ranked, gold))
        for k in k_values:
            p_at_k[k].append(precision_at_k(ranked, gold, k))
            r_at_k[k].append(recall_at_k(ranked, gold, k))
            ndcg_at_k_dict[k].append(ndcg_at_k(ranked, gold, k))

    results = {
        "num_queries_evaluated": num_queries,
        "mrr": float(np.mean(mrr_list)),
        "precision_at_k": {f"P@{k}": float(np.mean(p_at_k[k])) for k in k_values},
        "recall_at_k": {f"R@{k}": float(np.mean(r_at_k[k])) for k in k_values},
        "ndcg_at_k": {f"NDCG@{k}": float(np.mean(ndcg_at_k_dict[k])) for k in k_values},
    }

    # Summary DataFrame for display
    summary_rows = []
    for k in k_values:
        summary_rows.append({
            "Cutoff K": f"Top-{k}",
            "Precision@K": f"{results['precision_at_k'][f'P@{k}']:.4f}",
            "Recall@K": f"{results['recall_at_k'][f'R@{k}']:.4f}",
            "NDCG@K": f"{results['ndcg_at_k'][f'NDCG@{k}']:.4f}",
        })
    results["summary_table"] = pd.DataFrame(summary_rows)
    return results


def print_ranking_report(results: Dict[str, Any], title: str = "RANKING EVALUATION REPORT"):
    """Format and print IR ranking metrics report."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    if results.get("num_queries_evaluated", 0) == 0:
        print("No ranking evaluation queries were provided.")
        return

    print(f"Number of queries evaluated : {results['num_queries_evaluated']}")
    print(f"Mean Reciprocal Rank (MRR)  : {results['mrr']:.4f}")
    print("\nCutoff Metrics:")
    print(results["summary_table"].to_string(index=False))


if __name__ == "__main__":
    # Self-test on known reference test queries
    test_queries = [
        {
            "query_id": "Q1",
            "ranked_doc_ids": ["doc_1", "doc_2", "doc_3", "doc_4", "doc_5"],
            "gold_relevant_ids": ["doc_1", "doc_3"],
        },
        {
            "query_id": "Q2",
            "ranked_doc_ids": ["doc_9", "doc_8", "doc_2", "doc_1", "doc_7"],
            "gold_relevant_ids": ["doc_2"],
        },
    ]

    res = evaluate_ranking_queries(test_queries, k_values=[1, 3, 5])
    print_ranking_report(res, "UNIT TEST: RANKING EVALUATION METRICS")
