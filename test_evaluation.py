"""
Unit and Integration Tests for Evaluation Module (evaluation_metrics.py).

Tests:
1. Hand-calculated known test case (symmetric 2-class)
2. Hand-calculated known test case (asymmetric 3-class with class imbalance)
3. Safe handling of empty datasets
4. Safe handling of missing, NaN, and None labels
5. Safe handling of label aliases and normalizations
6. Integration test with real saved predictions (evaluation_predictions.csv)
"""

import math
import numpy as np
import pandas as pd
import evaluation_metrics as em


def test_known_symmetric_example():
    """Test 1: Hand-calculated known 2-class example."""
    print("--- Test 1: Symmetric 2-Class Known Example ---")
    y_true = ["A", "A", "B", "B"]
    y_pred = ["A", "B", "B", "A"]

    metrics = em.calculate_metrics(y_true, y_pred, labels=["A", "B"])

    assert math.isclose(metrics["accuracy"], 0.50, rel_tol=1e-4), f"Expected 0.50, got {metrics['accuracy']}"
    assert math.isclose(metrics["macro_precision"], 0.50, rel_tol=1e-4)
    assert math.isclose(metrics["macro_recall"], 0.50, rel_tol=1e-4)
    assert math.isclose(metrics["macro_f1"], 0.50, rel_tol=1e-4)
    assert metrics["valid_samples"] == 4
    assert metrics["dropped_samples"] == 0

    print("Passed Test 1: Symmetric 2-class metrics exactly match 0.50 (50%).")


def test_known_asymmetric_3class_example():
    """Test 2: Hand-calculated 3-class asymmetric example with class imbalance."""
    print("\n--- Test 2: Asymmetric 3-Class Known Example (Class Imbalance) ---")
    # 5 samples: 3 entailment, 1 contradiction, 1 neutral
    y_true = ["entailment", "entailment", "entailment", "contradiction", "neutral"]
    y_pred = ["entailment", "entailment", "contradiction", "contradiction", "neutral"]

    metrics = em.calculate_metrics(y_true, y_pred, labels=["entailment", "contradiction", "neutral"])

    # Hand-calculated values:
    # Accuracy: 4/5 = 0.80
    assert math.isclose(metrics["accuracy"], 0.80, rel_tol=1e-4), f"Expected 0.80, got {metrics['accuracy']}"

    # Precision: entailment=2/2=1.0, contradiction=1/2=0.5, neutral=1/1=1.0 -> Macro = 2.5/3 = 0.8333
    assert math.isclose(metrics["macro_precision"], 2.5 / 3.0, rel_tol=1e-3)

    # Recall: entailment=2/3=0.6667, contradiction=1/1=1.0, neutral=1/1=1.0 -> Macro = (2/3 + 2)/3 = 0.8889
    assert math.isclose(metrics["macro_recall"], (2.0 / 3.0 + 2.0) / 3.0, rel_tol=1e-3)

    # Weighted F1: accounts for class support
    expected_weighted_f1 = (3 * 0.80 + 1 * (2 / 3) + 1 * 1.0) / 5.0
    assert math.isclose(metrics["weighted_f1"], expected_weighted_f1, rel_tol=1e-3)

    print(f"Passed Test 2: Accuracy={metrics['accuracy']:.2%}, Macro-F1={metrics['macro_f1']:.2%}, Weighted-F1={metrics['weighted_f1']:.2%}.")


def test_empty_dataset_handling():
    """Test 3: Empty dataset handling without exceptions."""
    print("\n--- Test 3: Empty Dataset Handling ---")
    metrics_empty = em.calculate_metrics([], [], labels=["entailment", "contradiction", "neutral"])
    assert metrics_empty["total_samples"] == 0
    assert metrics_empty["valid_samples"] == 0
    assert metrics_empty["accuracy"] == 0.0
    assert metrics_empty["macro_f1"] == 0.0

    metrics_none = em.calculate_metrics(None, None)
    assert metrics_none["total_samples"] == 0

    print("Passed Test 3: Empty datasets safely return zeroed metrics without crashing.")


def test_missing_and_invalid_labels():
    """Test 4: Handling missing, NaN, None, and mismatched length labels."""
    print("\n--- Test 4: Missing and Invalid Label Handling ---")
    y_true = ["entailment", None, np.nan, "neutral", "contradiction"]
    y_pred = ["entailment", "contradiction", "neutral", None, "contradiction"]

    metrics = em.calculate_metrics(y_true, y_pred, labels=["entailment", "contradiction", "neutral"])

    # Out of 5 pairs, only index 0 and index 4 have non-null values for both true and pred
    assert metrics["valid_samples"] == 2
    assert metrics["dropped_samples"] == 3
    assert metrics["accuracy"] == 1.0  # both (entailment, entailment) and (contradiction, contradiction) match

    print(f"Passed Test 4: Missing labels safely filtered. Valid: {metrics['valid_samples']}, Dropped: {metrics['dropped_samples']}.")


def test_label_normalization():
    """Test 5: Label normalization aliases."""
    print("\n--- Test 5: Label Normalization ---")
    assert em.normalize_nli_label("SUPPORT") == "entailment"
    assert em.normalize_nli_label("supported") == "entailment"
    assert em.normalize_nli_label("contradicts") == "contradiction"
    assert em.normalize_nli_label("refuted") == "contradiction"
    assert em.normalize_nli_label("neutral") == "neutral"
    assert em.normalize_nli_label("invalid_xyz") is None

    assert em.normalize_verdict("supported") == "Potentially supported"
    assert em.normalize_verdict("refuted") == "Potentially refuted"
    assert em.normalize_verdict("insufficient") == "Insufficient evidence"
    assert em.normalize_verdict("mixed") == "Mixed evidence"

    print("Passed Test 5: All label aliases normalized correctly.")


def test_real_predictions_file():
    """Test 6: Integration test on evaluation_predictions.csv."""
    print("\n--- Test 6: Integration Test on Saved Predictions ---")
    res = em.evaluate_predictions_file("evaluation_predictions.csv")

    assert res["error"] is None, f"Error reading predictions: {res['error']}"
    assert res["nli"] is not None
    assert res["verdict"] is not None
    assert res["nli"]["valid_samples"] == len(res["df"])
    assert res["verdict"]["valid_samples"] == len(res["df"])

    # Model accuracy should be above 75% on validated ground truth
    assert res["nli"]["accuracy"] >= 0.75
    assert res["verdict"]["accuracy"] >= 0.75

    print(f"Passed Test 6: Predictions file verified. NLI Acc={res['nli']['accuracy']:.1%}, Verdict Acc={res['verdict']['accuracy']:.1%}.")


def test_expanded_dataset_and_ranking():
    """Test 7 & 8: Expanded dataset validation and ranking metrics."""
    print("\n--- Test 7: Expanded Dataset Integrity ---")
    df = pd.read_csv("evaluation_dataset_expanded.csv")
    assert len(df) in {60, 70}, f"Expected 60 or 70 examples, got {len(df)}"
    assert "example_id" in df.columns
    assert "claim" in df.columns
    assert "evidence" in df.columns
    assert "gold_doc_id" in df.columns
    assert "source_dataset" in df.columns
    assert "true_nli_label" in df.columns
    assert "true_verdict" in df.columns
    print(f"Passed Test 7: evaluation_dataset_expanded.csv verified with {len(df)} distinct examples.")

    print("\n--- Test 8: Ranking Metrics Calculations ---")
    import evaluate_ranking as er
    ranked = ["doc_A", "doc_B", "doc_C", "doc_D"]
    gold = {"doc_B"}
    assert er.reciprocal_rank(ranked, gold) == 0.5, "Expected MRR = 0.5 for rank 2"
    assert er.precision_at_k(ranked, gold, 1) == 0.0
    assert er.precision_at_k(ranked, gold, 2) == 0.5
    assert er.recall_at_k(ranked, gold, 2) == 1.0
    print("Passed Test 8: Ranking calculations (MRR, P@K, R@K) verified mathematically.")



def test_decision_engine_consensus_and_mixed():
    """Test 9: Decision Engine ratio/weighted threshold, 9-vs-1 consensus, and mixed split."""
    print("\n--- Test 9: Decision Engine Ratio Consensus & Mixed Evidence ---")
    import decision_engine as de

    # 1. 9-vs-1 consensus contradiction -> Potentially refuted
    v1, _ = de.determine_verdict([{'relationship': 'contradiction', 'confidence': 0.9}]*9 + [{'relationship': 'support', 'confidence': 0.8}])
    assert v1 == 'Potentially refuted', f"Expected Potentially refuted, got {v1}"

    # 2. 9-vs-1 consensus support -> Potentially supported
    v2, _ = de.determine_verdict([{'relationship': 'support', 'confidence': 0.9}]*9 + [{'relationship': 'contradiction', 'confidence': 0.8}])
    assert v2 == 'Potentially supported', f"Expected Potentially supported, got {v2}"

    # 3. 5-vs-5 divided split -> Mixed evidence
    v3, _ = de.determine_verdict([{'relationship': 'support', 'confidence': 0.85}]*5 + [{'relationship': 'contradiction', 'confidence': 0.85}]*5)
    assert v3 == 'Mixed evidence', f"Expected Mixed evidence, got {v3}"

    # 4. 3-vs-2 divided split -> Mixed evidence
    v4, _ = de.determine_verdict([{'relationship': 'support', 'confidence': 0.85}]*3 + [{'relationship': 'contradiction', 'confidence': 0.85}]*2)
    assert v4 == 'Mixed evidence', f"Expected Mixed evidence, got {v4}"

    # 5. Pure contradiction -> Potentially refuted
    v5, _ = de.determine_verdict([{'relationship': 'contradiction', 'confidence': 0.95}]*3)
    assert v5 == 'Potentially refuted', f"Expected Potentially refuted, got {v5}"

    # 6. Pure support -> Potentially supported
    v6, _ = de.determine_verdict([{'relationship': 'support', 'confidence': 0.95}]*3)
    assert v6 == 'Potentially supported', f"Expected Potentially supported, got {v6}"

    # 7. Neutral context only -> Insufficient evidence
    v7, _ = de.determine_verdict([{'relationship': 'neutral', 'confidence': 0.95}]*3)
    assert v7 == 'Insufficient evidence', f"Expected Insufficient evidence, got {v7}"

    print("Passed Test 9: Decision Engine ratio consensus (9-vs-1 solved) and divided mixed splits verified.")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING EVALUATION MODULE TEST SUITE")
    print("=" * 60)
    test_known_symmetric_example()
    test_known_asymmetric_3class_example()
    test_empty_dataset_handling()
    test_missing_and_invalid_labels()
    test_label_normalization()
    test_real_predictions_file()
    test_expanded_dataset_and_ranking()
    test_decision_engine_consensus_and_mixed()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
