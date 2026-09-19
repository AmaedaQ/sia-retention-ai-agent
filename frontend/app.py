import os
import sys
import time

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Path setup for Cloud environment
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from backend.agents.action import execute_retention_action
from backend.graph import retention_app
from config.settings import settings

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Retention AI | Jazz Telecom",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DESIGN SYSTEM  —  "Signal Room" v3
#
# Same "Mission Control" concept (dark ops-room, Jazz red, live
# telemetry), rebuilt with a proper type system, a calmer background,
# and a card hierarchy that actually distinguishes "read this" from
# "act on this" -- instead of every panel getting the same glass +
# glow treatment.
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    :root {
        --primary:        #e2231a;
        --primary-soft:   #ff5c50;
        --primary-glow:   rgba(226, 35, 26, 0.30);
        --accent:         #22d3ee;
        --accent-glow:    rgba(34, 211, 238, 0.26);
        --success:        #2dd4a7;
        --success-glow:   rgba(45, 212, 167, 0.30);
        --warning:        #f2a93c;
        --bg-0:           #08090d;
        --bg-1:           #0b0d13;
        --bg-card:        rgba(21, 24, 32, 0.68);
        --bg-card-solid:  #14161e;
        --bg-elevated:    #1b1f2a;
        --border:         rgba(255, 255, 255, 0.06);
        --border-strong:  rgba(255, 255, 255, 0.13);
        --text-primary:   #f4f5f8;
        --text-secondary: #9299a8;
        --text-muted:     #5b6272;
    }

    /* ====== GLOBAL RESET / CANVAS ====== */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(900px 560px at 12% -8%, rgba(226,35,26,0.09), transparent 62%),
            var(--bg-0);
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
        position: relative;
        z-index: 1;
    }

    html, body, [class*="st-"], .stMarkdown, p, span, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }

    /* ====== SIDEBAR ====== */
    [data-testid="stSidebar"] {
        background: var(--bg-1);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Sora', sans-serif;
        color: var(--text-secondary) !important;
        font-size: 0.66rem !important;
        font-weight: 600 !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0 0 0.9rem 0 !important;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid var(--border-strong);
        position: relative;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3::after {
        content: "";
        position: absolute; left: 0; bottom: -1px;
        width: 28px; height: 2px;
        background: var(--primary);
        border-radius: 2px;
    }

    /* Sidebar brand block */
    .brand-block {
        display: flex; align-items: center; gap: 12px;
        padding: 0 0 1.2rem 0;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid var(--border);
    }
    .brand-logo {
        width: 42px; height: 42px;
        border-radius: 11px;
        background: #fff;
        display: flex; align-items: center; justify-content: center;
        padding: 6px;
    }
    .brand-logo img { width: 100%; height: 100%; object-fit: contain; }
    .brand-text { line-height: 1.15; }
    .brand-name {
        font-family: 'Sora', sans-serif;
        font-size: 0.95rem; font-weight: 700; letter-spacing: 0.1px;
        color: var(--text-primary);
    }
    .brand-sub {
        font-size: 0.68rem; color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;
        margin-top: 2px;
    }

    /* ====== TERMINAL CONSOLE ====== */
    .terminal-shell {
        position: relative;
        background: #06070a;
        border: 1px solid var(--border-strong);
        border-radius: 12px;
        overflow: hidden;
    }
    .terminal-bar {
        display: flex; align-items: center; gap: 6px;
        padding: 8px 12px;
        background: #0c0e13;
        border-bottom: 1px solid var(--border);
    }
    .terminal-dot { width: 8px; height: 8px; border-radius: 50%; }
    .terminal-dot.r { background: #ff5f57; }
    .terminal-dot.y { background: #febc2e; }
    .terminal-dot.g { background: #28c840; }
    .terminal-title {
        margin-left: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        color: var(--text-muted);
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .terminal-box {
        padding: 13px 14px 15px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.71rem;
        color: var(--success);
        height: 240px;
        overflow-y: auto;
        line-height: 1.7;
    }
    .terminal-box::-webkit-scrollbar { width: 5px; }
    .terminal-box::-webkit-scrollbar-track { background: #06070a; }
    .terminal-box::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }
    .terminal-line { margin-bottom: 5px; white-space: pre-wrap; word-break: break-word; }
    .terminal-line::before { content: "› "; color: var(--primary-soft); font-weight: 700; }

    /* ====== SLIDER ====== */
    .stSlider { padding: 0.3rem 0 0.8rem 0; }
    [data-testid="stSlider"] label {
        color: var(--text-secondary) !important;
        font-size: 0.66rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        margin-bottom: 0.4rem !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div { background: var(--primary) !important; }
    [data-testid="stSlider"] [role="slider"] {
        background: #fff !important;
        border: 2px solid var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(226,35,26,0.16) !important;
    }
    [data-testid="stSlider"] [data-testid="stTickBar"] { display: none; }
    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        background: var(--primary) !important;
        color: white !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        padding: 2px 8px !important;
    }

    /* ====== BUTTONS ====== */
    .stButton > button {
        width: 100%;
        background: var(--primary);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 0.68rem 1.1rem;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.6px;
        transition: background 0.18s ease, transform 0.18s ease;
    }
    .stButton > button:hover { background: var(--primary-soft); transform: translateY(-1px); }
    .stButton > button:active { transform: translateY(0); }

    .deploy-btn .stButton > button {
        background: transparent;
        border: 1px solid rgba(226,35,26,0.45);
        color: #ff8078;
    }
    .deploy-btn .stButton > button:hover {
        background: var(--primary);
        color: #fff;
        border-color: var(--primary);
    }

    /* ====== HEADER ====== */
    .hero {
        display: flex; align-items: flex-end; justify-content: space-between;
        gap: 1.5rem;
        padding: 0 0 1.5rem 0;
        margin-bottom: 1.6rem;
        border-bottom: 1px solid var(--border);
    }
    .hero-title {
        font-family: 'Sora', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        line-height: 1.08;
        color: var(--text-primary);
        margin: 0;
        text-wrap: balance;
    }
    .hero-title .accent { color: var(--primary); }
    .hero-sub {
        color: var(--text-secondary);
        font-size: 0.92rem;
        margin-top: 0.4rem;
    }
    .hero-meta { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end; align-items: center; }

    /* ====== STATUS PILLS ====== */
    .pill {
        display: inline-flex; align-items: center; gap: 8px;
        background: var(--bg-card);
        border: 1px solid var(--border-strong);
        padding: 0.48rem 0.85rem;
        border-radius: 100px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: var(--text-secondary);
    }
    .pill .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); animation: pulse 2.4s ease-in-out infinite; }
    .pill.accent .dot { background: var(--accent); }
    .pill.primary .dot { background: var(--primary); }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%      { opacity: 0.4; }
    }

    /* ====== TABS ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 5px;
        margin-bottom: 1.6rem;
        width: fit-content;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-muted);
        padding: 0.62rem 1.15rem;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        transition: all 0.18s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff;
        background: var(--primary);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ====== METRIC CARDS ====== */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.05rem 1.2rem;
        transition: border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover { border-color: var(--border-strong); }
    [data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-size: 0.66rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem !important;
        font-weight: 600;
    }

    /* ====== SECTION HEADERS ====== */
    .section-head { display: flex; align-items: center; gap: 11px; margin: 0 0 1.1rem 0; }
    .section-head .bar { width: 3px; height: 18px; background: var(--primary); border-radius: 2px; }
    .section-head .label {
        font-family: 'Sora', sans-serif;
        font-size: 1rem; font-weight: 700; letter-spacing: 0.1px;
        color: var(--text-primary);
    }
    .section-head .count {
        margin-left: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    /* ====== ACTION CARDS ====== */
    .action-card {
        background: var(--bg-card-solid);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem 1.35rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .action-card::before {
        content: "";
        position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
        background: var(--primary);
    }
    .action-card:hover { border-color: var(--border-strong); transform: translateX(2px); }
    .action-card .ac-top { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 0.9rem; }
    .action-card .ac-id { display: flex; align-items: center; gap: 10px; }
    .action-card .ac-id .avatar {
        width: 36px; height: 36px; border-radius: 10px;
        background: var(--bg-elevated);
        border: 1px solid var(--border-strong);
        display: flex; align-items: center; justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; font-weight: 700;
        color: var(--primary-soft);
    }
    .action-card .ac-id .uid {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem; font-weight: 700;
        color: var(--text-primary);
    }
    .action-card .ac-id .meta {
        font-size: 0.68rem; color: var(--text-muted);
        letter-spacing: 0.5px; text-transform: uppercase; margin-top: 1px;
    }
    .offer-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(34, 211, 238, 0.1);
        border: 1px solid rgba(34, 211, 238, 0.35);
        color: var(--accent);
        padding: 0.4rem 0.85rem;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        white-space: nowrap;
    }
    .action-card .reasoning {
        color: var(--text-secondary);
        font-size: 0.86rem;
        line-height: 1.6;
        padding: 0.8rem 1rem;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        border-left: 2px solid var(--border-strong);
    }
    .action-card .reasoning .label {
        display: block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        color: var(--text-muted);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    /* ====== EMPTY / INFO PANELS ====== */
    .panel {
        background: var(--bg-card);
        border: 1px dashed var(--border-strong);
        border-radius: 14px;
        padding: 2.2rem 1.75rem;
        text-align: center;
    }
    .panel .icon { font-size: 2rem; margin-bottom: 0.6rem; }
    .panel .title { font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem; }
    .panel .desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; max-width: 480px; margin: 0 auto; }

    /* ====== DATAFRAME ====== */
    [data-testid="stDataFrame"] { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }

    /* ====== ALERTS ====== */
    .stAlert { background: var(--bg-card) !important; border: 1px solid var(--border-strong) !important; border-radius: 12px !important; padding: 1rem 1.15rem !important; color: var(--text-primary) !important; }
    .stAlert [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; font-size: 0.86rem !important; }

    /* ====== PLOTLY ====== */
    .js-plotly-plot { border-radius: 12px; overflow: hidden; }
    [data-testid="stPlotlyChart"] { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 0.4rem; }

    /* ====== TOAST ====== */
    [data-testid="stToast"] { background: var(--bg-card-solid) !important; border: 1px solid var(--success) !important; border-radius: 12px !important; padding: 1rem !important; }
    [data-testid="stToast"] > div { color: var(--text-primary) !important; font-weight: 600 !important; font-size: 0.88rem !important; }

    /* ====== SPINNER ====== */
    [data-testid="stSpinner"] > div { border-top-color: var(--primary) !important; }

    /* ====== DIVIDER UTIL ====== */
    .hr { height: 1px; background: var(--border); margin: 1.4rem 0; border: 0; }

    /* Hide Streamlit's default sidebar nav (we don't use multipage) */
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- DATA UTILITIES (UNCHANGED) ---
LOG_PATH = os.path.join(root_dir, 'backend', 'data', 'action_logs.csv')
USER_DATA_PATH = os.path.join(root_dir, 'backend', 'data', 'jazz_users.csv')

# Initialize session state
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = [
        "Retention AI System v2.0.1",
        "Initializing neural network...",
        "Loading customer behavior models...",
        "System ready for operation."
    ]

if "results" not in st.session_state:
    st.session_state.results = None


def log_event(msg):
    """Add timestamped event to agent logs"""
    ts = time.strftime("%H:%M:%S")
    st.session_state.agent_logs.append(f"[{ts}] {msg}")
    if len(st.session_state.agent_logs) > 50:
        st.session_state.agent_logs = st.session_state.agent_logs[-50:]


@st.cache_data(ttl=60)
def get_analytics():
    """Load and merge analytics data with caching"""
    if os.path.exists(LOG_PATH) and os.path.exists(USER_DATA_PATH):
        try:
            logs = pd.read_csv(LOG_PATH)
            users = pd.read_csv(USER_DATA_PATH)
            if not logs.empty and not users.empty:
                merged_df = pd.merge(logs, users, on='user_id', how='left')
                return merged_df
        except Exception as e:
            log_event(f"Error loading analytics: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=300)
def get_model_evaluation():
    """Pulls the trained model's real, published evaluation artifacts
    (Phase 2's notebooks/02_train_model.py output) from Hugging Face --
    never fabricated, and cached for 5 min so the Evaluation tab doesn't
    re-download on every rerun. Returns a dict:
        {"available": bool, "reason": str | None,
         "metrics": dict | None, "raw": dict | None}
    """
    if not settings.use_ml_model:
        return {"available": False, "reason": "USE_ML_MODEL is off -- the app is scoring with the original formula, not the trained model.", "metrics": None, "raw": None}
    if not settings.hf_model_repo:
        return {"available": False, "reason": "HF_MODEL_REPO is not configured.", "metrics": None, "raw": None}
    try:
        import json as _json

        from huggingface_hub import hf_hub_download
        metrics_path = hf_hub_download(repo_id=settings.hf_model_repo, filename="metrics.json", revision=settings.hf_model_revision)
        with open(metrics_path) as f:
            metrics = _json.load(f)
        raw = None
        try:
            raw_path = hf_hub_download(repo_id=settings.hf_model_repo, filename="test_raw.json", revision=settings.hf_model_revision)
            with open(raw_path) as f:
                raw = _json.load(f)
        except Exception:
            pass  # optional -- older publishes won't have it
        return {"available": True, "reason": None, "metrics": metrics, "raw": raw}
    except Exception as e:
        return {"available": False, "reason": f"could not fetch published evaluation artifacts: {e}", "metrics": None, "raw": None}


# ============================================================
# SIDEBAR: CONTROL PANEL
# ============================================================
with st.sidebar:
    st.markdown("""
        <div class="brand-block">
            <div class="brand-logo">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Jazz_logo.svg/1200px-Jazz_logo.svg.png" />
            </div>
            <div class="brand-text">
                <div class="brand-name">Retention AI</div>
                <div class="brand-sub">JAZZ · v2.0.1</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Control Panel")

    # Terminal Console (styled shell with traffic lights)
    logs_to_display = st.session_state.agent_logs[-15:]
    logs_html = "".join([f'<div class="terminal-line">{log}</div>' for log in logs_to_display])
    st.markdown(f"""
        <div class="terminal-shell">
            <div class="terminal-bar">
                <span class="terminal-dot r"></span>
                <span class="terminal-dot y"></span>
                <span class="terminal-dot g"></span>
                <span class="terminal-title">agent · stream</span>
            </div>
            <div class="terminal-box">{logs_html}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk Threshold Control
    threshold = st.slider(
        "Risk Sensitivity",
        min_value=0.40,
        max_value=0.95,
        value=0.70,
        step=0.05,
        help="Adjust the threshold for identifying at-risk customers"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Scan Button
    if st.button("🔍  Run Network Scan", key="scan_button"):
        log_event("Initiating churn risk analysis...")
        with st.spinner("Analyzing customer behavior patterns..."):
            try:
                results = retention_app.invoke({
                    "threshold": threshold,
                    "risky_users": [],
                    "final_reports": []
                })
                st.session_state.results = results
                num_flagged = len(results.get('risky_users', []))
                log_event(f"Scan complete: {num_flagged} customers flagged")
            except Exception as e:
                log_event(f"Scan error: {str(e)}")
                st.error(f"Scan failed: {str(e)}")
        st.rerun()


# ============================================================
# HERO HEADER
# ============================================================
st.markdown("""
    <div class="hero">
        <div>
            <div class="hero-title">Retention <span class="accent">AI</span></div>
            <div class="hero-sub">Intelligent Customer Retention System for Jazz Telecom</div>
        </div>
        <div class="hero-meta">
            <div class="pill primary"><span class="dot"></span>System Active</div>
            <div class="pill accent"><span class="dot"></span>LangGraph Pipeline</div>
        </div>
    </div>
""", unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Active Queue",
    "📈  Analytics",
    "📜  History",
    "🧪  Evaluation"
])


# ============================================================
# TAB 1: ACTIVE QUEUE
# ============================================================
with tab1:
    if st.session_state.results is not None:
        current_logs = get_analytics()
        executed_ids = current_logs['user_id'].tolist() if not current_logs.empty else []

        final_reports = st.session_state.results.get('final_reports', [])
        active_reports = [r for r in final_reports if r.get('user_id') not in executed_ids]

        if active_reports:
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Pending Actions", len(active_reports))
            with col2:
                risky_users_count = len(st.session_state.results.get('risky_users', []))
                st.metric("Risk Pool", risky_users_count)
            with col3:
                _eval = get_model_evaluation()
                if _eval["available"]:
                    _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                    st.metric(
                        "Model ROC-AUC (test)",
                        f"{_test_auc:.3f}",
                        help=f"From the published model at {settings.hf_model_repo}@{settings.hf_model_revision} -- see the Evaluation tab."
                    )
                else:
                    st.metric(
                        "Scoring Mode",
                        "Formula",
                        help="USE_ML_MODEL is off, or the trained model isn't reachable -- see the Evaluation tab for details."
                    )
            with col4:
                st.metric("AI Status", "Active")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"""
                <div class="section-head">
                    <span class="bar"></span>
                    <span class="label">Deployment Queue</span>
                    <span class="count">{len(active_reports)} awaiting review</span>
                </div>
            """, unsafe_allow_html=True)

            # Action Cards
            for report in active_reports:
                user_id = report.get('user_id', 'N/A')
                offer = report.get('offer', 'N/A')
                reasoning = report.get('reasoning', 'No reasoning provided')

                initials = str(user_id)[:2].upper() if user_id != 'N/A' else '??'

                st.markdown(f"""
                    <div class="action-card">
                        <div class="ac-top">
                            <div class="ac-id">
                                <div class="avatar">{initials}</div>
                                <div>
                                    <div class="uid">{user_id}</div>
                                    <div class="meta">Customer · Retention Target</div>
                                </div>
                            </div>
                            <span class="offer-badge">{offer}</span>
                        </div>
                        <div class="reasoning">
                            <span class="label">Agent Reasoning</span>
                            {reasoning}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_btn, col_space = st.columns([2, 3])
                with col_btn:
                    st.markdown('<div class="deploy-btn">', unsafe_allow_html=True)
                    if st.button("Deploy Retention Strategy", key=f"deploy_{user_id}"):
                        try:
                            success = execute_retention_action(report)
                            if success:
                                log_event(f"Successfully deployed strategy for {user_id}")
                                st.toast(f"✅ Strategy deployed for {user_id}", icon="✅")
                                time.sleep(0.5)
                                get_analytics.clear()
                                st.rerun()
                            else:
                                log_event(f"Failed to deploy strategy for {user_id}")
                                st.toast(f"❌ Deployment failed for {user_id}", icon="❌")
                        except Exception as e:
                            log_event(f"Error deploying for {user_id}: {str(e)}")
                            st.error(f"Deployment error: {str(e)}")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="panel">
                    <div class="icon">✅</div>
                    <div class="title">Queue Clear</div>
                    <div class="desc">All flagged customers have been processed. Run a new scan to refresh the risk pool.</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                if st.button("🔄  Scan for New Targets", key="rescan_button"):
                    log_event("Initiating new network scan...")
                    with st.spinner("Scanning for new targets..."):
                        try:
                            results = retention_app.invoke({
                                "threshold": threshold,
                                "risky_users": [],
                                "final_reports": []
                            })
                            st.session_state.results = results
                            log_event(f"Rescan complete: {len(results.get('risky_users', []))} customers found")
                            get_analytics.clear()
                        except Exception as e:
                            log_event(f"Rescan error: {str(e)}")
                            st.error(f"Rescan failed: {str(e)}")
                    st.rerun()
    else:
        st.markdown("""
            <div class="panel">
                <div class="icon">⚡</div>
                <div class="title">No Scan On Record</div>
                <div class="desc">Use the Control Panel in the sidebar to initiate your first network scan. The system will surface at-risk customers and generate retention strategies.</div>
            </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 2: ANALYTICS
# ============================================================
with tab2:
    st.markdown("""
        <div class="section-head">
            <span class="bar"></span>
            <span class="label">Performance Analytics</span>
        </div>
    """, unsafe_allow_html=True)

    analytics_df = get_analytics()

    if not analytics_df.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Actions", len(analytics_df))

        with col2:
            if 'churn_risk_score' in analytics_df.columns:
                avg_risk = analytics_df['churn_risk_score'].mean()
                st.metric("Avg Risk Score", f"{avg_risk:.2f}")
            else:
                st.metric("Avg Risk Score", "N/A")

        with col3:
            unique_customers = analytics_df['user_id'].nunique()
            st.metric("Unique Customers", unique_customers)

        with col4:
            if 'offer_sent' in analytics_df.columns and not analytics_df['offer_sent'].empty:
                mode_offers = analytics_df['offer_sent'].mode()
                most_common = mode_offers[0] if len(mode_offers) > 0 else "N/A"
                st.metric("Most Common Offer", most_common)
            else:
                st.metric("Most Common Offer", "N/A")

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'offer_sent' in analytics_df.columns:
                st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Offer Distribution</span></div>', unsafe_allow_html=True)
                fig = px.pie(
                    analytics_df,
                    names='offer_sent',
                    hole=0.65,
                    color_discrete_sequence=['#e30613', '#ff5c69', '#00d4ff', '#f59e0b', '#10b981']
                )
                fig.update_traces(
                    textposition='outside',
                    textinfo='percent+label',
                    textfont=dict(size=11, color='#a0aec0'),
                    marker=dict(line=dict(color='#05070c', width=2))
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#f7fafc', size=12),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=340,
                )
                st.plotly_chart(fig, width="stretch", key="offer_pie")

        with col2:
            if 'churn_risk_score' in analytics_df.columns:
                st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Risk Score Distribution</span></div>', unsafe_allow_html=True)
                fig2 = px.histogram(
                    analytics_df,
                    x='churn_risk_score',
                    nbins=20,
                    color_discrete_sequence=['#e30613']
                )
                fig2.update_traces(
                    marker=dict(line=dict(color='#05070c', width=1)),
                    opacity=0.85,
                )
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#f7fafc', size=12),
                    xaxis=dict(showgrid=False, title="Risk Score", zeroline=False, color='#8b97ab'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title="Count", zeroline=False, color='#8b97ab'),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=340,
                    bargap=0.05,
                )
                st.plotly_chart(fig2, width="stretch", key="risk_hist")

        st.markdown("<br>", unsafe_allow_html=True)

        if 'timestamp' in analytics_df.columns:
            st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Activity Timeline</span></div>', unsafe_allow_html=True)
            try:
                analytics_df['date'] = pd.to_datetime(analytics_df['timestamp']).dt.date
                timeline_data = analytics_df.groupby('date').size().reset_index(name='actions')

                fig3 = px.line(
                    timeline_data,
                    x='date',
                    y='actions',
                    color_discrete_sequence=['#e30613']
                )
                fig3.update_traces(
                    line=dict(width=2.5),
                    mode='lines+markers',
                    marker=dict(size=8, line=dict(color='#05070c', width=2)),
                    fill='tozeroy',
                    fillcolor='rgba(227,6,19,0.07)',
                )
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#f7fafc', size=12),
                    xaxis=dict(showgrid=False, title="", color='#8b97ab', zeroline=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title="Actions", color='#8b97ab', zeroline=False),
                    hovermode='x unified',
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=320,
                )
                st.plotly_chart(fig3, width="stretch", key="timeline")
            except Exception as e:
                log_event(f"Error creating timeline: {str(e)}")
                st.warning("Unable to display timeline chart")
    else:
        st.markdown("""
            <div class="panel">
                <div class="icon">📈</div>
                <div class="title">No Analytics Yet</div>
                <div class="desc">Run a network scan and deploy some retention strategies to generate insight into offer performance and risk distribution.</div>
            </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 3: HISTORY
# ============================================================
with tab3:
    st.markdown("""
        <div class="section-head">
            <span class="bar"></span>
            <span class="label">Action History</span>
        </div>
    """, unsafe_allow_html=True)

    df = get_analytics()

    if not df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Records", len(df))

        with col2:
            if 'timestamp' in df.columns:
                try:
                    latest = pd.to_datetime(df['timestamp']).max()
                    st.metric("Latest Action", latest.strftime("%Y-%m-%d %H:%M"))
                except Exception:
                    st.metric("Latest Action", "N/A")
            else:
                st.metric("Latest Action", "N/A")

        with col3:
            st.metric("Data Points", len(df.columns))

        st.markdown("<br>", unsafe_allow_html=True)

        display_df = df.copy()
        if 'timestamp' in display_df.columns:
            try:
                display_df = display_df.sort_values('timestamp', ascending=False)
            except Exception:
                pass

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            height=500
        )
    else:
        st.markdown("""
            <div class="panel">
                <div class="icon">📜</div>
                <div class="title">No History Yet</div>
                <div class="desc">Execute retention actions to build your audit trail. Every deployment is logged here for compliance and review.</div>
            </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 4: EVALUATION
# ============================================================
with tab4:
    st.markdown("""
        <div class="section-head">
            <span class="bar"></span>
            <span class="label">Model Evaluation</span>
        </div>
    """, unsafe_allow_html=True)

    eval_data = get_model_evaluation()

    if not eval_data["available"]:
        st.warning(f"⚠️ No live model evaluation to show: {eval_data['reason']}")
        st.markdown(
            "The dashboard falls back to the original hand-written formula "
            "(`backend/data_generator.py`) whenever the trained model isn't "
            "configured or reachable -- that's by design (`USE_ML_MODEL` in "
            "`config/settings.py`), not a bug. Set `USE_ML_MODEL=true`, "
            "`HF_MODEL_REPO`, and `HF_MODEL_REVISION` in `.env` to point at a "
            "published model and this tab will populate with its real, "
            "published metrics."
        )
    else:
        metrics = eval_data["metrics"]
        raw = eval_data["raw"]
        test_row = metrics["splits"][-1]

        badge_col, auc_col, formula_col = st.columns(3)
        with badge_col:
            st.metric(
                "Model Version",
                metrics.get("model_version", "unknown"),
                help=f"Published at huggingface.co/{settings.hf_model_repo}"
            )
        with auc_col:
            st.metric("Test ROC-AUC (model)", f"{test_row['model']['roc_auc']:.4f}")
        with formula_col:
            delta = test_row['model']['roc_auc'] - test_row['old_formula_roc_auc']
            st.metric(
                "Test ROC-AUC (old formula)",
                f"{test_row['old_formula_roc_auc']:.4f}",
                delta=f"{delta:+.4f} vs. model",
                delta_color="inverse"
            )

        st.caption(
            "Both scores are computed on the exact same held-out test rows -- "
            "the old formula is the literal one from `backend/data_generator.py` "
            "(`(days_since_last_recharge/45)*0.4 + (1-signal_strength_score)*0.4 "
            "+ support_tickets_open*0.2`), scored here only for comparison, never "
            "used for actual predictions once `USE_ML_MODEL` is on."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Metrics by split</span></div>', unsafe_allow_html=True)
        rows = []
        for split in metrics["splits"]:
            m = split["model"]
            rows.append({
                "split": split["split"],
                "n": split["n"],
                "accuracy": m["accuracy"],
                "precision": m["precision"],
                "recall": m["recall"],
                "f1": m["f1"],
                "roc_auc (model)": m["roc_auc"],
                "roc_auc (old formula)": split["old_formula_roc_auc"],
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Model vs. old formula (ROC-AUC)</span></div>', unsafe_allow_html=True)
            bar_df = pd.DataFrame(rows)
            fig_bar = go.Figure(data=[
                go.Bar(name="Model", x=bar_df["split"], y=bar_df["roc_auc (model)"], marker_color="#e30613"),
                go.Bar(name="Old formula", x=bar_df["split"], y=bar_df["roc_auc (old formula)"], marker_color="#4a5568"),
            ])
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family='Inter', color="#f7fafc", size=12),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="ROC-AUC", range=[0, 1], color='#8b97ab', zeroline=False),
                xaxis=dict(title="", color='#8b97ab'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'),
                margin=dict(l=20, r=20, t=40, b=20),
                height=340,
            )
            st.plotly_chart(fig_bar, width="stretch", key="eval_auc_bar")

        with chart_col2:
            st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Top features (mean |SHAP|)</span></div>', unsafe_allow_html=True)
            top_features = metrics.get("top_features_test", [])
            if top_features:
                shap_df = pd.DataFrame(top_features).sort_values("mean_abs_shap")
                fig_shap = go.Figure(go.Bar(
                    x=shap_df["mean_abs_shap"],
                    y=shap_df["feature"],
                    orientation="h",
                    marker=dict(
                        color=shap_df["mean_abs_shap"],
                        colorscale=[[0, '#0e3a4a'], [1, '#00d4ff']],
                        line=dict(color='rgba(0,0,0,0)'),
                    ),
                ))
                fig_shap.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family='Inter', color="#f7fafc", size=12),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="mean |SHAP value|", color='#8b97ab', zeroline=False),
                    yaxis=dict(title="", color='#8b97ab'),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=340,
                )
                st.plotly_chart(fig_shap, width="stretch", key="eval_shap_bar")
            else:
                st.info("No SHAP summary published with this model version.")

        st.markdown("<br>", unsafe_allow_html=True)

        if raw is not None:
            y_true = np.array(raw["y_true"])
            y_proba = np.array(raw["model_proba"])

            st.markdown('<div class="section-head"><span class="bar"></span><span class="label">ROC & Precision-Recall (test set)</span></div>', unsafe_allow_html=True)
            curve_col1, curve_col2 = st.columns(2)

            thresholds = np.linspace(0.0, 1.0, 101)
            tprs, fprs, precisions, recalls = [], [], [], []
            P = y_true.sum()
            N = len(y_true) - P
            for t in thresholds:
                pred = (y_proba >= t).astype(int)
                tp = int(((pred == 1) & (y_true == 1)).sum())
                fp = int(((pred == 1) & (y_true == 0)).sum())
                fn = int(((pred == 0) & (y_true == 1)).sum())
                tprs.append(tp / P if P else 0.0)
                fprs.append(fp / N if N else 0.0)
                precisions.append(tp / (tp + fp) if (tp + fp) else 1.0)
                recalls.append(tp / P if P else 0.0)

            with curve_col1:
                fig_roc = go.Figure()
                fig_roc.add_trace(go.Scatter(
                    x=fprs, y=tprs, mode="lines", name="Model",
                    line=dict(color="#e30613", width=3),
                    fill='tozeroy', fillcolor='rgba(227,6,19,0.08)',
                ))
                fig_roc.add_trace(go.Scatter(
                    x=[0, 1], y=[0, 1], mode="lines", name="Random",
                    line=dict(color="#4a5568", dash="dash", width=1.5),
                ))
                fig_roc.update_layout(
                    title=dict(text="ROC curve", font=dict(size=13, color='#8b97ab')),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family='Inter', color="#f7fafc", size=12),
                    xaxis=dict(title="False Positive Rate", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#8b97ab', zeroline=False),
                    yaxis=dict(title="True Positive Rate", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#8b97ab', zeroline=False),
                    legend=dict(bgcolor='rgba(0,0,0,0)'),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=340,
                )
                st.plotly_chart(fig_roc, width="stretch", key="eval_roc")

            with curve_col2:
                fig_pr = go.Figure()
                fig_pr.add_trace(go.Scatter(
                    x=recalls, y=precisions, mode="lines", name="Model",
                    line=dict(color="#00d4ff", width=3),
                    fill='tozeroy', fillcolor='rgba(0,212,255,0.08)',
                ))
                fig_pr.update_layout(
                    title=dict(text="Precision-Recall curve", font=dict(size=13, color='#8b97ab')),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family='Inter', color="#f7fafc", size=12),
                    xaxis=dict(title="Recall", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#8b97ab', zeroline=False),
                    yaxis=dict(title="Precision", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#8b97ab', zeroline=False),
                    legend=dict(bgcolor='rgba(0,0,0,0)'),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=340,
                )
                st.plotly_chart(fig_pr, width="stretch", key="eval_pr")

            st.markdown('<div class="section-head"><span class="bar"></span><span class="label">Confusion matrix (threshold = 0.5)</span></div>', unsafe_allow_html=True)
            pred_50 = (y_proba >= 0.5).astype(int)
            tp = int(((pred_50 == 1) & (y_true == 1)).sum())
            fp = int(((pred_50 == 1) & (y_true == 0)).sum())
            fn = int(((pred_50 == 0) & (y_true == 1)).sum())
            tn = int(((pred_50 == 0) & (y_true == 0)).sum())
            cm = [[tn, fp], [fn, tp]]
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=["Pred: Stay", "Pred: Churn"],
                y=["Actual: Stay", "Actual: Churn"],
                text=cm,
                texttemplate="<b>%{text}</b>",
                textfont=dict(size=18, color="#ffffff"),
                colorscale=[[0, "#0a0e16"], [1, "#e30613"]],
                showscale=False,
                hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
            ))
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family='Inter', color="#f7fafc", size=12),
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                xaxis=dict(color='#8b97ab', side='bottom'),
                yaxis=dict(color='#8b97ab', autorange='reversed'),
            )
            st.plotly_chart(fig_cm, width="stretch", key="eval_cm")
        else:
            st.info(
                "ℹ️ Per-row test predictions (`test_raw.json`) weren't published with "
                "this model version, so a real ROC/PR curve and confusion matrix "
                "can't be drawn here -- only the aggregate metrics above, which are "
                "real. Re-run `notebooks/02_train_model.py` (it now saves "
                "`test_raw.json` alongside `metrics.json`) and re-publish with "
                "`scripts/push_model_to_hf.py` to unlock this section."
            )
