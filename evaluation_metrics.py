"""
Backend evaluation module for the AI-Assisted Health Information Verification System.

Provides robust, safe calculation of:
- Accuracy
- Precision (Macro and Weighted for class imbalance)
- Recall (Macro and Weighted for class imbalance)
- F1-score (Macro and Weighted for class imbalance)
- Per-class breakdown (Precision, Recall, F1-Score, Support)
- Confusion Matrix

Supports:
- Level 1: NLI classifier evaluation (premise-evidence vs hypothesis-claim)
- Level 2: Final decision engine evaluation (verdict aggregation)

Handles empty datasets, missing labels, invalid inputs, and class imbalance safely.
Can be imported by Streamlit (app.py) or run standalone via CLI.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

try:
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        classification_report,
        confusion_matrix,
    )
except ImportError:
    # Graceful native pure-Python/NumPy fallback when scikit-learn is not installed in the active environment
    def accuracy_score(y_true, y_pred):
        if not y_true:
            return 0.0
        correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
        return float(correct / len(y_true))

    def confusion_matrix(y_true, y_pred, labels=None):
        if labels is None:
            labels = sorted(list(set(y_true) | set(y_pred)))
        label_to_idx = {lbl: idx for idx, lbl in enumerate(labels)}
        matrix = np.zeros((len(labels), len(labels)), dtype=int)
        for yt, yp in zip(y_true, y_pred):
            if yt in label_to_idx and yp in label_to_idx:
                matrix[label_to_idx[yt], label_to_idx[yp]] += 1
        return matrix

    def precision_score(y_true, y_pred, labels=None, average=None, zero_division=0):
        if labels is None:
            labels = sorted(list(set(y_true) | set(y_pred)))
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        precisions = []
        for i in range(len(labels)):
            tp = cm[i, i]
            col_sum = cm[:, i].sum()
            prec = float(tp / col_sum) if col_sum > 0 else float(zero_division)
            precisions.append(prec)
        precisions = np.array(precisions)
        if average is None:
            return precisions
        if average == "macro":
            return float(np.mean(precisions)) if len(precisions) > 0 else float(zero_division)
        if average == "weighted":
            supports = cm.sum(axis=1)
            total = supports.sum()
            return float(np.sum(precisions * supports) / total) if total > 0 else float(zero_division)
        return precisions

    def recall_score(y_true, y_pred, labels=None, average=None, zero_division=0):
        if labels is None:
            labels = sorted(list(set(y_true) | set(y_pred)))
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        recalls = []
        for i in range(len(labels)):
            tp = cm[i, i]
            row_sum = cm[i, :].sum()
            rec = float(tp / row_sum) if row_sum > 0 else float(zero_division)
            recalls.append(rec)
        recalls = np.array(recalls)
        if average is None:
            return recalls
        if average == "macro":
            return float(np.mean(recalls)) if len(recalls) > 0 else float(zero_division)
        if average == "weighted":
            supports = cm.sum(axis=1)
            total = supports.sum()
            return float(np.sum(recalls * supports) / total) if total > 0 else float(zero_division)
        return recalls

    def f1_score(y_true, y_pred, labels=None, average=None, zero_division=0):
        if labels is None:
            labels = sorted(list(set(y_true) | set(y_pred)))
        p = precision_score(y_true, y_pred, labels=labels, average=None, zero_division=zero_division)
        r = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=zero_division)
        f1s = []
        for pi, ri in zip(p, r):
            if (pi + ri) > 0:
                f1s.append(2.0 * pi * ri / (pi + ri))
            else:
                f1s.append(float(zero_division))
        f1s = np.array(f1s)
        if average is None:
            return f1s
        if average == "macro":
            return float(np.mean(f1s)) if len(f1s) > 0 else float(zero_division)
        if average == "weighted":
            cm = confusion_matrix(y_true, y_pred, labels=labels)
            supports = cm.sum(axis=1)
            total = supports.sum()
            return float(np.sum(f1s * supports) / total) if total > 0 else float(zero_division)
        return f1s

    def classification_report(y_true, y_pred, labels=None, zero_division=0):
        if labels is None:
            labels = sorted(list(set(y_true) | set(y_pred)))
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        p = precision_score(y_true, y_pred, labels=labels, average=None, zero_division=zero_division)
        r = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=zero_division)
        f = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=zero_division)
        supports = cm.sum(axis=1)

        lines = [f"{'':>25} {'precision':>10} {'recall':>10} {'f1-score':>10} {'support':>10}\n"]
        for lbl, pi, ri, fi, si in zip(labels, p, r, f, supports):
            lines.append(f"{str(lbl):>25} {pi:>10.2f} {ri:>10.2f} {fi:>10.2f} {si:>10d}\n")
        lines.append("\n")
        acc = accuracy_score(y_true, y_pred)
        lines.append(f"{'accuracy':>25} {'':>10} {'':>10} {acc:>10.2f} {sum(supports):>10d}\n")
        mac_p = precision_score(y_true, y_pred, labels=labels, average='macro', zero_division=zero_division)
        mac_r = recall_score(y_true, y_pred, labels=labels, average='macro', zero_division=zero_division)
        mac_f = f1_score(y_true, y_pred, labels=labels, average='macro', zero_division=zero_division)
        lines.append(f"{'macro avg':>25} {mac_p:>10.2f} {mac_r:>10.2f} {mac_f:>10.2f} {sum(supports):>10d}\n")
        w_p = precision_score(y_true, y_pred, labels=labels, average='weighted', zero_division=zero_division)
        w_r = recall_score(y_true, y_pred, labels=labels, average='weighted', zero_division=zero_division)
        w_f = f1_score(y_true, y_pred, labels=labels, average='weighted', zero_division=zero_division)
        lines.append(f"{'weighted avg':>25} {w_p:>10.2f} {w_r:>10.2f} {w_f:>10.2f} {sum(supports):>10d}\n")
        return "".join(lines)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PREDICTIONS_PATH = BASE_DIR / "evaluation_predictions.csv"
DEFAULT_DATASET_PATH = BASE_DIR / "evaluation_dataset.csv"

# ============================================================
# CANONICAL LABELS AND NORMALIZATION
# ============================================================

NLI_LABELS = [
    "entailment",
    "contradiction",
    "neutral",
]

VERDICT_LABELS = [
    "Potentially supported",
    "Potentially refuted",
    "Mixed evidence",
    "Insufficient evidence",
]

NLI_ALIASES = {
    "entailment": "entailment",
    "entails": "entailment",
    "support": "entailment",
    "supported": "entailment",
    "contradiction": "contradiction",
    "contradicts": "contradiction",
    "refute": "contradiction",
    "refutes": "contradiction",
    "refuted": "contradiction",
    "neutral": "neutral",
    "unrelated": "neutral",
}

VERDICT_ALIASES = {
    "supported": "Potentially supported",
    "potentially supported": "Potentially supported",
    "refuted": "Potentially refuted",
    "potentially refuted": "Potentially refuted",
    "mixed": "Mixed evidence",
    "mixed evidence": "Mixed evidence",
    "insufficient": "Insufficient evidence",
    "insufficient evidence": "Insufficient evidence",
    "unresolved": "Insufficient evidence",
}


def normalize_nli_label(label):
    """Normalize raw label strings into canonical NLI labels."""
    if label is None or pd.isna(label):
        return None
    value = str(label).strip().lower()
    return NLI_ALIASES.get(value)


def normalize_verdict(label):
    """Normalize raw label strings into canonical verdict labels."""
    if label is None or pd.isna(label):
        return None
    value = str(label).strip().lower()
    return VERDICT_ALIASES.get(value)


# ============================================================
# SAFE METRICS CALCULATION
# ============================================================

def calculate_metrics(y_true, y_pred, labels=None):
    """
    Safely calculate Accuracy, Precision, Recall, F1 (macro & weighted),
    per-class breakdown, and confusion matrix.

    Handles:
    - Empty datasets / 0 rows (returns zeroed metrics dict without crashing)
    - Missing/NaN/None values (safely drops unmatchable pairs and reports count)
    - Class imbalance (returns both macro and weighted metrics)
    - Invalid labels
    """
    empty_result = {
        "total_samples": 0,
        "valid_samples": 0,
        "dropped_samples": 0,
        "accuracy": 0.0,
        "macro_precision": 0.0,
        "macro_recall": 0.0,
        "macro_f1": 0.0,
        "weighted_precision": 0.0,
        "weighted_recall": 0.0,
        "weighted_f1": 0.0,
        "labels": labels or [],
        "class_metrics": pd.DataFrame(
            columns=["Class", "Precision", "Recall", "F1-Score", "Support"]
        ),
        "confusion_matrix": np.zeros((0, 0), dtype=int),
        "confusion_matrix_df": pd.DataFrame(),
        "classification_report_str": "No valid evaluation samples provided.",
    }

    if y_true is None or y_pred is None:
        return empty_result

    total_samples = max(len(y_true), len(y_pred))
    if total_samples == 0:
        return empty_result

    # Pairwise filter for valid, non-null labels
    paired = []
    dropped_count = 0
    for true_val, pred_val in zip(y_true, y_pred):
        if true_val is None or pd.isna(true_val) or pred_val is None or pd.isna(pred_val):
            dropped_count += 1
            continue
        true_str = str(true_val).strip()
        pred_str = str(pred_val).strip()
        if not true_str or not pred_str:
            dropped_count += 1
            continue
        paired.append((true_str, pred_str))

    # Also account for length mismatch
    if len(y_true) != len(y_pred):
        dropped_count += abs(len(y_true) - len(y_pred))

    if not paired:
        res = dict(empty_result)
        res["total_samples"] = total_samples
        res["dropped_samples"] = dropped_count
        return res

    clean_true = [p[0] for p in paired]
    clean_pred = [p[1] for p in paired]

    # Resolve target labels
    if labels is None:
        inferred_labels = sorted(list(set(clean_true) | set(clean_pred)))
    else:
        inferred_labels = list(labels)

    # 1. Overall Accuracy
    accuracy = float(accuracy_score(clean_true, clean_pred))

    # 2. Macro Metrics (Equal weight to each class)
    macro_precision = float(
        precision_score(clean_true, clean_pred, labels=inferred_labels, average="macro", zero_division=0)
    )
    macro_recall = float(
        recall_score(clean_true, clean_pred, labels=inferred_labels, average="macro", zero_division=0)
    )
    macro_f1 = float(
        f1_score(clean_true, clean_pred, labels=inferred_labels, average="macro", zero_division=0)
    )

    # 3. Weighted Metrics (Weighted by support - handles class imbalance safely)
    weighted_precision = float(
        precision_score(clean_true, clean_pred, labels=inferred_labels, average="weighted", zero_division=0)
    )
    weighted_recall = float(
        recall_score(clean_true, clean_pred, labels=inferred_labels, average="weighted", zero_division=0)
    )
    weighted_f1 = float(
        f1_score(clean_true, clean_pred, labels=inferred_labels, average="weighted", zero_division=0)
    )

    # 4. Per-class metrics
    per_class_precision = precision_score(
        clean_true, clean_pred, labels=inferred_labels, average=None, zero_division=0
    )
    per_class_recall = recall_score(
        clean_true, clean_pred, labels=inferred_labels, average=None, zero_division=0
    )
    per_class_f1 = f1_score(
        clean_true, clean_pred, labels=inferred_labels, average=None, zero_division=0
    )

    class_rows = []
    for idx, lbl in enumerate(inferred_labels):
        support_cnt = int(sum(1 for t in clean_true if t == lbl))
        class_rows.append({
            "Class": lbl,
            "Precision": float(per_class_precision[idx]),
            "Recall": float(per_class_recall[idx]),
            "F1-Score": float(per_class_f1[idx]),
            "Support": support_cnt,
        })
    class_metrics_df = pd.DataFrame(class_rows)

    # 5. Confusion Matrix
    cm = confusion_matrix(clean_true, clean_pred, labels=inferred_labels)
    cm_df = pd.DataFrame(
        cm,
        index=[f"Actual: {lbl}" for lbl in inferred_labels],
        columns=[f"Predicted: {lbl}" for lbl in inferred_labels],
    )

    # 6. Detailed text report
    report_str = classification_report(
        clean_true,
        clean_pred,
        labels=inferred_labels,
        zero_division=0,
    )

    return {
        "total_samples": total_samples,
        "valid_samples": len(paired),
        "dropped_samples": dropped_count,
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "labels": inferred_labels,
        "class_metrics": class_metrics_df,
        "confusion_matrix": cm,
        "confusion_matrix_df": cm_df,
        "classification_report_str": report_str,
    }


def evaluate_model(y_true, y_pred, labels, model_name="EVALUATION"):
    """
    Calculate and print evaluation metrics for console/terminal use.
    Maintains full backward compatibility with existing code.
    """
    metrics = calculate_metrics(y_true, y_pred, labels=labels)

    print("\n" + "=" * 60)
    print(model_name)
    print("=" * 60)

    if metrics["valid_samples"] == 0:
        print("Warning: No valid evaluation examples were provided.")
        return {
            "accuracy": 0.0,
            "precision_macro": 0.0,
            "recall_macro": 0.0,
            "f1_macro": 0.0,
            "precision_weighted": 0.0,
            "recall_weighted": 0.0,
            "f1_weighted": 0.0,
            "details": metrics,
        }

    print(f"Total samples  : {metrics['total_samples']}")
    print(f"Valid evaluated: {metrics['valid_samples']}")
    if metrics["dropped_samples"] > 0:
        print(f"Dropped/missing: {metrics['dropped_samples']}")

    print(f"Accuracy          : {metrics['accuracy']:.4f} ({metrics['accuracy']:.2%})")
    print(f"Macro Precision   : {metrics['macro_precision']:.4f} ({metrics['macro_precision']:.2%})")
    print(f"Macro Recall      : {metrics['macro_recall']:.4f} ({metrics['macro_recall']:.2%})")
    print(f"Macro F1-score    : {metrics['macro_f1']:.4f} ({metrics['macro_f1']:.2%})")
    print(f"Weighted F1-score : {metrics['weighted_f1']:.4f} ({metrics['weighted_f1']:.2%})")

    print("\nClassification Report:")
    print(metrics["classification_report_str"])

    print("Confusion Matrix:")
    print(metrics["confusion_matrix_df"].to_string())

    return {
        "accuracy": metrics["accuracy"],
        "precision_macro": metrics["macro_precision"],
        "recall_macro": metrics["macro_recall"],
        "f1_macro": metrics["macro_f1"],
        "precision_weighted": metrics["weighted_precision"],
        "recall_weighted": metrics["weighted_recall"],
        "f1_weighted": metrics["weighted_f1"],
        "details": metrics,
    }


# ============================================================
# EVALUATE FROM CSV FILE
# ============================================================

def evaluate_predictions_file(file_path=DEFAULT_PREDICTIONS_PATH):
    """
    Load a predictions CSV (e.g. evaluation_predictions.csv) and compute
    metrics for both NLI Classifier and Decision Engine Verdicts.
    """
    path = Path(file_path)
    if not path.exists():
        return {
            "error": f"Predictions file not found: {path}",
            "nli": None,
            "verdict": None,
            "df": None,
        }

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        return {
            "error": f"Error reading CSV file: {exc}",
            "nli": None,
            "verdict": None,
            "df": None,
        }

    results = {
        "error": None,
        "nli": None,
        "verdict": None,
        "df": df,
    }

    # Level 1: NLI Model
    if "true_nli_label" in df.columns and "predicted_nli_label" in df.columns:
        norm_true_nli = df["true_nli_label"].apply(normalize_nli_label).tolist()
        norm_pred_nli = df["predicted_nli_label"].apply(normalize_nli_label).tolist()
        results["nli"] = calculate_metrics(
            norm_true_nli,
            norm_pred_nli,
            labels=NLI_LABELS,
        )

    # Level 2: Verdict
    if "true_verdict" in df.columns and "predicted_verdict" in df.columns:
        norm_true_verdict = df["true_verdict"].apply(normalize_verdict).tolist()
        norm_pred_verdict = df["predicted_verdict"].apply(normalize_verdict).tolist()
        results["verdict"] = calculate_metrics(
            norm_true_verdict,
            norm_pred_verdict,
            labels=VERDICT_LABELS,
        )

    return results


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AI-ASSISTED HEALTH INFORMATION VERIFICATION SYSTEM")
    print("SYSTEM EVALUATION METRICS REPORT")
    print("=" * 60)

    # 1. Prefer actual evaluation predictions if available
    if DEFAULT_PREDICTIONS_PATH.exists():
        print(f"\nEvaluating saved predictions from: {DEFAULT_PREDICTIONS_PATH.name}")
        res = evaluate_predictions_file(DEFAULT_PREDICTIONS_PATH)

        if res["nli"]:
            evaluate_model(
                y_true=res["df"]["true_nli_label"].apply(normalize_nli_label).tolist(),
                y_pred=res["df"]["predicted_nli_label"].apply(normalize_nli_label).tolist(),
                labels=NLI_LABELS,
                model_name="LEVEL 1: NLI CLASSIFIER EVALUATION",
            )

        if res["verdict"]:
            evaluate_model(
                y_true=res["df"]["true_verdict"].apply(normalize_verdict).tolist(),
                y_pred=res["df"]["predicted_verdict"].apply(normalize_verdict).tolist(),
                labels=VERDICT_LABELS,
                model_name="LEVEL 2: FINAL DECISION ENGINE VERDICT EVALUATION",
            )

    else:
        print("\nNo evaluation_predictions.csv found.")
        print("To generate predictions, run: python evaluate_real_model.py")
        print("\nRunning demonstration benchmark on reference test examples:")

        demo_nli_true = ["entailment", "contradiction", "neutral", "entailment", "contradiction", "neutral"]
        demo_nli_pred = ["entailment", "contradiction", "neutral", "neutral", "contradiction", "neutral"]
        evaluate_model(demo_nli_true, demo_nli_pred, NLI_LABELS, "DEMO: LEVEL 1 NLI")

        demo_dec_true = ["Potentially supported", "Potentially refuted", "Insufficient evidence", "Potentially supported", "Potentially refuted", "Insufficient evidence"]
        demo_dec_pred = ["Potentially supported", "Potentially refuted", "Insufficient evidence", "Insufficient evidence", "Potentially refuted", "Insufficient evidence"]
        evaluate_model(demo_dec_true, demo_dec_pred, VERDICT_LABELS, "DEMO: LEVEL 2 DECISION ENGINE")
