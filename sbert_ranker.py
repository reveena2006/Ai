
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 16


def rank_factchecks(user_claim, records):
    """Rank Google Fact Check API records by cosine similarity."""

    if not isinstance(user_claim, str) or not user_claim.strip():
        print("Cannot rank fact-checks: the user claim is empty.")
        return []

    if not isinstance(records, list) or not records:
        print("No fact-check records were provided.")
        return []

    usable_records = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        claim_text = record.get("text", "")

        if isinstance(claim_text, str) and claim_text.strip():
            usable_records.append({
                "original_index": index,
                "record": record,
                "claim_text": claim_text.strip(),
            })

    if not usable_records:
        print("No fact-check records with valid claim text were found.")
        return []

    print(f"\nLoading SBERT model: {MODEL_NAME}")

    # Explicit CPU use helps avoid GPU-related deployment issues.
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    query_embedding = model.encode(
        user_claim.strip(),
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    texts = [item["claim_text"] for item in usable_records]

    # Batch encoding helps control memory usage.
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    scores = np.dot(embeddings, query_embedding)
    sorted_indices = np.argsort(scores)[::-1]

    results = []

    for rank, position in enumerate(sorted_indices, start=1):
        item = usable_records[int(position)]
        record = item["record"]

        results.append({
            "rank": rank,
            "original_index": item["original_index"],
            "similarity_score": round(float(scores[position]), 4),
            "claim_text": item["claim_text"],
            "claim_reviews": record.get("claimReview", []),
            "original_record": record,
        })

    print(f"Successfully ranked {len(results)} fact-check records.")
    return results
