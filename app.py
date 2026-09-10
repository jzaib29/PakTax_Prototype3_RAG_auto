"""Main Streamlit application."""
import streamlit as st

from config import MAX_QUERY_CHARS, CONFIDENCE_THRESHOLD, KNOWLEDGE_BASE_DIR, VECTORSTORE_DIR, EMBEDDING_MODEL
from data_collection import init_state, collect_profile, profile_summary, ACTIONS
from processing import ask_rag, expand_answer
from rag_engine import build_index
from internet_search import search_web
from ui import apply_theme, hero, confidence_badge

apply_theme()
init_state()
hero()

# Build the owner-managed RAG index automatically on first cloud startup.
# End users are never given an upload control for the knowledge base.
if not (VECTORSTORE_DIR / "index.faiss").exists() or not (VECTORSTORE_DIR / "metadata.json").exists():
    with st.spinner("Preparing the verified tax knowledge base for the first use…"):
        try:
            stats = build_index(str(KNOWLEDGE_BASE_DIR), str(VECTORSTORE_DIR), EMBEDDING_MODEL)
            st.session_state["index_ready_message"] = f"Knowledge base ready: {stats["documents"]} chunks indexed."
        except Exception as exc:
            st.error(f"Could not prepare the RAG knowledge base: {exc}")
            st.stop()

if st.session_state.get("index_ready_message"):
    st.caption(st.session_state["index_ready_message"])

st.markdown("### How it works")
st.caption("1) Your situation → 2) Context → 3) Tax action → verified RAG answer → optional Internet verification")

if st.session_state.step < 3:
    collect_profile()
    st.stop()

profile = profile_summary()
with st.expander("Your selected profile", expanded=False):
    st.json(profile)

st.subheader("Step 3 — Choose an action")
tab1, tab2, tab3 = st.tabs(["Ask Tax Question", "Compliance Checklist", "More Info"])

with tab1:
    st.write("Ask one focused question. Keep it within 200 characters to control API usage.")
    action = st.selectbox("Start with a common question", ["Custom question"] + ACTIONS, key="action_select")
    default_q = "" if action == "Custom question" else action
    query = st.text_area("Your question", value=default_q, max_chars=MAX_QUERY_CHARS, height=90, key="main_query")
    st.caption(f"{len(query)}/{MAX_QUERY_CHARS} characters")

    if st.button("Get Answer", type="primary", use_container_width=True, key="ask_button"):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching verified knowledge base…"):
                try:
                    st.session_state.rag_result = ask_rag(query, profile)
                    st.session_state.query = query
                    st.session_state.web_result = None
                except Exception as exc:
                    st.error(str(exc))

    result = st.session_state.get("rag_result")
    if result:
        st.markdown(f"**RAG confidence:** {confidence_badge(result['confidence'])} ({result['confidence']:.2f})")
        st.info(result["answer"])
        if result.get("results"):
            with st.expander("Verified sources used by RAG"):
                for r in result["results"]:
                    st.write(f"**{r['source']}** — similarity {r['score']:.2f}")
        if result.get("needs_web"):
            st.warning("The confidence is low. An authentic answer could not be established from the verified knowledge base.")
            if st.button("Search the Internet for this same query", key="web_button"):
                with st.spinner("Searching current public sources…"):
                    try:
                        st.session_state.web_result = search_web(st.session_state.query, profile)
                    except Exception as exc:
                        st.error(str(exc))

        web_result = st.session_state.get("web_result")
        if web_result:
            st.success("Internet-grounded answer")
            st.write(web_result["answer"])
            if web_result.get("sources"):
                with st.expander("Web sources"):
                    for source in web_result["sources"]:
                        title = source.get("title") or source.get("uri") or "Source"
                        uri = source.get("uri")
                        if uri:
                            st.markdown(f"- [{title}]({uri})")
                        else:
                            st.write(f"- {title}")

with tab2:
    st.markdown("#### Personalized compliance checklist")
    st.write("Use this as a navigation aid; it does not confirm your legal/tax liability.")
    checklist = [
        "Confirm your taxpayer category and income sources",
        "Check whether FBR registration/NTN may apply",
        "Collect income and payment records",
        "Collect withholding / bank / supporting documents",
        "Check current filing requirements for the relevant tax year",
        "Verify any time-sensitive rule against current official sources",
    ]
    for item in checklist:
        st.checkbox(item, key=f"check_{item}")

with tab3:
    st.write("The short answer is shown first. Request a longer explanation only when you need it.")
    more_query = st.text_input("Question to explain further", value=st.session_state.get("query", ""), max_chars=MAX_QUERY_CHARS, key="more_query")
    if st.button("More Info", use_container_width=True, key="more_button"):
        if not more_query.strip():
            st.warning("Ask a question first.")
        else:
            with st.spinner("Retrieving more detail from the verified knowledge base…"):
                try:
                    detail = expand_answer(more_query, profile)
                    st.write(detail["answer"])
                    st.caption(f"RAG confidence: {detail['confidence']:.2f}")
                    if detail.get("results"):
                        with st.expander("Sources"):
                            for r in detail["results"]:
                                st.write(f"{r['source']} — similarity {r['score']:.2f}")
                except Exception as exc:
                    st.error(str(exc))

st.divider()
st.caption("Prototype only. Do not submit confidential personal documents or rely on this app as a substitute for a qualified tax professional. The app is designed to use owner-managed knowledge-base files and does not expose an upload control to end users.")
