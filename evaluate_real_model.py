import os
import sys

# Set offline environment variables before transformers/huggingface imports
if os.environ.get("HF_HUB_OFFLINE") is None:
    os.environ["HF_HUB_OFFLINE"] = "1"
if os.environ.get("TRANSFORMERS_OFFLINE") is None:
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

import ast
import pandas as pd

import nli_classifier as nli
import decision_engine as de
import evaluation_metrics as em


# ============================================================
# CONFIGURATION
# ============================================================

# Allow passing dataset path via CLI argument (default: evaluation_dataset_10.csv or evaluation_dataset.csv)
if len(sys.argv) > 1 and sys.argv[1].endswith(".csv"):
    DATASET_PATH = sys.argv[1]
elif os.path.exists("evaluation_dataset_expanded.csv"):
    DATASET_PATH = "evaluation_dataset_expanded.csv"
elif os.path.exists("evaluation_dataset.csv"):
    DATASET_PATH = "evaluation_dataset.csv"
else:
    DATASET_PATH = "evaluation_dataset_10.csv"

OUTPUT_PATH = "evaluation_predictions.csv"

NLI_LABELS = em.NLI_LABELS
VERDICT_LABELS = em.VERDICT_LABELS


# ============================================================
# LABEL NORMALIZATION
# ============================================================

def normalize_nli_label(label):
    return em.normalize_nli_label(label)


def normalize_verdict(label):
    return em.normalize_verdict(label)


def safe_parse_scores(scores):
    """Parse scores when stored as a string."""
    if isinstance(scores, str):
        try:
            return ast.literal_eval(scores)
        except (ValueError, SyntaxError):
            return scores
    return scores


# ============================================================
# METRICS DISPLAY
# ============================================================

def print_metrics(y_true, y_pred, labels, title):
    """Calculate and display metrics using evaluation_metrics module."""
    return em.evaluate_model(y_true, y_pred, labels=labels, model_name=title)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. Load and validate dataset
    # --------------------------------------------------------

    print("Loading labeled evaluation dataset...")

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}\n"
            "Make sure the CSV is in your project directory."
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = {
        "claim",
        "evidence",
        "true_nli_label",
        "true_verdict",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required CSV columns: {sorted(missing_columns)}"
        )

    # Preserve original labels for clear validation errors.
    original_nli_labels = df["true_nli_label"].copy()
    original_verdict_labels = df["true_verdict"].copy()

    # Clean text fields.
    df["claim"] = df["claim"].fillna("").astype(str).str.strip()
    df["evidence"] = (
        df["evidence"].fillna("").astype(str).str.strip()
    )

    # Normalize ground-truth labels.
    df["true_nli_label"] = df["true_nli_label"].apply(
        normalize_nli_label
    )

    df["true_verdict"] = df["true_verdict"].apply(
        normalize_verdict
    )

    # Validate NLI labels.
    invalid_nli = sorted(
        set(
            str(value)
            for value in original_nli_labels
            if normalize_nli_label(value) is None
        )
    )

    if invalid_nli:
        raise ValueError(
            f"Invalid true_nli_label values: {invalid_nli}"
        )

    # Validate verdict labels.
    invalid_verdict = sorted(
        set(
            str(value)
            for value in original_verdict_labels
            if normalize_verdict(value) is None
        )
    )

    if invalid_verdict:
        raise ValueError(
            f"Invalid true_verdict values: {invalid_verdict}"
        )

    # Keep only rows containing claims and evidence.
    usable_mask = (
        df["claim"].ne("")
        & df["evidence"].ne("")
    )

    skipped_rows = int((~usable_mask).sum())

    if skipped_rows:
        print(f"Skipping {skipped_rows} incomplete rows.")

    df = df.loc[usable_mask].copy().reset_index(drop=True)

    if df.empty:
        raise ValueError(
            "No usable examples found in the evaluation dataset."
        )

    print(f"Loaded {len(df)} evaluation examples from {DATASET_PATH}.")

    print("\nGround-truth NLI label counts:")
    print(df["true_nli_label"].value_counts())

    print("\nGround-truth verdict counts:")
    print(df["true_verdict"].value_counts())

    # --------------------------------------------------------
    # 2. Load NLI model
    # --------------------------------------------------------

    print("\nLoading the NLI model...")
    print(f"Model: {nli.MODEL_NAME}")

    model = nli.CrossEncoder(nli.MODEL_NAME)

    label_names = nli.get_label_names(model)

    print("Model label mapping:")
    print(label_names)

    # --------------------------------------------------------
    # 3. Prepare records WITHOUT premise contamination
    # --------------------------------------------------------

    records = []

    for _, row in df.iterrows():
        # Title must be empty string so claim is NOT prepended to evidence text
        records.append({
            "claim": row["claim"],
            "title": "",
            "abstract": row["evidence"],
        })

    # --------------------------------------------------------
    # 4. Run NLI predictions (without max_records truncation)
    # --------------------------------------------------------

    print("\nRunning NLI predictions...")

    predicted_records = nli.classify_records(
        records=records,
        model=model,
        label_names=label_names,
        source_name="Evaluation dataset",
        user_claim="",
        max_records=None,
    )

    if not isinstance(predicted_records, list):
        raise TypeError(
            "classify_records() must return a list, but returned "
            f"{type(predicted_records).__name__}."
        )

    if len(predicted_records) != len(df):
        raise ValueError(
            f"Expected {len(df)} predictions but received "
            f"{len(predicted_records)}. "
            "Check nli_classifier.py for record limits or filtering."
        )

    # --------------------------------------------------------
    # 5. Extract predicted labels and scores
    # --------------------------------------------------------

    predicted_nli = []
    confidences = []
    score_values = []

    for index, item in enumerate(predicted_records):

        if not isinstance(item, dict):
            raise TypeError(
                f"Prediction {index + 1} is not a dictionary."
            )

        predicted_label = normalize_nli_label(
            item.get("nli_label")
        )

        if predicted_label not in NLI_LABELS:
            raise ValueError(
                f"Invalid predicted NLI label at row {index + 1}: "
                f"{item.get('nli_label')!r}"
            )

        predicted_nli.append(predicted_label)
        confidences.append(item.get("nli_confidence"))

        score_values.append(
            safe_parse_scores(item.get("nli_scores"))
        )

    df["predicted_nli_label"] = predicted_nli
    df["nli_confidence"] = confidences
    df["nli_scores"] = [
        str(value) for value in score_values
    ]

    # --------------------------------------------------------
    # 6. Evaluate NLI classifier
    # --------------------------------------------------------

    print_metrics(
        y_true=df["true_nli_label"].tolist(),
        y_pred=df["predicted_nli_label"].tolist(),
        labels=NLI_LABELS,
        title="NLI MODEL EVALUATION",
    )

    # --------------------------------------------------------
    # 7. Decision Engine evaluation
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DECISION ENGINE EVALUATION")
    print("=" * 60)

    # Aggregate predicted evidence records by claim to evaluate multi-evidence claims,
    # genuine mixed evidence splits, and consensus decisions accurately.
    claim_groups = {}
    claim_order = []
    for item, (_, row) in zip(predicted_records, df.iterrows()):
        c = row["claim"]
        if c not in claim_groups:
            claim_groups[c] = []
            claim_order.append(c)
        claim_groups[c].append(item)

    claim_to_verdict = {}
    claim_to_error = {}

    for c in claim_order:
        items = claim_groups[c]
        try:
            source_result = de.process_source(items, "Evaluation")
            if not isinstance(source_result, tuple) or len(source_result) != 3:
                raise ValueError("process_source() returned an unexpected format.")
            summary, accepted, rejected = source_result
            verdict_result = de.determine_verdict(accepted)
            if isinstance(verdict_result, tuple):
                verdict_value = verdict_result[0]
            else:
                verdict_value = verdict_result
            normalized_verdict = normalize_verdict(verdict_value)
            if normalized_verdict not in VERDICT_LABELS:
                raise ValueError(f"Unexpected verdict returned: {verdict_value!r}")
            claim_to_verdict[c] = normalized_verdict
            claim_to_error[c] = ""
        except Exception as exc:
            print(f"Warning: Decision Engine failed on claim '{c[:40]}...': {exc}")
            claim_to_verdict[c] = None
            claim_to_error[c] = str(exc)

    predicted_verdicts = [claim_to_verdict.get(row["claim"]) for _, row in df.iterrows()]
    decision_errors = [claim_to_error.get(row["claim"], "") for _, row in df.iterrows()]

    df["predicted_verdict"] = predicted_verdicts
    df["decision_engine_error"] = decision_errors

    valid_mask = df["predicted_verdict"].isin(VERDICT_LABELS)

    valid_df = df.loc[valid_mask].copy()

    print(
        f"\nValid Decision Engine predictions: "
        f"{len(valid_df)} / {len(df)}"
    )

    if not valid_df.empty:

        print_metrics(
            y_true=valid_df["true_verdict"].tolist(),
            y_pred=valid_df["predicted_verdict"].tolist(),
            labels=VERDICT_LABELS,
            title="DECISION ENGINE EVALUATION",
        )

    else:
        print(
            "No valid Decision Engine verdicts were produced. "
            "Inspect decision_engine.py and the warnings above."
        )

    # --------------------------------------------------------
    # 8. Save results
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n" + "=" * 60)
    print("EVALUATION FINISHED")
    print("=" * 60)

    print(f"Dataset used      : {DATASET_PATH}")
    print(f"Rows evaluated    : {len(df)}")
    print(f"Predictions saved : {OUTPUT_PATH}")

    if skipped_rows:
        print(f"Rows skipped      : {skipped_rows}")

    print(
        "\nImportant: these metrics are meaningful only when "
        "the ground-truth labels have been independently verified."
    )


if __name__ == "__main__":
    main()
