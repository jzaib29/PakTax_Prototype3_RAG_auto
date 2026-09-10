"""Owner-side RAG ingestion and retrieval using local embeddings + FAISS."""
from pathlib import Path
import json
from functools import lru_cache
from typing import List, Dict, Any, Tuple

import faiss
import numpy as np
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer

SUPPORTED = {".pdf", ".txt", ".md", ".docx"}
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


@lru_cache(maxsize=1)
def _get_model(model_name: str):
    return SentenceTransformer(model_name)


def _read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if path.suffix.lower() == ".docx":
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    return path.read_text(encoding="utf-8", errors="ignore")


def _chunk_text(text: str) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks


def build_index(knowledge_dir: str, output_dir: str, model_name: str) -> Dict[str, Any]:
    kb = Path(knowledge_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    documents: List[Dict[str, Any]] = []
    for path in sorted(kb.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            text = _read_file(path)
            for i, chunk in enumerate(_chunk_text(text)):
                documents.append({"text": chunk, "source": path.name, "chunk": i})

    if not documents:
        raise RuntimeError("No supported files found in knowledge_base/. Add PDFs/DOCX/TXT/MD first.")

    model = _get_model(model_name)
    matrix = model.encode(
        [d["text"] for d in documents],
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    matrix = np.asarray(matrix, dtype="float32")
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)

    faiss.write_index(index, str(out / "index.faiss"))
    (out / "metadata.json").write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"documents": len(documents), "dimension": matrix.shape[1]}


def retrieve(query: str, vectorstore_dir: str, model_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
    out = Path(vectorstore_dir)
    index_path = out / "index.faiss"
    meta_path = out / "metadata.json"
    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError("RAG index is not available. The app should build it automatically from knowledge_base/.")

    model = _get_model(model_name)
    index = faiss.read_index(str(index_path))
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    vector = model.encode([query], normalize_embeddings=True)
    scores, ids = index.search(np.asarray(vector, dtype="float32"), min(top_k, len(metadata)))

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue
        item = dict(metadata[idx])
        item["score"] = float(score)
        results.append(item)
    return results
