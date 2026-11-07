# AI-Assisted Health Information Verification System

A research prototype that analyzes health-related statements using fact-check retrieval, biomedical literature (PubMed), semantic ranking (SBERT, MedCPT), and Natural Language Inference (NLI).

---

## Evidence Retrieval & Ranking Architecture

The system retrieves candidate evidence from two complementary sources and filters them through domain-specific rankers:

### 1. Google Fact Check Retrieval & SBERT Ranking
- **Retrieval**: Queries the Google Fact Check Tools API (`claims:search`) with the user's claim and extracted key phrases, requesting up to **100 records** per API query.
- **Ranking**: Sentence-BERT (`sentence-transformers/all-MiniLM-L6-v2`) computes semantic cosine similarity between the claim and the retrieved fact-check claim text/reviews.
- **Selection**: Up to the **top 10** highest-ranked fact-check records are forwarded to the NLI classification stage.

### 2. PubMed Biomedical Literature Retrieval & MedCPT Ranking
- **Retrieval**: Searches the NCBI Entrez E-Utilities database across multiple generated query variants (literal claim, keywords, core terms).
  - **Results per query**: Up to **50 article IDs** (`MAX_RESULTS_PER_QUERY = 50`) are requested per query.
  - **Candidate ceiling**: A maximum of **100 unique PubMed IDs** (`MAX_UNIQUE_PMIDS = 100`) are collected, deduplicated, and fetched with full titles and abstracts.
- **Ranking**: Evaluated with **MedCPT** (`ncbi/MedCPT-Cross-Encoder`), a pre-trained biomedical information retrieval model trained on large-scale PubMed query–article data. It scores the relevance of each article's title and abstract against the claim.
- **Selection**: Up to the **top 10** highest-ranked research articles (`TOP_N = 10`) are forwarded to the NLI classification stage.

> **Implementation Note on Candidate Limits**:
> The setting of 50 PubMed results per query and 100 maximum unique PMIDs is an implementation configuration (defined in `pubmed_retriever.py`), rather than a strict requirement of the MedCPT model. These parameters can be tuned to balance:
> - **Evidence Coverage (Recall)**: Higher candidate pools increase the likelihood of capturing highly relevant clinical studies for obscure or multi-faceted claims.
> - **Ranking Quality (Precision)**: MedCPT Cross-Encoder reranking ensures the most semantically and clinically relevant evidence rises to the top 10.
> - **Processing Latency (Speed)**: Cross-encoder scoring and PubMed XML fetching scale with candidate count; capping at 50–100 ensures responsive end-to-end execution on standard hardware.

### 3. Natural Language Inference (NLI) & Decision Engine
- **NLI Classification**: The top evidence candidates from each source are evaluated by `cross-encoder/nli-deberta-v3-base` to determine if each evidence passage **entails**, **contradicts**, or is **neutral** toward the user's claim.
- **Decision Engine**: Applies heuristic confidence thresholds (`MIN_CONFIDENCE = 0.70`, `MIN_MARGIN = 0.15`) and rule-based aggregation over the classified evidence to produce the final verdict:
  - `Potentially supported`
  - `Potentially refuted`
  - `Mixed evidence`
  - `Insufficient evidence`

---

## Evaluation Architecture

The system evaluates verification performance across two distinct tiers:

1. **Level 1: NLI Classifier**
   - Measures the accuracy of the Natural Language Inference model (`cross-encoder/nli-deberta-v3-base`) in classifying the relationship between evidence premises and claims.
   - Target Classes: `entailment`, `contradiction`, `neutral`.

2. **Level 2: Final Decision Engine**
   - Measures the rule-based aggregation engine that synthesizes individual NLI predictions into a preliminary claim assessment.
   - Target Classes: `Potentially supported`, `Potentially refuted`, `Mixed evidence`, `Insufficient evidence`.

### Evaluated Metrics
- **Accuracy**: Overall fraction of correct predictions.
- **Precision (Macro & Weighted)**: Measure of false-positive rate across classes. Weighted precision accounts for class imbalance based on support.
- **Recall (Macro & Weighted)**: Measure of coverage / false-negative rate across classes.
- **F1-Score (Macro & Weighted)**: Harmonic mean of precision and recall.
- **Confusion Matrix & Per-Class Breakdown**: Detailed diagnostic tables showing true vs. predicted counts and per-class performance.

---

## Running the Evaluation

### 1. View Metrics in the Interactive Streamlit UI
Run the web application:
```bash
streamlit run app.py
```
1. Open the sidebar navigation.
2. Select **"Evaluation Metrics"**.
3. View the KPI metric cards, per-class breakdowns, confusion matrices, and sample-by-sample predictions for both Level 1 (NLI) and Level 2 (Decision Engine).

### 2. View Metrics via CLI
To quickly view the evaluation report from existing predictions:
```bash
python evaluation_metrics.py
```

### 3. Run Predictions on a Test Dataset
To run model inference and re-evaluate on a test dataset:
```bash
# Evaluate on the 10-sample benchmark dataset:
python evaluate_real_model.py evaluation_dataset_10.csv

# Evaluate on the full 50-sample dataset:
python evaluate_real_model.py evaluation_dataset.csv
```
This generates an updated `evaluation_predictions.csv` with predictions and confidence scores.

### 4. Run the Automated Test Suite
To verify mathematical calculation correctness and edge-case handling:
```bash
python test_evaluation.py
```

---

## Dataset Format

Evaluation datasets (`evaluation_dataset.csv`, `evaluation_dataset_10.csv`) must contain the following columns:

| Column | Description | Supported Values |
| :--- | :--- | :--- |
| `claim` | Health statement or claim | Text string |
| `evidence` | Retrieved snippet or scientific abstract | Text string |
| `true_nli_label` | Ground-truth NLI relationship | `entailment`, `contradiction`, `neutral` |
| `true_verdict` | Ground-truth overall verdict | `supported`, `refuted`, `insufficient` |
