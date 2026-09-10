"""Central configuration for Pakistan Tax Navigator."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# Current stable, free-tier-friendly Gemini model for this MVP.
LLM_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K = 5
CONFIDENCE_THRESHOLD = 0.62
MAX_QUERY_CHARS = 200
MAX_HISTORY_ITEMS = 6


def get_gemini_api_key() -> str:
    """Read API key from Streamlit secrets or environment variables."""
    key = os.getenv("GEMINI_API_KEY", "")
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", key) or key
    except Exception:
        pass
    return key
