# ui.py

import streamlit as st
import json
from agent import run_agent

st.set_page_config(page_title="Clinical Workflow Agent", layout="centered")

st.title("🩺 Clinical Workflow Automation Agent")
st.write("Enter a clinical or administrative request below.")

user_input = st.text_area(
    "Request",
    placeholder="e.g. Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"
)

if st.button("Run Agent"):
    if not user_input.strip():
        st.warning("Please enter a request.")
    else:
        with st.spinner("Processing..."):
            try:
                result = run_agent(user_input)
                st.success("Agent executed successfully")

                st.subheader("📄 Structured Output")
                st.json(result)

            except Exception as e:
                st.error(f"Error: {str(e)}")
