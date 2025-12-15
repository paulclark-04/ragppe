from typing import List
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np
import faiss

# Initialize models
embed_model = SentenceTransformer('BAAI/bge-base-en-v1.5')

class RAGService:
    def __init__(self):
        self.chunks = []
        self.index = None # FAISS index
        self.bm25 = None
        self.tokenized_chunks = []

    def chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
        """Simple chunking strategy."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def index_document(self, text: str):
        """Index document using FAISS and BGE."""
        self.chunks = self.chunk_text(text)
        print(f"Indexed document. Total chunks: {len(self.chunks)}")
        
        # ONE-TIME Index Build (simplification for single doc)
        # Dense Embedding (BGE)
        embeddings = embed_model.encode(self.chunks, normalize_embeddings=True)
        dimension = embeddings.shape[1]
        
        # FAISS Index
        self.index = faiss.IndexFlatIP(dimension) # Inner Product for normalized vectors = Cosine Similarity
        self.index.add(embeddings)
        
        # Sparse Embedding (BM25)
        self.tokenized_chunks = [chunk.split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_chunks)

    def retrieve(self, query: str, top_k: int = 5) -> List[tuple[str, float]]:
        """Hybrid retrieval with FAISS and BM25 (75/25 split). Returns (chunk, score) tuples."""
        if not self.chunks:
            return []

        # --- Dense Search (FAISS) ---
        query_embedding = embed_model.encode([query], normalize_embeddings=True)
        # Search all to get scores for normalization
        D, I = self.index.search(query_embedding, len(self.chunks))
        
        # FAISS returns sorted results, we need to map them back to original indices for combination
        # Create a dense score array aligned with self.chunks
        dense_scores_all = np.zeros(len(self.chunks))
        for score, idx in zip(D[0], I[0]):
            dense_scores_all[idx] = score
            
        # --- Sparse Search (BM25) ---
        tokenized_query = query.split()
        sparse_scores_all = np.array(self.bm25.get_scores(tokenized_query))
        
        # --- Normalization ---
        def normalize(scores):
            if scores.max() == scores.min():
                return scores
            return (scores - scores.min()) / (scores.max() - scores.min())

        norm_dense = normalize(dense_scores_all)
        norm_sparse = normalize(sparse_scores_all)
        
        # --- Hybrid Combination (75% Dense, 25% Sparse) ---
        hybrid_scores = 0.75 * norm_dense + 0.25 * norm_sparse
        
        # --- Top-K Selection ---
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
        
        results = []
        print(f"Query: {query}")
        print(f"Retrieved {len(top_indices)} candidates (showing top {top_k}).")
        
        for i, idx in enumerate(top_indices):
            score = hybrid_scores[idx]
            chunk = self.chunks[idx]
            if i < top_k:
                print(f"Rank {i+1}: Hybrid={score:.4f} (Dense={norm_dense[idx]:.4f}, Sparse={norm_sparse[idx]:.4f})")
                results.append((chunk, float(score)))
            
        return results

rag_service = RAGService()
