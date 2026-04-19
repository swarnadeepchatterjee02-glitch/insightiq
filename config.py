import os
try:
    import streamlit as st
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = "llama-3.3-70b-versatile"
APP_NAME = "InsightIQ"
APP_TAGLINE = "AI-Powered Business Intelligence"
APP_VERSION = "1.0.0"
MAX_FILE_SIZE_MB = 50
SUPPORTED_FORMATS = [".csv", ".xlsx"]
SAMPLE_DATA_PATH = "sample_data/superstore_cleaned.csv"
MAX_TOKENS = 1500
TEMPERATURE = 0.3
CHART_THEME = "plotly_dark"
MAX_CHART_ROWS = 50