"""LLM + RAG processing workflow."""
from typing import Dict, Any, List
from google import genai
from google.genai import types

from config import (
    LLM_MODEL,
    EMBEDDING_MODEL,
    VECTORSTORE_DIR,
    TOP_K,
    CONFIDENCE_THRESHOLD,
    MAX_QUERY_CHARS,
    get_gemini_api_key,
)
from rag_engine import retrieve

SYSTEM_PROMPT = """
You are Pakistan Tax Navigator, an information assistant for Pakistani tax-compliance guidance.
Use ONLY the supplied retrieved evidence for tax-specific claims.
Do not invent rules, rates, deadlines, exemptions, filing requirements, or legal conclusions.
The answer is informational, not professional tax/legal advice.
For the normal answer, use no more than 3 short lines.
When evidence is insufficient, say that authentic information could not be established from the verified knowledge base.
Always mention the most relevant source filename(s) when evidence supports an answer.
""".strip()


def _client() -> genai.Client:
    key = get_gemini_api_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to Streamlit Secrets.")
    return genai.Client(api_key=key)


def _profile_text(profile: Dict[str, Any]) -> str:
    parts = [f"{k}: {v}" for k, v in profile.items() if v not in (None, "", [], {})]
    return " | ".join(parts)


def _confidence(results: List[Dict[str, Any]]) -> float:
    if not results:
        return 0.0
    # Practical hybrid score: top semantic similarity + support from multiple chunks.
    top = max(r["score"] for r in results)
    second = sorted([r["score"] for r in results], reverse=True)[1] if len(results) > 1 else top
    support = min(1.0, len([r for r in results if r["score"] >= 0.45]) / 3.0)
    raw = (0.60 * max(0.0, min(1.0, top)) + 0.20 * max(0.0, min(1.0, second)) + 0.20 * support)
    return round(raw, 2)


def ask_rag(question: str, profile: Dict[str, Any], more_info: bool = False) -> Dict[str, Any]:
    question = question.strip()
    if len(question) > MAX_QUERY_CHARS:
        raise ValueError(f"Question must be {MAX_QUERY_CHARS} characters or fewer.")
    results = retrieve(question, str(VECTORSTORE_DIR), EMBEDDING_MODEL, TOP_K)
    confidence = _confidence(results)

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "answer": "An authentic answer could not be established from the verified knowledge base.",
            "confidence": confidence,
            "results": results,
            "needs_web": True,
        }

    evidence = "\n\n".join(
        f"SOURCE: {r['source']}\nEVIDENCE: {r['text']}" for r in results
    )
    length_instruction = (
        "Provide 1–2 concise paragraphs with a little more explanation." if more_info
        else "Provide no more than 3 short lines."
    )
    prompt = f"""
{SYSTEM_PROMPT}

USER PROFILE:
{_profile_text(profile)}

QUESTION:
{question}

RETRIEVED VERIFIED EVIDENCE:
{evidence}

{length_instruction}
"""
    response = _client().models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=300 if more_info else 120),
    )
    return {
        "answer": (response.text or "No answer generated.").strip(),
        "confidence": confidence,
        "results": results,
        "needs_web": confidence < CONFIDENCE_THRESHOLD,
    }


def expand_answer(question: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    return ask_rag(question, profile, more_info=True)
