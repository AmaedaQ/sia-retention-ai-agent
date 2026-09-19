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
    initial_sidebar_state="collapsed",
)

LOG_PATH = os.path.join(root_dir, 'backend', 'data', 'action_logs.csv')
USER_DATA_PATH = os.path.join(root_dir, 'backend', 'data', 'jazz_users.csv')

# ============================================================
# DESIGN SYSTEM  —  "Guided Flow" (v3)
#
# The old dashboard put four tabs and a sidebar full of controls in
# front of a new user with no indication of what to do first. This
# version is one column, top to bottom: Scan -> Review -> Deploy. Every
# other view (analytics, history, model evaluation) still exists, just
# tucked under collapsed sections below the flow instead of competing
# with it for attention.
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {
        --primary:        #e2231a;
        --primary-soft:   #ff5c50;
        --primary-glow:   rgba(226, 35, 26, 0.28);
        --accent:         #38bdf8;
        --success:        #22c55e;
        --success-soft:   rgba(34, 197, 94, 0.14);
        --warning:        #f5a524;
        --bg-0:           #0a0c11;
        --bg-1:           #0d1016;
        --surface:        #12151d;
        --surface-2:      #171b25;
        --border:         rgba(255, 255, 255, 0.08);
        --border-strong:  rgba(255, 255, 255, 0.16);
        --text-primary:   #f3f5f8;
        --text-secondary: #9aa3b2;
        --text-muted:     #616b7c;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg-0);
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container {
        padding-top: 1.6rem !important;
        padding-bottom: 3rem !important;
        max-width: 900px;
    }
    html, body, [class*="st-"], .stMarkdown, p, span, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    h1, h2, h3 { font-family: 'Sora', sans-serif; }

    [data-testid="stSidebar"] {
        background: var(--bg-1);
        border-right: 1px solid var(--border);
    }

    /* ---- top bar ---- */
    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding-bottom: 1.4rem; margin-bottom: 1.6rem;
        border-bottom: 1px solid var(--border);
    }
    .topbar-brand { display: flex; align-items: center; gap: 0.6rem; }
    .topbar-brand img { height: 22px; }
    .topbar-name { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.05rem; }
    .topbar-name .accent { color: var(--primary); }
    .topbar-status {
        display: flex; align-items: center; gap: 0.4rem;
        font-size: 0.78rem; color: var(--text-secondary);
        background: var(--surface); border: 1px solid var(--border);
        padding: 0.3rem 0.7rem; border-radius: 999px;
    }
    .topbar-status .dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--success); box-shadow: 0 0 6px var(--success);
    }

    /* ---- step tracker ---- */
    .steps { display: flex; align-items: center; gap: 0; margin-bottom: 1.8rem; }
    .step { display: flex; align-items: center; gap: 0.55rem; flex: 1; }
    .step-num {
        width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.8rem;
        background: var(--surface); border: 1px solid var(--border-strong);
        color: var(--text-muted);
    }
    .step.done .step-num { background: var(--success-soft); border-color: var(--success); color: var(--success); }
    .step.active .step-num { background: var(--primary); border-color: var(--primary); color: white; box-shadow: 0 0 0 4px var(--primary-glow); }
    .step-label { font-size: 0.82rem; color: var(--text-muted); font-weight: 500; }
    .step.active .step-label, .step.done .step-label { color: var(--text-primary); }
    .step-line { flex: 0 0 auto; width: 100%; height: 1px; background: var(--border-strong); margin: 0 0.7rem; }
    .step-connector { flex: 1; height: 1px; background: var(--border-strong); margin: 0 0.4rem; }
    .step-connector.done { background: var(--success); opacity: 0.5; }

    /* ---- cards ---- */
    .flow-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 16px; padding: 1.8rem 2rem; margin-bottom: 1.2rem;
    }
    .flow-card.hero {
        background: linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
        border-color: var(--border-strong);
    }
    .flow-eyebrow {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 1.6px; text-transform: uppercase;
        color: var(--primary); margin-bottom: 0.4rem;
    }
    .flow-title { font-family: 'Sora', sans-serif; font-size: 1.35rem; font-weight: 700; margin-bottom: 0.35rem; }
    .flow-sub { font-size: 0.92rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 0; }

    /* ---- customer card ---- */
    .cust-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 14px; padding: 1.1rem 1.3rem; margin-bottom: 0.7rem;
    }
    .cust-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.6rem; }
    .cust-id { display: flex; align-items: center; gap: 0.7rem; }
    .cust-avatar {
        width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
        background: linear-gradient(135deg, var(--primary), var(--primary-soft));
        display: flex; align-items: center; justify-content: center;
        font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 0.82rem; color: white;
    }
    .cust-uid { font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 0.95rem; }
    .cust-risk { font-size: 0.76rem; color: var(--text-muted); }
    .offer-chip {
        font-size: 0.76rem; font-weight: 600; padding: 0.28rem 0.7rem; border-radius: 999px;
        background: rgba(56, 189, 248, 0.12); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.3);
        white-space: nowrap;
    }
    .cust-reason { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; padding-top: 0.5rem; border-top: 1px solid var(--border); }

    /* ---- empty state ---- */
    .empty-state { text-align: center; padding: 2.2rem 1rem; }
    .empty-state .icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
    .empty-state .title { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.05rem; margin-bottom: 0.3rem; }
    .empty-state .desc { font-size: 0.88rem; color: var(--text-secondary); max-width: 420px; margin: 0 auto; }

    /* ---- buttons ---- */
    .stButton > button {
        border-radius: 10px !important; font-weight: 600 !important;
        border: 1px solid var(--border-strong) !important;
        background: var(--surface-2) !important; color: var(--text-primary) !important;
    }
    .stButton > button:hover { border-color: var(--primary) !important; color: var(--primary) !important; }
    div[data-testid="stButton"].primary-cta > button,
    .primary-cta button {
        background: var(--primary) !important; border-color: var(--primary) !important; color: white !important;
        font-size: 1rem !important; padding: 0.7rem 1rem !important;
    }
    .primary-cta button:hover { background: var(--primary-soft) !important; border-color: var(--primary-soft) !important; color: white !important; }

    [data-testid="stMetric"] {
        background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.9rem 1.1rem;
    }
    [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }

    [data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 12px !important; background: var(--surface); }

    .section-head { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.8rem; }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# STATE
# ============================================================
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "results" not in st.session_state:
    st.session_state.results = None


def log_event(msg):
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
    never fabricated, and cached for 5 min so the Evaluation section
    doesn't re-download on every rerun. Returns a dict:
        {"available": bool, "reason": str | None,
         "metrics": dict | None, "raw": dict | None}
    """
    if not settings.use_ml_model:
        return {"available": False, "reason": "The app is scoring with the original formula, not the trained model (USE_ML_MODEL is off).", "metrics": None, "raw": None}
    if not settings.hf_model_repo:
        return {"available": False, "reason": "No model is configured (HF_MODEL_REPO is empty).", "metrics": None, "raw": None}
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
        return {"available": False, "reason": f"couldn't fetch the published model's evaluation data: {e}", "metrics": None, "raw": None}


def run_scan(threshold, log_prefix="Scan"):
    with st.spinner("Scanning customers for churn risk..."):
        try:
            results = retention_app.invoke({
                "threshold": threshold,
                "risky_users": [],
                "final_reports": []
            })
            st.session_state.results = results
            n = len(results.get('risky_users', []))
            log_event(f"{log_prefix} complete: {n} customers flagged")
            get_analytics.clear()
        except Exception as e:
            log_event(f"{log_prefix} error: {str(e)}")
            st.error(f"Scan failed: {e}")


# ============================================================
# TOP BAR
# ============================================================
st.markdown("""
    <div class="topbar">
        <div class="topbar-brand">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Jazz_logo.svg/1200px-Jazz_logo.svg.png" />
            <span class="topbar-name">Retention <span class="accent">AI</span></span>
        </div>
        <div class="topbar-status"><span class="dot"></span>System active</div>
    </div>
""", unsafe_allow_html=True)

# Figure out where the user is in the flow, to drive the step tracker
# and decide which card to show as the "current" one.
results = st.session_state.results
risky_users = results.get('risky_users', []) if results else []
final_reports = results.get('final_reports', []) if results else []

current_logs_df = get_analytics()
executed_ids = current_logs_df['user_id'].tolist() if not current_logs_df.empty else []
pending_reports = [r for r in final_reports if r.get('user_id') not in executed_ids]

has_scanned = results is not None
has_pending = len(pending_reports) > 0
deployed_this_session = has_scanned and not has_pending and len(final_reports) > 0

step1_state = "done" if has_scanned else "active"
step2_state = "active" if has_scanned and has_pending else ("done" if has_scanned and not has_pending else "")
step3_state = "active" if deployed_this_session else ""

st.markdown(f"""
    <div class="steps">
        <div class="step {step1_state}"><div class="step-num">1</div><div class="step-label">Scan</div></div>
        <div class="step-connector {'done' if has_scanned else ''}"></div>
        <div class="step {step2_state}"><div class="step-num">2</div><div class="step-label">Review &amp; deploy</div></div>
        <div class="step-connector {'done' if deployed_this_session else ''}"></div>
        <div class="step {step3_state}"><div class="step-num">3</div><div class="step-label">Impact</div></div>
    </div>
""", unsafe_allow_html=True)


# ============================================================
# STEP 1 — SCAN
# ============================================================
with st.container():
    st.markdown("""
        <div class="flow-card hero">
            <div class="flow-eyebrow">Step 1</div>
            <div class="flow-title">Scan for customers at risk of leaving</div>
            <div class="flow-sub">The AI checks every customer's usage and support history and flags the ones likely to churn.</div>
        </div>
    """, unsafe_allow_html=True)

    scan_col1, scan_col2 = st.columns([3, 1])
    with scan_col1:
        threshold = st.slider(
            "Sensitivity — lower catches more customers, higher shows only the clearest risks",
            min_value=0.40, max_value=0.95, value=0.70, step=0.05,
        )
    with scan_col2:
        st.markdown('<div class="primary-cta">', unsafe_allow_html=True)
        if st.button("🔍  Scan now", key="scan_button", width="stretch"):
            log_event("Initiating churn risk analysis...")
            run_scan(threshold, "Scan")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if has_scanned:
        st.caption(f"Last scan flagged **{len(risky_users)}** customer(s) at or above {threshold:.0%} risk.")


# ============================================================
# STEP 2 — REVIEW & DEPLOY
# ============================================================
if has_scanned:
    if pending_reports:
        st.markdown(f"""
            <div class="flow-card">
                <div class="flow-eyebrow">Step 2</div>
                <div class="flow-title">Review and send retention offers</div>
                <div class="flow-sub">{len(pending_reports)} customer(s) need a decision. Each card is the AI's suggested offer and why.</div>
            </div>
        """, unsafe_allow_html=True)

        for report in pending_reports:
            user_id = report.get('user_id', 'N/A')
            offer = report.get('offer', 'N/A')
            reasoning = report.get('reasoning', 'No reasoning provided')
            initials = str(user_id)[-3:] if user_id != 'N/A' else '???'
            risk_row = next((u for u in risky_users if u.get('user_id') == user_id), None)
            risk_score = risk_row.get('churn_risk_score') if risk_row else None

            st.markdown(f"""
                <div class="cust-card">
                    <div class="cust-top">
                        <div class="cust-id">
                            <div class="cust-avatar">{initials}</div>
                            <div>
                                <div class="cust-uid">{user_id}</div>
                                <div class="cust-risk">{f"Risk score {risk_score:.2f}" if risk_score is not None else "Flagged as high-risk"}</div>
                            </div>
                        </div>
                        <span class="offer-chip">{offer}</span>
                    </div>
                    <div class="cust-reason">{reasoning}</div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("Send this offer", key=f"deploy_{user_id}"):
                try:
                    success = execute_retention_action(report)
                    if success:
                        log_event(f"Sent {offer} to {user_id}")
                        st.toast(f"✅ Offer sent to {user_id}", icon="✅")
                        time.sleep(0.4)
                        get_analytics.clear()
                        st.rerun()
                    else:
                        st.toast(f"❌ Couldn't send offer to {user_id}", icon="❌")
                except Exception as e:
                    st.error(f"Error sending offer: {e}")
    else:
        st.markdown("""
            <div class="flow-card">
                <div class="empty-state">
                    <div class="icon">✅</div>
                    <div class="title">Queue clear</div>
                    <div class="desc">Every flagged customer has an offer on the way. Scan again any time to check for new risks.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# ============================================================
# STEP 3 — IMPACT (only once something's actually been deployed)
# ============================================================
if not current_logs_df.empty:
    st.markdown("""
        <div class="flow-card">
            <div class="flow-eyebrow">Step 3</div>
            <div class="flow-title">Impact so far</div>
        </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Offers sent", len(current_logs_df))
    with m2:
        st.metric("Customers reached", current_logs_df['user_id'].nunique())
    with m3:
        _eval = get_model_evaluation()
        if _eval["available"]:
            _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
            st.metric("Model accuracy (ROC-AUC)", f"{_test_auc:.2f}")
        else:
            st.metric("Scoring mode", "Formula")


# ============================================================
# EVERYTHING ELSE — tucked away, not competing with the flow above
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📈  Analytics — offers, risk distribution, activity over time"):
    analytics_df = get_analytics()
    if not analytics_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Actions", len(analytics_df))
        with col2:
            if 'churn_risk_score' in analytics_df.columns:
                st.metric("Avg Risk Score", f"{analytics_df['churn_risk_score'].mean():.2f}")
            else:
                st.metric("Avg Risk Score", "N/A")
        with col3:
            st.metric("Unique Customers", analytics_df['user_id'].nunique())
        with col4:
            if 'offer_sent' in analytics_df.columns and not analytics_df['offer_sent'].empty:
                mode_offers = analytics_df['offer_sent'].mode()
                st.metric("Most Common Offer", mode_offers[0] if len(mode_offers) > 0 else "N/A")
            else:
                st.metric("Most Common Offer", "N/A")

        col1, col2 = st.columns(2)
        with col1:
            if 'offer_sent' in analytics_df.columns:
                st.markdown('<div class="section-head">Offer distribution</div>', unsafe_allow_html=True)
                fig = px.pie(
                    analytics_df, names='offer_sent', hole=0.65,
                    color_discrete_sequence=['#e2231a', '#ff8a80', '#38bdf8', '#f5a524', '#22c55e'],
                )
                fig.update_traces(textposition='outside', textinfo='percent+label',
                                   textfont=dict(size=11, color='#9aa3b2'),
                                   marker=dict(line=dict(color='#12151d', width=2)))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   font=dict(family='Inter', color='#f3f5f8', size=12),
                                   showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=320)
                st.plotly_chart(fig, width="stretch", key="offer_pie")
        with col2:
            if 'churn_risk_score' in analytics_df.columns:
                st.markdown('<div class="section-head">Risk score distribution</div>', unsafe_allow_html=True)
                fig2 = px.histogram(analytics_df, x='churn_risk_score', nbins=20, color_discrete_sequence=['#e2231a'])
                fig2.update_traces(marker=dict(line=dict(color='#12151d', width=1)), opacity=0.85)
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#f3f5f8', size=12),
                    xaxis=dict(showgrid=False, title="Risk Score", zeroline=False, color='#9aa3b2'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title="Count", zeroline=False, color='#9aa3b2'),
                    margin=dict(l=20, r=20, t=20, b=20), height=320, bargap=0.05,
                )
                st.plotly_chart(fig2, width="stretch", key="risk_hist")

        if 'timestamp' in analytics_df.columns:
            st.markdown('<div class="section-head">Activity over time</div>', unsafe_allow_html=True)
            try:
                analytics_df['date'] = pd.to_datetime(analytics_df['timestamp']).dt.date
                timeline_data = analytics_df.groupby('date').size().reset_index(name='actions')
                fig3 = px.line(timeline_data, x='date', y='actions', color_discrete_sequence=['#e2231a'])
                fig3.update_traces(line=dict(width=2.5), mode='lines+markers',
                                    marker=dict(size=8, line=dict(color='#12151d', width=2)),
                                    fill='tozeroy', fillcolor='rgba(226,35,26,0.08)')
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#f3f5f8', size=12),
                    xaxis=dict(showgrid=False, title="", color='#9aa3b2', zeroline=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title="Actions", color='#9aa3b2', zeroline=False),
                    hovermode='x unified', margin=dict(l=20, r=20, t=20, b=20), height=300,
                )
                st.plotly_chart(fig3, width="stretch", key="timeline")
            except Exception as e:
                st.warning(f"Couldn't draw the timeline: {e}")
    else:
        st.caption("No offers sent yet — analytics will fill in once you deploy some.")

with st.expander("📜  History — full log of every offer sent"):
    df = get_analytics()
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            if 'timestamp' in df.columns:
                try:
                    st.metric("Latest Action", pd.to_datetime(df['timestamp']).max().strftime("%Y-%m-%d %H:%M"))
                except Exception:
                    st.metric("Latest Action", "N/A")
            else:
                st.metric("Latest Action", "N/A")
        with col3:
            st.metric("Data Points", len(df.columns))

        display_df = df.copy()
        if 'timestamp' in display_df.columns:
            try:
                display_df = display_df.sort_values('timestamp', ascending=False)
            except Exception:
                pass
        st.dataframe(display_df, width="stretch", hide_index=True, height=420)
    else:
        st.caption("Nothing logged yet — every offer you send shows up here.")

with st.expander("🧪  Model evaluation — how accurate is the AI, really"):
    eval_data = get_model_evaluation()
    if not eval_data["available"]:
        st.warning(f"No live evaluation to show: {eval_data['reason']}")
        st.caption(
            "The dashboard falls back to a simple formula when the trained model "
            "isn't configured — set USE_ML_MODEL, HF_MODEL_REPO and HF_MODEL_REVISION "
            "in .env to point at a published model."
        )
    else:
        metrics = eval_data["metrics"]
        raw = eval_data["raw"]
        test_row = metrics["splits"][-1]

        badge_col, auc_col, formula_col = st.columns(3)
        with badge_col:
            st.metric("Model Version", metrics.get("model_version", "unknown"))
        with auc_col:
            st.metric("Test ROC-AUC (model)", f"{test_row['model']['roc_auc']:.4f}")
        with formula_col:
            delta = test_row['model']['roc_auc'] - test_row['old_formula_roc_auc']
            st.metric("Test ROC-AUC (old formula)", f"{test_row['old_formula_roc_auc']:.4f}",
                       delta=f"{delta:+.4f} vs. model", delta_color="inverse")

        st.caption("Both scores are computed on the same held-out test rows, for a fair comparison.")

        rows = []
        for split in metrics["splits"]:
            m = split["model"]
            rows.append({
                "split": split["split"], "n": split["n"], "accuracy": m["accuracy"],
                "precision": m["precision"], "recall": m["recall"], "f1": m["f1"],
                "roc_auc (model)": m["roc_auc"], "roc_auc (old formula)": split["old_formula_roc_auc"],
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown('<div class="section-head">Model vs. old formula (ROC-AUC)</div>', unsafe_allow_html=True)
            bar_df = pd.DataFrame(rows)
            fig_bar = go.Figure(data=[
                go.Bar(name="Model", x=bar_df["split"], y=bar_df["roc_auc (model)"], marker_color="#e2231a"),
                go.Bar(name="Old formula", x=bar_df["split"], y=bar_df["roc_auc (old formula)"], marker_color="#4a5568"),
            ])
            fig_bar.update_layout(
                barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family='Inter', color="#f3f5f8", size=12),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="ROC-AUC", range=[0, 1], color='#9aa3b2', zeroline=False),
                xaxis=dict(title="", color='#9aa3b2'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'),
                margin=dict(l=20, r=20, t=40, b=20), height=320,
            )
            st.plotly_chart(fig_bar, width="stretch", key="eval_auc_bar")

        with chart_col2:
            st.markdown('<div class="section-head">Top features (mean |SHAP|)</div>', unsafe_allow_html=True)
            top_features = metrics.get("top_features_test", [])
            if top_features:
                shap_df = pd.DataFrame(top_features).sort_values("mean_abs_shap")
                fig_shap = go.Figure(go.Bar(
                    x=shap_df["mean_abs_shap"], y=shap_df["feature"], orientation="h",
                    marker=dict(color=shap_df["mean_abs_shap"], colorscale=[[0, '#123244'], [1, '#38bdf8']], line=dict(color='rgba(0,0,0,0)')),
                ))
                fig_shap.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family='Inter', color="#f3f5f8", size=12),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="mean |SHAP value|", color='#9aa3b2', zeroline=False),
                    yaxis=dict(title="", color='#9aa3b2'),
                    margin=dict(l=20, r=20, t=20, b=20), height=320,
                )
                st.plotly_chart(fig_shap, width="stretch", key="eval_shap_bar")
            else:
                st.info("No SHAP summary published with this model version.")

        if raw is not None:
            y_true = np.array(raw["y_true"])
            y_proba = np.array(raw["model_proba"])

            st.markdown('<div class="section-head">ROC &amp; Precision-Recall (test set)</div>', unsafe_allow_html=True)
            curve_col1, curve_col2 = st.columns(2)

            thresholds = np.linspace(0.0, 1.0, 101)
            tprs, fprs, precisions, recalls = [], [], [], []
            P = y_true.sum()
            N = len(y_true) - P
            for t in thresholds:
                pred = (y_proba >= t).astype(int)
                tp = int(((pred == 1) & (y_true == 1)).sum())
                fp = int(((pred == 1) & (y_true == 0)).sum())
                tprs.append(tp / P if P else 0.0)
                fprs.append(fp / N if N else 0.0)
                precisions.append(tp / (tp + fp) if (tp + fp) else 1.0)
                recalls.append(tp / P if P else 0.0)

            with curve_col1:
                fig_roc = go.Figure()
                fig_roc.add_trace(go.Scatter(x=fprs, y=tprs, mode="lines", name="Model",
                                              line=dict(color="#e2231a", width=3), fill='tozeroy', fillcolor='rgba(226,35,26,0.08)'))
                fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random",
                                              line=dict(color="#4a5568", dash="dash", width=1.5)))
                fig_roc.update_layout(
                    title=dict(text="ROC curve", font=dict(size=13, color='#9aa3b2')),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family='Inter', color="#f3f5f8", size=12),
                    xaxis=dict(title="False Positive Rate", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#9aa3b2', zeroline=False),
                    yaxis=dict(title="True Positive Rate", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#9aa3b2', zeroline=False),
                    legend=dict(bgcolor='rgba(0,0,0,0)'), margin=dict(l=20, r=20, t=40, b=20), height=320,
                )
                st.plotly_chart(fig_roc, width="stretch", key="eval_roc")

            with curve_col2:
                fig_pr = go.Figure()
                fig_pr.add_trace(go.Scatter(x=recalls, y=precisions, mode="lines", name="Model",
                                             line=dict(color="#38bdf8", width=3), fill='tozeroy', fillcolor='rgba(56,189,248,0.08)'))
                fig_pr.update_layout(
                    title=dict(text="Precision-Recall curve", font=dict(size=13, color='#9aa3b2')),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family='Inter', color="#f3f5f8", size=12),
                    xaxis=dict(title="Recall", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#9aa3b2', zeroline=False),
                    yaxis=dict(title="Precision", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color='#9aa3b2', zeroline=False),
                    legend=dict(bgcolor='rgba(0,0,0,0)'), margin=dict(l=20, r=20, t=40, b=20), height=320,
                )
                st.plotly_chart(fig_pr, width="stretch", key="eval_pr")

            st.markdown('<div class="section-head">Confusion matrix (threshold = 0.5)</div>', unsafe_allow_html=True)
            pred_50 = (y_proba >= 0.5).astype(int)
            tp = int(((pred_50 == 1) & (y_true == 1)).sum())
            fp = int(((pred_50 == 1) & (y_true == 0)).sum())
            fn = int(((pred_50 == 0) & (y_true == 1)).sum())
            tn = int(((pred_50 == 0) & (y_true == 0)).sum())
            cm = [[tn, fp], [fn, tp]]
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm, x=["Pred: Stay", "Pred: Churn"], y=["Actual: Stay", "Actual: Churn"],
                text=cm, texttemplate="<b>%{text}</b>", textfont=dict(size=18, color="#ffffff"),
                colorscale=[[0, "#12151d"], [1, "#e2231a"]], showscale=False,
                hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
            ))
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family='Inter', color="#f3f5f8", size=12),
                margin=dict(l=20, r=20, t=20, b=20), height=300,
                xaxis=dict(color='#9aa3b2', side='bottom'), yaxis=dict(color='#9aa3b2', autorange='reversed'),
            )
            st.plotly_chart(fig_cm, width="stretch", key="eval_cm")
        else:
            st.info(
                "Per-row test predictions weren't published with this model version, so "
                "a real ROC/PR curve can't be drawn here — only the aggregate metrics above."
            )

with st.expander("🖥️  Agent activity log"):
    if st.session_state.agent_logs:
        for line in reversed(st.session_state.agent_logs[-20:]):
            st.text(line)
    else:
        st.caption("Nothing logged yet this session.")
