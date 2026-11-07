import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from evaluation_metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

df = pd.read_csv("evaluation_dataset_expanded.csv")

print("Running Baseline: SBERT Bi-Encoder Semantic Similarity...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

claims = df["claim"].tolist()
evidences = df["evidence"].tolist()

claim_embeds = model.encode(claims, convert_to_numpy=True, normalize_embeddings=True)
evidence_embeds = model.encode(evidences, convert_to_numpy=True, normalize_embeddings=True)

# Cosine similarity for each pair
sims = np.sum(claim_embeds * evidence_embeds, axis=1)

# Bi-encoder thresholding baseline:
pred_baseline_nli = []
for sim in sims:
    if sim >= 0.70:
        pred_baseline_nli.append("entailment")
    elif sim >= 0.45:
        pred_baseline_nli.append("neutral")
    else:
        pred_baseline_nli.append("contradiction")

true_nli = df["true_nli_label"].tolist()

acc = accuracy_score(true_nli, pred_baseline_nli)
macro_f1 = f1_score(true_nli, pred_baseline_nli, average="macro", zero_division=0)
weighted_f1 = f1_score(true_nli, pred_baseline_nli, average="weighted", zero_division=0)

print("\n--- BASELINE RESULTS (SBERT Cosine Similarity Thresholding) ---")
print(f"Accuracy          : {acc:.4f} ({acc:.2%})")
print(f"Macro F1-score    : {macro_f1:.4f} ({macro_f1:.2%})")
print(f"Weighted F1-score : {weighted_f1:.4f} ({weighted_f1:.2%})")
print("\nConfusion Matrix (labels=['entailment', 'contradiction', 'neutral']):")
print(confusion_matrix(true_nli, pred_baseline_nli, labels=["entailment", "contradiction", "neutral"]))
