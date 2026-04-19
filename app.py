import streamlit as st
import pandas as pd
import time
from config import APP_NAME, APP_TAGLINE, APP_VERSION
from modules.data_processor import DataProcessor
from modules.llm_engine import LLMEngine
from modules.visualizer import Visualizer
from modules.insight_generator import InsightGenerator
from modules.report_generator import ReportGenerator
from modules.anomaly_detector import AnomalyDetector

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="InsightIQ — AI Business Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3250;
    }
    .kpi-card {
        background: #1a1d27;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 4px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #4F8EF7;
        margin: 8px 0;
    }
    .kpi-label {
        font-size: 11px;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .user-message {
        background: #1a1d27;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    .ai-message {
        background: #22263a;
        border: 1px solid #4F8EF7;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4F8EF7, #7c3aed);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
    }
    .insight-box {
        background: #1a1d27;
        border-left: 4px solid #4F8EF7;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin: 8px 0;
    }
    .risk-box {
        background: #1a1d27;
        border-left: 4px solid #ef4444;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin: 8px 0;
    }
    .opportunity-box {
        background: #1a1d27;
        border-left: 4px solid #22c55e;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin: 8px 0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────
def init_session_state():
    if 'dp' not in st.session_state:
        st.session_state.dp = DataProcessor()
    if 'llm' not in st.session_state:
        st.session_state.llm = LLMEngine()
    if 'viz' not in st.session_state:
        st.session_state.viz = Visualizer()
    if 'ig' not in st.session_state:
        st.session_state.ig = InsightGenerator()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'last_question' not in st.session_state:
        st.session_state.last_question = None
    if 'last_answer' not in st.session_state:
        st.session_state.last_answer = None

init_session_state()

# ── SIDEBAR ────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding: 20px 0;'>
            <div style='font-size:40px'>🧠</div>
            <div style='font-size:22px; font-weight:700;
                background: linear-gradient(135deg, #e8eaf6, #4F8EF7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;'>
                {APP_NAME}
            </div>
            <div style='font-size:11px; color:#8892b0; margin-top:4px'>
                {APP_TAGLINE}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**NAVIGATION**")

        pages = {
            'home': '🏠 Home',
            'analyze': '💬 Ask AI',
            'insights': '🎯 Auto Insights',
            'charts': '📊 Charts',
            'whatif': '🔮 What If?',
            'report': '📄 Export Report'
        }

        for page_id, page_name in pages.items():
            if st.button(
                page_name,
                key=f"nav_{page_id}",
                use_container_width=True,
                disabled=not st.session_state.data_loaded and page_id != 'home'
            ):
                st.session_state.current_page = page_id
                st.rerun()

        st.divider()

        if st.session_state.data_loaded:
            dp = st.session_state.dp
            st.markdown(f"""
            <div style='background:#1a1d27; border:1px solid #22c55e;
                border-radius:8px; padding:12px; font-size:12px;'>
                <div style='color:#22c55e; font-weight:600'>✅ Data Loaded</div>
                <div style='color:#8892b0; margin-top:4px'>{dp.filename[:30]}</div>
                <div style='color:#8892b0'>{len(dp.df):,} rows × {len(dp.df.columns)} cols</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Load New Data", use_container_width=True):
                st.session_state.data_loaded = False
                st.session_state.chat_history = []
                st.session_state.current_page = 'home'
                st.session_state.llm.clear_history()
                st.rerun()
        else:
            st.markdown("""
            <div style='background:#1a1d27; border:1px solid #f59e0b;
                border-radius:8px; padding:12px; font-size:12px;'>
                <div style='color:#f59e0b; font-weight:600'>⚠️ No Data Loaded</div>
                <div style='color:#8892b0; margin-top:4px'>Upload or use demo data</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown(f"""
        <div style='text-align:center; font-size:10px; color:#8892b0'>
            {APP_NAME} v{APP_VERSION}<br>
            Built with Python + Groq AI
        </div>
        """, unsafe_allow_html=True)

# ── HOME PAGE ──────────────────────────────────────────────
def render_home():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px 0;'>
        <div style='font-size:56px'>🧠</div>
        <h1 style='font-size:42px; font-weight:800; margin:10px 0;
            background: linear-gradient(135deg, #e8eaf6, #4F8EF7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;'>
            InsightIQ
        </h1>
        <p style='font-size:18px; color:#8892b0; margin:0'>
            AI-Powered Business Intelligence Platform
        </p>
        <p style='font-size:14px; color:#8892b0; margin-top:8px'>
            Upload any dataset → Ask questions in plain English → Get instant business insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    ig = st.session_state.ig
    ba = ig.get_before_after()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background:#1a1d27; border:1px solid #ef4444;
            border-radius:12px; padding:20px;'>
            <div style='color:#ef4444; font-weight:700;
                font-size:16px; margin-bottom:12px'>
                ❌ Without InsightIQ
            </div>
        """, unsafe_allow_html=True)
        for item in ba['before']:
            st.markdown(f"<div style='color:#8892b0; padding:4px 0'>{item}</div>",
                unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background:#1a1d27; border:1px solid #22c55e;
            border-radius:12px; padding:20px;'>
            <div style='color:#22c55e; font-weight:700;
                font-size:16px; margin-bottom:12px'>
                ✅ With InsightIQ
            </div>
        """, unsafe_allow_html=True)
        for item in ba['after']:
            st.markdown(f"<div style='color:#e8eaf6; padding:4px 0'>{item}</div>",
                unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📂 Get Started")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style='background:#1a1d27; border:1px solid #2e3250;
            border-radius:12px; padding:20px; text-align:center;'>
            <div style='font-size:32px'>📁</div>
            <div style='font-weight:600; margin:8px 0'>Upload Your Data</div>
            <div style='color:#8892b0; font-size:13px'>CSV or Excel files supported</div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose file",
            type=['csv', 'xlsx', 'xls'],
            label_visibility="collapsed"
        )

        if uploaded_file:
            with st.spinner("Loading your data..."):
                success, msg = st.session_state.dp.load_file(uploaded_file)
                if success:
                    st.session_state.data_loaded = True
                    st.session_state.current_page = 'analyze'
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)

    with col2:
        st.markdown("""
        <div style='background:#1a1d27; border:1px solid #2e3250;
            border-radius:12px; padding:20px; text-align:center;'>
            <div style='font-size:32px'>🎮</div>
            <div style='font-weight:600; margin:8px 0'>Try Demo Dataset</div>
            <div style='color:#8892b0; font-size:13px'>
                Explore with Superstore Sales data
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Launch Demo", use_container_width=True):
            with st.spinner("Loading demo dataset..."):
                success, msg = st.session_state.dp.load_sample_data()
                if success:
                    st.session_state.data_loaded = True
                    st.session_state.current_page = 'analyze'
                    st.success("Demo loaded! Launching InsightIQ...")
                    time.sleep(1)
                    st.rerun()

# ── ANALYZE PAGE ───────────────────────────────────────────
def render_analyze():
    dp = st.session_state.dp
    llm = st.session_state.llm
    viz = st.session_state.viz

    st.markdown("## 💬 Ask InsightIQ")

    metrics = dp.get_business_metrics()
    cols = st.columns(len(metrics))
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i]:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>{key}</div>
                <div class='kpi-value'>{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔍 Explain My Data", use_container_width=True):
            with st.spinner("Analyzing your dataset..."):
                explanation = llm.explain_dataset(dp.get_ai_context())
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": explanation,
                    "type": "explain"
                })

    explanation_data = dp.get_data_explanation()
    sample_questions = explanation_data.get('sample_questions', [])

    if sample_questions:
        st.markdown("**💡 Try asking:**")
        q_cols = st.columns(len(sample_questions))
        for i, q in enumerate(sample_questions):
            with q_cols[i]:
                if st.button(q, key=f"sample_q_{i}", use_container_width=True):
                    st.session_state.pending_question = q

    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation")
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class='user-message'>
                    <strong>You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='ai-message'>
                    <strong>🧠 InsightIQ:</strong><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)

                if msg.get('chart'):
                    st.plotly_chart(msg['chart'], use_container_width=True)
                    if msg.get('chart_type'):
                        st.caption(f"📊 {msg['chart_type']}")

                    if st.button("💬 Explain this chart",
                        key=f"explain_chart_{st.session_state.chat_history.index(msg)}"):
                        with st.spinner("Analyzing chart..."):
                            chart_explanation = llm.explain_chart(
                                msg.get('chart_type', 'this chart'),
                                dp.get_ai_context()
                            )
                            st.info(chart_explanation)

                if msg.get('suggestions'):
                    st.markdown("**You might also ask:**")
                    sug_cols = st.columns(len(msg['suggestions']))
                    for i, sug in enumerate(msg['suggestions']):
                        with sug_cols[i]:
                            clean_sug = sug.lstrip('123. ')
                            if st.button(clean_sug,
                                key=f"sug_{len(st.session_state.chat_history)}_{i}"):
                                st.session_state.pending_question = clean_sug

    st.markdown("---")

    pending = st.session_state.get('pending_question', '')
    question = st.text_input(
        "Ask a business question:",
        value=pending,
        placeholder="e.g. Which region has the highest profit margin?",
        key="question_input"
    )

    if pending:
        st.session_state.pending_question = ''

    col1, col2 = st.columns([4, 1])
    with col1:
        ask_clicked = st.button("🔍 Analyze", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            llm.clear_history()
            st.rerun()

    if ask_clicked and question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.spinner("InsightIQ is analyzing..."):
            answer = llm.ask_question(question, dp.get_ai_context())
            chart, chart_type = viz.smart_chart(dp.df, question)
            suggestions = llm.get_suggested_questions(question, dp.get_ai_context())

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "chart": chart,
            "chart_type": chart_type,
            "suggestions": suggestions,
            "type": "analysis"
        })

        st.session_state.last_question = question
        st.session_state.last_answer = answer
        st.rerun()

# ── AUTO INSIGHTS PAGE ─────────────────────────────────────
def render_insights():
    dp = st.session_state.dp
    llm = st.session_state.llm
    ig = st.session_state.ig

    st.markdown("## 🎯 Auto Insights")
    st.markdown("InsightIQ proactively analyzes your data and surfaces what matters most.")

    growth = ig.get_growth_analysis(dp.df)
    if growth:
        st.markdown("### 📈 Growth Analysis")
        g_cols = st.columns(len(growth))
        for i, g in enumerate(growth):
            with g_cols[i]:
                color = "#22c55e" if g['growth_pct'] > 0 else "#ef4444"
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>{g['metric']}</div>
                    <div class='kpi-value' style='color:{color}'>
                        {g['direction']} {abs(g['growth_pct'])}%
                    </div>
                    <div style='color:#8892b0; font-size:11px'>
                        {g['from_year']} → {g['to_year']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🧠 Generate AI Insights", use_container_width=True):
        with st.spinner("InsightIQ is analyzing your entire dataset..."):
            insights = llm.generate_auto_insights(dp.get_ai_context())

        sections = insights.split('**')
        current_section = None
        content_buffer = []

        for part in sections:
            part = part.strip()
            if 'TOP 3 TRENDS' in part:
                current_section = 'trends'
            elif 'TOP 3 RISKS' in part:
                if content_buffer:
                    _render_insight_section(current_section, content_buffer)
                current_section = 'risks'
                content_buffer = []
            elif 'TOP 3 OPPORTUNITIES' in part:
                if content_buffer:
                    _render_insight_section(current_section, content_buffer)
                current_section = 'opportunities'
                content_buffer = []
            elif 'EXECUTIVE SUMMARY' in part:
                if content_buffer:
                    _render_insight_section(current_section, content_buffer)
                current_section = 'summary'
                content_buffer = []
            elif part and current_section:
                content_buffer.append(part)

        if content_buffer:
            _render_insight_section(current_section, content_buffer)

    st.markdown("---")

    performers = ig.get_top_performers(dp.df)
    if performers:
        st.markdown(f"### 🏆 Top & Bottom Performers by {performers.get('numeric_col', 'Value')}")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🟢 Top Performers**")
            for item in performers.get('top', []):
                cat = item.get(performers['cat_col'], 'Unknown')
                val = item.get(performers['numeric_col'], 0)
                st.markdown(f"""
                <div class='insight-box'>
                    <strong>{cat}</strong>
                    <span style='float:right; color:#22c55e'>${val:,.0f}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("**🔴 Bottom Performers**")
            for item in performers.get('bottom', []):
                cat = item.get(performers['cat_col'], 'Unknown')
                val = item.get(performers['numeric_col'], 0)
                color = "#ef4444" if val < 0 else "#f59e0b"
                st.markdown(f"""
                <div class='risk-box'>
                    <strong>{cat}</strong>
                    <span style='float:right; color:{color}'>${val:,.0f}</span>
                </div>
                """, unsafe_allow_html=True)

def _render_insight_section(section, content):
    if not section or not content:
        return
    text = ' '.join(content).strip()
    if section == 'trends':
        st.markdown("### 📈 Top Trends")
        st.markdown(f"<div class='insight-box'>{text}</div>", unsafe_allow_html=True)
    elif section == 'risks':
        st.markdown("### ⚠️ Top Risks")
        st.markdown(f"<div class='risk-box'>{text}</div>", unsafe_allow_html=True)
    elif section == 'opportunities':
        st.markdown("### 💡 Top Opportunities")
        st.markdown(f"<div class='opportunity-box'>{text}</div>", unsafe_allow_html=True)
    elif section == 'summary':
        st.markdown("### 📋 Executive Summary")
        st.info(text)

# ── CHARTS PAGE ────────────────────────────────────────────
def render_charts():
    dp = st.session_state.dp
    viz = st.session_state.viz

    st.markdown("## 📊 Data Overview Charts")

    with st.spinner("Generating charts..."):
        charts = viz.get_overview_charts(dp.df)

    if charts:
        for i in range(0, len(charts), 2):
            col1, col2 = st.columns(2)
            with col1:
                if i < len(charts):
                    st.plotly_chart(charts[i][1], use_container_width=True)
            with col2:
                if i+1 < len(charts):
                    st.plotly_chart(charts[i+1][1], use_container_width=True)
    else:
        st.info("No charts could be generated for this dataset.")

# ── WHAT IF PAGE ───────────────────────────────────────────
def render_whatif():
    dp = st.session_state.dp
    llm = st.session_state.llm

    st.markdown("## 🔮 What If? Decision Simulator")
    st.markdown("Simulate business decisions before making them.")

    st.markdown("""
    <div style='background:#1a1d27; border:1px solid #7c3aed;
        border-radius:12px; padding:20px; margin-bottom:20px'>
        <div style='color:#7c3aed; font-weight:700; margin-bottom:8px'>
            💡 Example Scenarios
        </div>
        <div style='color:#8892b0; font-size:13px'>
            • "What if we increase prices by 10%?"<br>
            • "What if we stop selling Tables?"<br>
            • "What if we expand to 2 more regions?"<br>
            • "What if we reduce shipping costs by 15%?"
        </div>
    </div>
    """, unsafe_allow_html=True)

    scenario = st.text_area(
        "Describe your scenario:",
        placeholder="What if we increase prices by 10%?",
        height=100
    )

    if st.button("🔮 Simulate Decision", use_container_width=True):
        if scenario:
            with st.spinner("Simulating business scenario..."):
                result = llm.simulate_what_if(scenario, dp.get_ai_context())

            st.markdown("### 📊 Simulation Results")
            st.markdown(f"""
            <div style='background:#1a1d27; border:1px solid #7c3aed;
                border-radius:12px; padding:24px;'>
                {result.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a scenario first!")

# ── REPORT PAGE ────────────────────────────────────────────
def render_report():
    dp = st.session_state.dp
    llm = st.session_state.llm
    ig = st.session_state.ig

    st.markdown("## 📄 Export Report")
    st.markdown("Generate a professional PDF consulting report from your analysis.")

    st.markdown("""
    <div style='background:#1a1d27; border:1px solid #4F8EF7;
        border-radius:12px; padding:20px; margin-bottom:20px'>
        <div style='color:#4F8EF7; font-weight:700; margin-bottom:8px'>
            📋 Your Report Will Include:
        </div>
        <div style='color:#8892b0; font-size:13px'>
            • Cover page with dataset details<br>
            • Executive summary with KPI cards<br>
            • Growth analysis<br>
            • Data quality report<br>
            • AI-generated insights<br>
            • Top and bottom performers table<br>
        </div>
    </div>
    """, unsafe_allow_html=True)

    include_insights = st.checkbox(
        "Include AI Insights (adds 30 seconds)", value=True)

    if st.button("📄 Generate PDF Report", use_container_width=True):
        insights_text = None

        if include_insights:
            with st.spinner("Getting AI insights..."):
                try:
                    insights_text = llm.generate_auto_insights(
                        dp.get_ai_context())
                except Exception as e:
                    st.warning(f"Could not get AI insights: {e}")
                    insights_text = None

        with st.spinner("Generating your professional report..."):
            try:
                rg = ReportGenerator()
                report_path = rg.generate_report(dp, ig, insights_text)

                with open(report_path, "rb") as f:
                    pdf_bytes = f.read()

                st.success("Report generated successfully!")
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"InsightIQ_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Report error: {e}")

# ── MAIN ROUTER ────────────────────────────────────────────
def main():
    render_sidebar()
    page = st.session_state.current_page

    if not st.session_state.data_loaded and page != 'home':
        render_home()
    elif page == 'home':
        render_home()
    elif page == 'analyze':
        render_analyze()
    elif page == 'insights':
        render_insights()
    elif page == 'charts':
        render_charts()
    elif page == 'whatif':
        render_whatif()
    elif page == 'report':
        render_report()

if __name__ == "__main__":
    main()