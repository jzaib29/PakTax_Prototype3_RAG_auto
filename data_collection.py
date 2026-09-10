"""Step 1 and Step 2 user data collection."""
from typing import Dict, Any
import streamlit as st

SEGMENTS = [
    "Salaried Individual",
    "Freelancer",
    "IT / Software Exporter",
    "Small Business / Home Business",
    "Online Seller",
    "Multiple Income Sources",
]

ACTIONS = [
    "Do I need to register with FBR?",
    "Do I need to file a tax return?",
    "What documents do I need?",
    "Understand withholding tax",
    "Understand IT/export income rules",
    "Understand my next steps",
]


def init_state() -> None:
    defaults = {
        "step": 1,
        "profile": {},
        "query": "",
        "rag_result": None,
        "web_result": None,
        "show_more": False,
        "run_query": False,
        "run_more_info": False,
        "run_web_search": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def collect_profile() -> bool:
    """Render progressive profile collection. Returns True when saved."""
    st.subheader("Step 1 — Tell us about you")
    segment = st.selectbox("Your situation", SEGMENTS, key="segment_input")

    st.subheader("Step 2 — A little more context")
    if segment == "Salaried Individual":
        income_type = st.multiselect(
            "Income sources",
            ["Salary", "Bank profit / investment", "Rental income", "Other"],
            key="income_type",
        )
        employer = st.selectbox("Employment type", ["Private", "Government", "Other"], key="employer")
        foreign_income = st.selectbox("Do you receive foreign income?", ["No", "Yes", "Not sure"], key="foreign_income")
        extra = {"income_sources": income_type, "employment_type": employer, "foreign_income": foreign_income}
    elif segment == "Freelancer":
        services = st.text_input("Main freelance service", max_chars=80, key="services")
        payment = st.selectbox("How do you usually receive payments?", ["Local bank", "Foreign currency / remittance", "Platform (e.g. Upwork)", "Other / Not sure"], key="payment")
        foreign_income = st.selectbox("Do you receive income from clients outside Pakistan?", ["No", "Yes", "Not sure"], key="foreign_income")
        extra = {"service": services, "payment_method": payment, "foreign_income": foreign_income}
    elif segment == "IT / Software Exporter":
        entity = st.selectbox("How do you operate?", ["Individual", "Sole proprietor", "Company", "Not sure"], key="entity")
        export_channel = st.selectbox("How are services sold/exported?", ["Direct foreign clients", "Platform", "Through another company", "Other / Not sure"], key="export_channel")
        foreign_income = "Yes"
        extra = {"entity_type": entity, "export_channel": export_channel, "foreign_income": foreign_income}
    elif segment == "Small Business / Home Business":
        business_type = st.text_input("What do you sell/provide?", max_chars=80, key="business_type")
        channel = st.selectbox("Main sales channel", ["Physical shop", "Home-based", "Online", "Mixed"], key="channel")
        registration = st.selectbox("Already registered with FBR?", ["No", "Yes", "Not sure"], key="registration")
        extra = {"business_type": business_type, "channel": channel, "fbr_registration": registration}
    elif segment == "Online Seller":
        product = st.text_input("What do you mainly sell?", max_chars=80, key="product")
        channel = st.selectbox("Sales channel", ["Social media", "Marketplace", "Own website", "Mixed"], key="channel")
        delivery = st.selectbox("Delivery / payment model", ["Cash on delivery", "Online payment", "Mixed", "Other"], key="delivery")
        extra = {"product": product, "sales_channel": channel, "payment_model": delivery}
    else:
        sources = st.multiselect("Income sources", ["Salary", "Freelancing", "Business", "Rental", "Investments", "Other"], key="multi_income")
        foreign_income = st.selectbox("Do you receive foreign income?", ["No", "Yes", "Not sure"], key="foreign_income")
        registration = st.selectbox("Current FBR registration", ["Registered", "Not registered", "Not sure"], key="registration")
        extra = {"income_sources": sources, "foreign_income": foreign_income, "fbr_registration": registration}

    if st.button("Continue to Step 3", type="primary", use_container_width=True):
        st.session_state.profile = {"segment": segment, **extra}
        st.session_state.step = 3
        st.rerun()
    return False


def  profile_summary() -> Dict[str, Any]:
    return st.session_state.get("profile", {})
