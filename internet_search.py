"""Optional Internet fallback using Gemini's built-in Google Search grounding."""
from typing import Dict, Any
from google import genai
from google.genai import types

from config import LLM_MODEL, MAX_QUERY_CHARS, get_gemini_api_key


def search_web(question: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    question = question.strip()
    if len(question) > MAX_QUERY_CHARS:
        raise ValueError(f"Question must be {MAX_QUERY_CHARS} characters or fewer.")
    key = get_gemini_api_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to Streamlit Secrets.")

    client = genai.Client(api_key=key)
    prompt = f"""
You are a Pakistan tax information assistant.
The verified internal knowledge base did not provide sufficient evidence.
Search the current public web, prioritizing authoritative Pakistan sources such as FBR and official government websites.
Do not invent tax rules or imply professional legal/tax advice.
Answer the user's question in no more than 3 short lines and clearly say when evidence is uncertain.
User profile: {profile}
Question: {question}
"""
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.1,
            max_output_tokens=180,
        ),
    )

    sources = []
    try:
        metadata = response.candidates[0].grounding_metadata
        if metadata and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                web = getattr(chunk, "web", None)
                if web:
                    sources.append({"title": getattr(web, "title", ""), "uri": getattr(web, "uri", "")})
    except Exception:
        pass

    return {"answer": (response.text or "No web answer generated.").strip(), "sources": sources}
