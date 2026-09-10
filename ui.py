"""Reusable Streamlit UI styling/components."""
import streamlit as st


def apply_theme() -> None:
    st.set_page_config(page_title="Pakistan Tax Navigator", page_icon="🇵🇰", layout="wide")
    st.markdown(
        """
        <style>
        .main { background: #f7f9fc; }
        .block-container { max-width: 1100px; padding-top: 2rem; }
        .hero { padding: 1.0rem 1.2rem; border-radius: 16px; background: #0b3d5c; color: white; margin-bottom: 1rem; }
        .hero h1 { margin: 0; font-size: 2.0rem; }
        .hero p { margin: .3rem 0 0; opacity: .9; }
        .card { padding: 1rem; border-radius: 14px; border: 1px solid #dfe6ee; background: white; margin-bottom: .7rem; }
        .small { color: #667085; font-size: .88rem; }
        .confidence { font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>🇵🇰 Pakistan Tax Navigator</h1>
          <p>Understand your possible tax-compliance path using verified sources first.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def confidence_badge(score: float) -> str:
    if score >= 0.80:
        return "🟢 High"
    if score >= 0.62:
        return "🟡 Medium"
    return "🔴 Low"
