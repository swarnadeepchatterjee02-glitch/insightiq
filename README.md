# 🧠 InsightIQ — AI-Powered Business Intelligence Platform

> Upload any dataset → Ask questions in plain English → Get instant business insights

[![Live App](https://img.shields.io/badge/🚀_Live_App-Hugging_Face-yellow)](https://huggingface.co/spaces/s0chat12/insightiq)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/LLM-Groq_LLaMA_3.3_70B-green)](https://groq.com)

---

## 🔗 Live Demo

👉 **[https://huggingface.co/spaces/s0chat12/insightiq](https://huggingface.co/spaces/s0chat12/insightiq)**

---

## 📌 What Is InsightIQ?

InsightIQ is a fully deployed, AI-powered Business Intelligence web application built with Python and Streamlit. It allows anyone — technical or not — to upload a CSV or Excel dataset and instantly get:

- AI-generated answers to business questions in plain English
- Automated charts and visualizations
- Proactively surfaced trends, risks, and opportunities
- What-If scenario simulations
- One-click professional PDF consulting reports

No SQL. No code. No dashboards to build from scratch.

---

## ✨ Features

| Page | Description |
|------|-------------|
| 🏠 **Home** | Upload CSV/Excel or launch with built-in Superstore demo dataset |
| 💬 **Ask AI** | Multi-turn conversational Q&A with auto-generated Plotly charts |
| 🎯 **Auto Insights** | AI surfaces top trends, risks, and opportunities from your data |
| 📊 **Charts** | Auto-generated overview dashboard based on your dataset |
| 🔮 **What If?** | Natural language business scenario simulator |
| 📄 **Export Report** | One-click professional PDF report with KPIs, insights, and performers |

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Frontend / UI | Streamlit |
| AI / LLM | Groq API — LLaMA 3.3 70B Versatile |
| Data Processing | Pandas, NumPy |
| Visualizations | Plotly |
| PDF Generation | FPDF2 |
| Deployment | Hugging Face Spaces (Docker) |
| Language | Python 3.13 |

---

## 📁 Project Structure

```
insightiq/
├── app.py                  # Main Streamlit app & page router
├── config.py               # App settings and API key config
├── requirements.txt        # Python dependencies
├── modules/
│   ├── data_processor.py   # File upload, cleaning, KPI detection
│   ├── llm_engine.py       # Groq API — Q&A, insights, what-if
│   ├── visualizer.py       # Smart auto-chart generation
│   ├── insight_generator.py# Growth analysis, top/bottom performers
│   ├── report_generator.py # PDF report generation
│   └── anomaly_detector.py # IQR-based outlier detection
└── sample_data/
    └── superstore_cleaned.csv  # Built-in demo dataset (9,994 rows)
```

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/swarnadeepchatterjee02-glitch/insightiq.git
cd insightiq
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Groq API key**

Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com)

**4. Run the app**
```bash
streamlit run app.py
```

---

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (required for AI features) |

---

## 📊 Demo Dataset

The app includes a built-in **Superstore Sales dataset** (9,994 rows) covering sales, profit, region, category, and customer data from 2014–2017. Click **Launch Demo** on the home page to use it instantly.

---

## 👤 Author

**Swarnadeep Chatterjee**
- GitHub: [@swarnadeepchatterjee02-glitch](https://github.com/swarnadeepchatterjee02-glitch)
- Email: swarnadeepchatterjee19@gmail.com

---

*Built with Python + Groq AI | April 2026*
