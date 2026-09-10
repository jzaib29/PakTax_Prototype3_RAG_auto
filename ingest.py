"""OWNER-ONLY utility: build/rebuild the RAG index from knowledge_base/."""
from config import KNOWLEDGE_BASE_DIR, VECTORSTORE_DIR, EMBEDDING_MODEL
from rag_engine import build_index

if __name__ == "__main__":
    stats = build_index(str(KNOWLEDGE_BASE_DIR), str(VECTORSTORE_DIR), EMBEDDING_MODEL)
    print(f"Indexed {stats['documents']} chunks; embedding dimension={stats['dimension']}")
