import numpy as np
from app.services.vector_store import VectorStore
from app.config import settings

def main():
    vs = VectorStore(settings.QDRANT_STORAGE_PATH)
    
    # Fetch points for upload_log_id = 7
    res7 = vs.client.scroll(
        collection_name="face_embeddings",
        scroll_filter={
            "must": [
                {"key": "upload_log_id", "match": {"value": 7}}
            ]
        },
        with_vectors=True,
        limit=100
    )
    pts7 = res7[0]
    
    # Fetch points for upload_log_id = 8
    res8 = vs.client.scroll(
        collection_name="face_embeddings",
        scroll_filter={
            "must": [
                {"key": "upload_log_id", "match": {"value": 8}}
            ]
        },
        with_vectors=True,
        limit=100
    )
    pts8 = res8[0]
    
    print(f"Upload 7: {len(pts7)} faces found.")
    print(f"Upload 8: {len(pts8)} faces found.")
    
    matches = []
    for p7 in pts7:
        for p8 in pts8:
            vec7 = np.array(p7.vector)
            vec8 = np.array(p8.vector)
            sim = float(np.dot(vec7, vec8))
            matches.append((sim, p7.id, p8.id, p7.payload.get("face_index"), p8.payload.get("face_index")))
            
    matches.sort(reverse=True)
    print("\nTop 10 pairwise matches:")
    for sim, id7, id8, idx7, idx8 in matches[:10]:
        print(f"Similarity: {sim:.4f} | Point {id7} (idx {idx7}) vs Point {id8} (idx {idx8})")

if __name__ == "__main__":
    main()
