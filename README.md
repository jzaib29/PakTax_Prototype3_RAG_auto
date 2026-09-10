# Pakistan Tax Navigator

A Streamlit MVP that helps salaried individuals, freelancers, IT/software exporters and small businesses navigate Pakistan tax-compliance questions.

## Architecture

- `app.py` — main Streamlit workflow and progressive UI
- `data_collection.py` — Step 1/2 segmentation and profile collection
- `processing.py` — RAG query workflow, LLM prompting and confidence scoring
- `rag_engine.py` — local document parsing, chunking, embeddings and FAISS retrieval
- `internet_search.py` — optional current-web fallback using Gemini Google Search grounding
- `ui.py` — styling and reusable UI components
- `ingest.py` — owner-only RAG indexing utility
- `config.py` — configuration, paths, model and thresholds
- `knowledge_base/` — owner-managed source documents only; no public upload feature
- `vectorstore/` — generated FAISS index and metadata; commit these generated files for Streamlit Cloud so the app does not need to rebuild the index on every deployment

## Local setup

1. Create a Python 3.10+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your owner-managed FBR/Pakistan source documents to `knowledge_base/`.
4. Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key-here"
```

Never commit this file.

5. Build the index:

```bash
python ingest.py
```

6. Start the app:

```bash
streamlit run app.py
```

## GitHub / Streamlit Community Cloud

Commit the Python files, owner-managed `knowledge_base/`, and generated `vectorstore/` index. If the index becomes large later, move it to external storage rather than rebuilding it for every app session. Keep `.streamlit/secrets.toml` out of GitHub and add the secret in the deployed app's Secrets settings.

## Important product rule

The RAG knowledge base is intentionally not user-editable from the front end. Only the application owner updates source documents and rebuilds the index.

### Important: build the RAG index before running Streamlit
The app reads `vectorstore/index.faiss` and `vectorstore/metadata.json`. They are not created automatically when a document is copied into `knowledge_base/`.

Run from the project folder:

```bash
pip install -r requirements.txt
python ingest.py
streamlit run app.py
```

For scanned/image-only PDFs, normal PDF text extraction may return zero characters. Convert the PDF to a searchable PDF or provide a text/DOCX version. The current sample project also contains an OCR text companion for the supplied `Filing Tax Return Declaration.pdf`.


## Streamlit Community Cloud deployment

No local Python installation is required for deployment. Commit `app.py`, the Python modules, `requirements.txt`, and your owner-managed `knowledge_base/` to GitHub. On first startup, the app automatically builds the FAISS index in the Streamlit runtime when `vectorstore/index.faiss` and `vectorstore/metadata.json` are missing. End users cannot upload or modify knowledge-base files through the UI.

Add `GEMINI_API_KEY` in Streamlit Community Cloud -> App settings -> Secrets. Never commit `secrets.toml`.

`ingest.py` remains available as an owner/development utility, but it is not required for normal Streamlit Cloud deployment.
