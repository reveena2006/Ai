
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def rank_factchecks(user_claim, records):
    """Rank fact-check records by cosine similarity to the user claim."""

    usable_records = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        claim_text = record.get("text", "")

        if isinstance(claim_text, str) and claim_text.strip():
            usable_records.append({
                "original_index": index,
                "record": record,
                "claim_text": claim_text.strip()
            })

    if not usable_records:
        print("No fact-check records with claim text to rank.")
        return []

    print(f"\nLoading SBERT model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # Encode the original user claim.
    query_embedding = model.encode(
        user_claim,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Encode every retrieved fact-check claim.
    texts = [
        item["claim_text"] for item in usable_records
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # For normalized embeddings, dot product equals cosine similarity.
    scores = np.dot(embeddings, query_embedding)

    # Sort from highest similarity to lowest.
    sorted_indices = np.argsort(scores)[::-1]

    results = []

    for rank, position in enumerate(sorted_indices, start=1):
        item = usable_records[int(position)]
        record = item["record"]

        results.append({
            "rank": rank,
            "original_index": item["original_index"],
            "similarity_score": round(
                float(scores[position]), 4
            ),
            "claim_text": item["claim_text"],
            "claim_reviews": record.get("claimReview", []),
            "original_record": record
        })

    return results
