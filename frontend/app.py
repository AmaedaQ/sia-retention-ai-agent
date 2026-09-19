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
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from backend.agents.action import execute_retention_action
from backend.graph import retention_app
from config.settings import settings

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Retention AI | Jazz Telecom",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23E2231A'/><text x='16' y='22' text-anchor='middle' fill='white' font-family='system-ui' font-weight='700' font-size='17'>J</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM — "Neutral"
# ------------------------------------------------------------
# Restraint-first. One accent. Solid borders. No glow. No
# gradients on surfaces. The numbers do the talking.
# Backend calls / session state / data functions untouched.
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg:             #09090B;
    --surface:        #111113;
    --surface-2:      #18181B;
    --surface-3:      #212124;
    --border:         #1F1F23;
    --border-strong:  #2E2E33;
    --border-hover:   #3F3F46;

    --text:           #FAFAFA;
    --text-2:         #A1A1AA;
    --text-3:         #71717A;
    --text-4:         #52525B;

    --accent:         #E2231A;
    --accent-hover:   #F03B2E;
    --accent-soft:    rgba(226, 35, 26, 0.10);

    --success:        #22C55E;
    --warning:        #F59E0B;
    --danger:         #EF4444;
}

/* ============ BASE ============ */
[data-testid="stAppViewContainer"] {
    background: var(--bg);
}
.block-container {
    padding-top: 32px !important;
    padding-bottom: 80px !important;
    max-width: 1280px;
}
[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stToolbar"] { right: 12px; top: 8px; opacity: 0.4; transition: opacity 0.15s; }
[data-testid="stToolbar"]:hover { opacity: 1; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stStatusWidget"] { display: none !important; }

html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
}
.stApp, .stApp .stMarkdown, .stApp p,
.stApp label,
.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stWidgetLabel"],
.stApp button, .stApp input, .stApp textarea, .stApp select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text);
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.02em;
    font-weight: 600;
}
/* Never override Material Symbols used by native Streamlit icons */
.stApp [data-testid="stIconMaterial"],
.stApp span[data-testid="stIconMaterial"],
.stApp .material-symbols-rounded,
.stApp .material-symbols-outlined,
.stApp .material-icons,
.stApp [class*="material-symbols"],
.stApp [class*="material-icons"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-feature-settings: 'liga' !important;
}

/* ============ SIDEBAR ============ */
[data-testid="stSidebar"] {
    background: var(--bg);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 24px;
    padding-bottom: 24px;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] { z-index: 100 !important; }
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-3) !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: var(--surface-2) !important;
    border-color: var(--border-hover) !important;
    color: var(--text) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    color: currentColor !important;
    fill: currentColor !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-3) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    margin: 0 0 14px 0 !important;
}

/* Brand */
.brand {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 20px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
}
.brand-logo {
    width: 28px; height: 28px;
    border-radius: 6px;
    background: var(--accent);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 700; font-size: 15px;
    font-family: 'Inter', sans-serif;
    flex-shrink: 0;
}
.brand-name { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.2; }
.brand-meta { font-size: 11px; color: var(--text-4); margin-top: 2px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.2px; }

/* Log list — clean, no fake terminal chrome */
.log-list {
    display: flex; flex-direction: column;
    margin-bottom: 24px;
    max-height: 240px; overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--border-strong) transparent;
}
.log-list::-webkit-scrollbar { width: 4px; }
.log-list::-webkit-scrollbar-track { background: transparent; }
.log-list::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 2px; }
.log-item {
    display: flex; gap: 10px; align-items: baseline;
    padding: 7px 0;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
}
.log-item:last-child { border-bottom: none; }
.log-item .ts {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: var(--text-4);
    flex-shrink: 0;
    letter-spacing: -0.02em;
}
.log-item .msg { color: var(--text-2); line-height: 1.4; word-break: break-word; }
.log-item.err .msg { color: var(--danger); }
.log-item.warn .msg { color: var(--warning); }

/* Slider */
.stSlider { padding: 4px 0 12px 0; }
[data-testid="stSlider"] label {
    color: var(--text-3) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
    background: var(--accent) !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: #FFFFFF !important;
    border: 2px solid var(--accent) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
    width: 14px !important; height: 14px !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none; }
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
}

/* ============ BUTTONS ============ */
.stButton > button {
    width: 100%;
    background: var(--accent);
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 9px 14px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 13px;
    letter-spacing: -0.005em;
    transition: background 0.12s ease;
    box-shadow: none;
}
.stButton > button:hover {
    background: var(--accent-hover);
    transform: none;
    box-shadow: none;
}
.stButton > button:active { background: var(--accent); }
.stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--accent-soft);
}

/* Secondary buttons in the queue */
.btn-secondary .stButton > button {
    background: transparent;
    color: var(--text);
    border: 1px solid var(--border-strong);
    box-shadow: none;
}
.btn-secondary .stButton > button:hover {
    background: var(--surface-2);
    border-color: var(--border-hover);
    color: var(--text);
}

/* ============ HEADER ============ */
.page-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 24px;
    padding-bottom: 28px;
    margin-bottom: 32px;
    border-bottom: 1px solid var(--border);
}
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.025em; line-height: 1.2; margin: 0; }
.page-sub { font-size: 13px; color: var(--text-3); margin-top: 6px; line-height: 1.4; }
.status-row { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    height: 26px; padding: 0 10px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 100px;
    font-size: 11px; font-weight: 500;
    color: var(--text-2);
    white-space: nowrap;
}
.status-pill .dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--success);
}
.status-pill.accent .dot { background: var(--accent); }
.status-pill.muted .dot { background: var(--text-4); }

/* ============ TABS (Linear underline style) ============ */
.stTabs [data-baseweb="tab-list"] {
    gap: 28px;
    background: transparent;
    border-bottom: 1px solid var(--border);
    padding: 0;
    margin-bottom: 32px;
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: none;
    box-shadow: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    height: auto;
    background: transparent;
    border: none;
    border-radius: 0;
    color: var(--text-3);
    padding: 12px 0;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 13px;
    letter-spacing: 0;
    white-space: nowrap;
    transition: color 0.12s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-2);
    background: transparent;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--text);
    background: transparent;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: var(--accent) !important;
    height: 2px;
    border-radius: 0;
}
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ============ SECTION HEAD ============ */
.section {
    display: flex; align-items: baseline; gap: 10px;
    margin: 0 0 16px 0;
}
.section-title {
    font-size: 14px; font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
    margin: 0;
}
.section-meta {
    font-size: 12px;
    color: var(--text-4);
}
.section-count {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 500;
    color: var(--text-4);
    letter-spacing: -0.01em;
}

/* ============ KPI GRID ============ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 32px;
}
@media (max-width: 1000px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px)  { .kpi-grid { grid-template-columns: 1fr; } }
.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    transition: border-color 0.12s ease;
}
.kpi:hover { border-color: var(--border-strong); }
.kpi-label {
    font-size: 12px;
    color: var(--text-3);
    margin-bottom: 10px;
    font-weight: 500;
    letter-spacing: -0.005em;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 500;
    color: var(--text);
    line-height: 1.1;
    letter-spacing: -0.04em;
    font-variant-numeric: tabular-nums;
}
.kpi-value.danger { color: #F87171; }
.kpi-meta {
    font-size: 11px;
    color: var(--text-4);
    margin-top: 8px;
    line-height: 1.4;
}

/* ============ QUEUE ROW ============ */
.queue-list {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    background: var(--surface);
}
.queue-item {
    padding: 18px 20px;
    border-bottom: 1px solid var(--border);
    transition: background 0.12s ease;
}
.queue-item:last-child { border-bottom: none; }
.queue-item:hover { background: var(--surface-2); }
.queue-head {
    display: flex; align-items: center; gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
.q-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px; font-weight: 600;
    color: var(--text);
    letter-spacing: -0.02em;
}
.q-sep { color: var(--text-4); font-size: 12px; }
.q-plan {
    font-size: 12px;
    color: var(--text-3);
}
.badge {
    display: inline-flex; align-items: center;
    height: 20px; padding: 0 8px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 500;
    letter-spacing: -0.01em;
    white-space: nowrap;
}
.badge.high { background: rgba(239, 68, 68, 0.10); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.22); }
.badge.med  { background: rgba(245, 158, 11, 0.10); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.22); }
.badge.low  { background: rgba(34, 197, 94, 0.10); color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.22); }
.badge.offer {
    background: var(--accent-soft);
    color: #F87171;
    border: 1px solid rgba(226, 35, 26, 0.22);
}
.q-reason {
    font-size: 13px;
    color: var(--text-2);
    line-height: 1.55;
    max-width: 780px;
}
.q-reason .lbl {
    display: inline;
    color: var(--text-4);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-right: 8px;
}

/* ============ PLAN BARS ============ */
.plan-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.plan-row:last-child { border-bottom: none; }
.plan-name {
    width: 76px; flex-shrink: 0;
    font-size: 13px; font-weight: 500;
    color: var(--text);
    letter-spacing: -0.005em;
}
.plan-track {
    flex: 1; height: 4px;
    background: var(--surface-3);
    border-radius: 2px; overflow: hidden;
}
.plan-fill { height: 100%; border-radius: 2px; }
.plan-val {
    width: 40px; flex-shrink: 0; text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-3);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}

/* ============ MODEL CARD ============ */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
}
.card-label {
    font-size: 12px;
    color: var(--text-3);
    font-weight: 500;
    margin-bottom: 8px;
}
.card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 500;
    color: var(--text);
    letter-spacing: -0.02em;
}
.card-meta {
    font-size: 12px;
    color: var(--text-4);
    margin-top: 8px;
    line-height: 1.5;
}

/* ============ EMPTY PANEL ============ */
.empty {
    padding: 64px 32px;
    text-align: center;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
}
.empty-title {
    font-size: 14px; font-weight: 600;
    color: var(--text);
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}
.empty-desc {
    font-size: 13px;
    color: var(--text-3);
    line-height: 1.6;
    max-width: 420px;
    margin: 0 auto;
}

/* ============ TABLE ============ */
.table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}
.table-scroll {
    overflow: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--border-strong) transparent;
}
.table-scroll::-webkit-scrollbar { width: 8px; height: 8px; }
.table-scroll::-webkit-scrollbar-track { background: transparent; }
.table-scroll::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; }
table.dt {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13px;
    min-width: 560px;
}
table.dt thead th {
    position: sticky; top: 0;
    background: var(--surface-2);
    padding: 11px 16px;
    text-align: left;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-4);
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
    z-index: 2;
}
table.dt tbody td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    white-space: nowrap;
}
table.dt tbody tr:last-child td { border-bottom: none; }
table.dt tbody tr:hover td { background: rgba(255,255,255,0.015); }
table.dt td.mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text);
    letter-spacing: -0.02em;
}
table.dt td.muted { color: var(--text-3); }
table.dt td.num {
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-variant-numeric: tabular-nums;
    color: var(--text);
    letter-spacing: -0.02em;
}

/* ============ NATIVE METRICS ============ */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px 20px;
    transition: border-color 0.12s ease;
}
[data-testid="stMetric"]:hover { border-color: var(--border-strong); }
[data-testid="stMetric"] label {
    color: var(--text-3) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: none !important;
    letter-spacing: -0.005em !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 24px !important;
    font-weight: 500 !important;
    letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px !important;
    letter-spacing: -0.02em;
}

/* ============ CHARTS ============ */
[data-testid="stPlotlyChart"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px;
}
.js-plotly-plot { border-radius: 6px; overflow: hidden; }

/* ============ ALERTS / TOASTS ============ */
.stAlert {
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stAlert [data-testid="stMarkdownContainer"] p {
    color: var(--text-2) !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}
[data-testid="stToast"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}
[data-testid="stToast"] > div { color: var(--text) !important; font-size: 13px !important; }
[data-testid="stSpinner"] > div { border-top-color: var(--accent) !important; }

/* ============ DATAFRAME FALLBACK ============ */
[data-testid="stDataFrame"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}

/* ============ UTILITY SPACERS ============ */
.sp-1 { height: 8px; }
.sp-2 { height: 16px; }
.sp-3 { height: 24px; }
.sp-4 { height: 32px; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SVG ICONS (used sparingly — only where they earn their place)
# ============================================================
def _svg(path: str, size: int = 14) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


# ============================================================
# HELPERS
# ============================================================
def section(title, meta=None, count=None):
    meta_html = f'<span class="section-meta">{meta}</span>' if meta else ""
    count_html = f'<span class="section-count">{count}</span>' if count else ""
    return (
        f'<div class="section">'
        f'<div class="section-title">{title}</div>'
        f'{meta_html}{count_html}'
        f'</div>'
    )


def risk_badge(score):
    """Return a small badge for a churn score."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return ""
    if s >= 0.7:
        cls, label = "high", "High"
    elif s >= 0.5:
        cls, label = "med", "Medium"
    else:
        cls, label = "low", "Low"
    return f'<span class="badge {cls}">{label} {s:.2f}</span>'


def kpi(label, value, meta="", variant=""):
    return (
        f'<div class="kpi">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value {variant}">{value}</div>'
        f'<div class="kpi-meta">{meta}</div>'
        f'</div>'
    )


def empty_state(title, desc):
    return (
        f'<div class="empty">'
        f'<div class="empty-title">{title}</div>'
        f'<div class="empty-desc">{desc}</div>'
        f'</div>'
    )


def render_table(headers, rows, max_height=440):
    head_html = "".join([f"<th>{h}</th>" for h in headers])
    body_html = ""
    for row in rows:
        cells = "".join([f"<td class='{cls}'>{val}</td>" for val, cls in row])
        body_html += f"<tr>{cells}</tr>"
    return (
        f'<div class="table-wrap"><div class="table-scroll" style="max-height:{max_height}px;">'
        f'<table class="dt"><thead><tr>{head_html}</tr></thead>'
        f'<tbody>{body_html}</tbody></table></div></div>'
    )


def log_line(raw):
    s = str(raw)
    ts = ""
    msg = s
    if s.startswith("["):
        end = s.find("]")
        if end > 0:
            ts = s[1:end]
            msg = s[end + 1:].strip()
    low = msg.lower()
    cls = ""
    if any(k in low for k in ("error", "failed", "fail")):
        cls = "err"
    elif "warn" in low:
        cls = "warn"
    return f'<div class="log-item {cls}"><span class="ts">{ts}</span><span class="msg">{msg}</span></div>'


def plotly_base(fig, height=340):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#FAFAFA", size=12),
        margin=dict(l=16, r=16, t=16, b=16),
        height=height,
        showlegend=False,
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False, color="#71717A",
        linecolor="#1F1F23", tickfont=dict(size=11),
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="#1F1F23", gridwidth=1,
        zeroline=False, color="#71717A",
        linecolor="rgba(0,0,0,0)", tickfont=dict(size=11),
    )
    return fig


# ============================================================
# DATA UTILITIES (UNCHANGED)
# ============================================================
LOG_PATH = os.path.join(root_dir, "backend", "data", "action_logs.csv")
USER_DATA_PATH = os.path.join(root_dir, "backend", "data", "jazz_users.csv")

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = [
        "Retention AI System v2.0.1",
        "Initializing neural network...",
        "Loading customer behavior models...",
        "System ready for operation.",
    ]

if "results" not in st.session_state:
    st.session_state.results = None


def log_event(msg):
    ts = time.strftime("%H:%M:%S")
    st.session_state.agent_logs.append(f"[{ts}] {msg}")
    if len(st.session_state.agent_logs) > 50:
        st.session_state.agent_logs = st.session_state.agent_logs[-50:]


def risk_tier(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "Unknown", "med"
    if score >= 0.7:
        return "High", "high"
    if score >= 0.5:
        return "Medium", "med"
    return "Low", "low"


@st.cache_data(ttl=60)
def get_analytics():
    if os.path.exists(LOG_PATH) and os.path.exists(USER_DATA_PATH):
        try:
            logs = pd.read_csv(LOG_PATH)
            users = pd.read_csv(USER_DATA_PATH)
            if not logs.empty and not users.empty:
                return pd.merge(logs, users, on="user_id", how="left")
        except Exception as e:
            log_event(f"Error loading analytics: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=60)
def get_portfolio():
    if os.path.exists(USER_DATA_PATH):
        try:
            df = pd.read_csv(USER_DATA_PATH)
            if not df.empty:
                return df
        except Exception as e:
            log_event(f"Error loading portfolio: {str(e)}")
    return pd.DataFrame()


@st.cache_data(ttl=300)
def get_model_evaluation():
    if not settings.use_ml_model:
        return {"available": False, "reason": "USE_ML_MODEL is off -- scoring with original formula.", "metrics": None, "raw": None}
    if not settings.hf_model_repo:
        return {"available": False, "reason": "HF_MODEL_REPO is not configured.", "metrics": None, "raw": None}
    try:
        import json as _json

        from huggingface_hub import hf_hub_download

        metrics_path = hf_hub_download(
            repo_id=settings.hf_model_repo,
            filename="metrics.json",
            revision=settings.hf_model_revision,
        )
        with open(metrics_path) as f:
            metrics = _json.load(f)
        raw = None
        try:
            raw_path = hf_hub_download(
                repo_id=settings.hf_model_repo,
                filename="test_raw.json",
                revision=settings.hf_model_revision,
            )
            with open(raw_path) as f:
                raw = _json.load(f)
        except Exception:
            pass
        return {"available": True, "reason": None, "metrics": metrics, "raw": raw}
    except Exception as e:
        return {"available": False, "reason": f"could not fetch published evaluation artifacts: {e}", "metrics": None, "raw": None}


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-logo">J</div>
            <div>
                <div class="brand-name">Retention AI</div>
                <div class="brand-meta">JAZZ · v2.0.1</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Agent log")
    logs_html = "".join([log_line(x) for x in st.session_state.agent_logs[-12:]])
    st.markdown(f'<div class="log-list">{logs_html}</div>', unsafe_allow_html=True)

    st.markdown("### Risk threshold")

    threshold = st.slider(
        "Flag threshold",
        min_value=0.40, max_value=0.95, value=0.70, step=0.05,
        help="Customers scoring at or above this value are flagged.",
        label_visibility="collapsed",
    )

    if st.button("Run network scan", key="run_scan_btn"):
        log_event("Initiating network scan...")
        with st.spinner("Scanning portfolio..."):
            try:
                results = retention_app.invoke(
                    {"threshold": threshold, "risky_users": [], "final_reports": []}
                )
                st.session_state.results = results
                n = len(results.get("risky_users", []))
                log_event(f"Scan complete: {n} customers flagged")
                get_analytics.clear()
            except Exception as e:
                log_event(f"Scan error: {str(e)}")
                st.error(f"Scan failed: {str(e)}")
        st.rerun()


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="page-head">
        <div>
            <div class="page-title">Retention AI</div>
            <div class="page-sub">Customer retention intelligence for Jazz Telecom</div>
        </div>
        <div class="status-row">
            <div class="status-pill accent"><span class="dot"></span>Operational</div>
            <div class="status-pill"><span class="dot"></span>LangGraph</div>
            <div class="status-pill muted"><span class="dot"></span>v2.0.1</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================
tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["Dashboard", "Queue", "Analytics", "History", "Evaluation"]
)


# ============================================================
# TAB 0: DASHBOARD
# ============================================================
with tab0:
    portfolio = get_portfolio()
    logs_df = get_analytics()

    if portfolio.empty:
        st.markdown(
            empty_state(
                "No customer data",
                "backend/data/jazz_users.csv was not found or is empty. Load the portfolio to begin.",
            ),
            unsafe_allow_html=True,
        )
    else:
        at_risk_df = (
            portfolio[portfolio["churn_risk_score"] >= threshold]
            if "churn_risk_score" in portfolio.columns
            else portfolio.iloc[0:0]
        )
        at_risk_count = len(at_risk_df)
        revenue_at_risk = (
            at_risk_df["avg_monthly_spend"].sum()
            if "avg_monthly_spend" in at_risk_df.columns
            else 0.0
        )
        offers_sent_total = len(logs_df) if not logs_df.empty else 0
        reach_pct = round(100.0 * offers_sent_total / at_risk_count, 1) if at_risk_count else 0

        st.markdown(
            '<div class="kpi-grid">'
            + kpi("Total customers", f"{len(portfolio):,}", "in the active portfolio")
            + kpi("At risk", f"{at_risk_count:,}", f"scoring at ≥{threshold:.0%}", variant="danger" if at_risk_count else "")
            + kpi("Monthly spend at risk", f"{revenue_at_risk:,.0f}", "combined avg. monthly spend")
            + kpi("Offers sent", f"{offers_sent_total}", f"{reach_pct}% of at-risk reached")
            + '</div>',
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.6, 1], gap="large")

        with left:
            st.markdown(
                section("Highest-risk customers", "Top 10 by churn probability", count="TOP 10"),
                unsafe_allow_html=True,
            )
            top_risk = portfolio.nlargest(10, "churn_risk_score")
            rows = []
            for _, r in top_risk.iterrows():
                uid = str(r.get("user_id", "—"))
                plan = str(r.get("active_plan", "—")) if "active_plan" in r else "—"
                spend = f"{float(r.get('avg_monthly_spend', 0)):,.0f}" if "avg_monthly_spend" in r else "—"
                days = f"{int(r.get('days_since_last_recharge', 0))}" if "days_since_last_recharge" in r else "—"
                score = r.get("churn_risk_score", None)
                rows.append([
                    (uid, "mono"),
                    (plan, "muted"),
                    (spend, "num"),
                    (days, "num"),
                    (risk_badge(score), ""),
                ])
            st.markdown(
                render_table(
                    ["Customer", "Plan", "Spend / mo", "Days idle", "Risk"],
                    rows, max_height=440,
                ),
                unsafe_allow_html=True,
            )

        with right:
            st.markdown(
                section("Avg. risk by plan", "Mean churn score"),
                unsafe_allow_html=True,
            )
            if "active_plan" in portfolio.columns and "churn_risk_score" in portfolio.columns:
                plan_risk = (
                    portfolio.groupby("active_plan")["churn_risk_score"]
                    .mean()
                    .sort_values(ascending=False)
                )
                colors = {"Premium": "#E2231A", "Flexi": "#F59E0B", "Standard": "#22C55E"}
                rows_html = ""
                for plan, val in plan_risk.items():
                    pct = min(100, max(0, val * 100))
                    color = colors.get(plan, "#71717A")
                    rows_html += (
                        f'<div class="plan-row">'
                        f'<div class="plan-name">{plan}</div>'
                        f'<div class="plan-track"><div class="plan-fill" style="width:{pct}%;background:{color}"></div></div>'
                        f'<div class="plan-val">{val:.2f}</div>'
                        f'</div>'
                    )
                st.markdown(rows_html, unsafe_allow_html=True)
            else:
                st.caption("Plan breakdown unavailable.")

            st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
            st.markdown(section("Model"), unsafe_allow_html=True)
            _eval = get_model_evaluation()
            if _eval["available"]:
                _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                ver = _eval["metrics"].get("model_version", "v1.0.0")
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-label">Scoring with</div>'
                    f'<div class="card-value">{ver}</div>'
                    f'<div class="card-meta">Test ROC-AUC {_test_auc:.3f}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-label">Scoring mode</div>'
                    f'<div class="card-value">Formula</div>'
                    f'<div class="card-meta">{_eval["reason"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# TAB 1: QUEUE
# ============================================================
with tab1:
    if st.session_state.results is not None:
        final_reports = st.session_state.results.get("final_reports", [])
        active_reports = [r for r in final_reports if r.get("status") != "deployed"] if final_reports else []

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Flagged", len(st.session_state.results.get("risky_users", [])))
        with col2:
            st.metric("In queue", len(active_reports))
        with col3:
            _eval = get_model_evaluation()
            if _eval["available"]:
                _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                st.metric("Test ROC-AUC", f"{_test_auc:.3f}")
            else:
                st.metric("Scoring mode", "Formula")
        with col4:
            st.metric("AI status", "Active")

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)

        st.markdown(
            section("Deployment queue", "Flagged customers awaiting action", count=f"{len(active_reports)} pending"),
            unsafe_allow_html=True,
        )

        if active_reports:
            risky_by_id = {
                str(u.get("user_id")): u.get("churn_risk_score")
                for u in st.session_state.results.get("risky_users", [])
            }
            for report in active_reports:
                user_id = report.get("user_id", "N/A")
                offer = report.get("offer", "N/A")
                reasoning = report.get("reasoning", "No reasoning provided")
                risk_score = risky_by_id.get(str(user_id))
                risk_badge_html = risk_badge(risk_score) if risk_score is not None else ""

                c_row, c_btn = st.columns([8, 1.4])

                with c_row:
                    st.markdown(
                        f'<div class="queue-list"><div class="queue-item">'
                        f'<div class="queue-head">'
                        f'<span class="q-id">{user_id}</span>'
                        f'<span class="q-sep">·</span>'
                        f'<span class="q-plan">Retention target</span>'
                        f'{risk_badge_html}'
                        f'<span class="badge offer">{offer}</span>'
                        f'</div>'
                        f'<div class="q-reason"><span class="lbl">Agent</span>{reasoning}</div>'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )

                with c_btn:
                    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
                    if st.button("Deploy", key=f"deploy_{user_id}"):
                        try:
                            success = execute_retention_action(report)
                            if success:
                                log_event(f"Deployed strategy for {user_id}")
                                st.toast(f"Deployed for {user_id}")
                                time.sleep(0.5)
                                get_analytics.clear()
                                st.rerun()
                            else:
                                log_event(f"Failed to deploy strategy for {user_id}")
                                st.toast(f"Deployment failed for {user_id}")
                        except Exception as e:
                            log_event(f"Error deploying for {user_id}: {str(e)}")
                            st.error(f"Deployment error: {str(e)}")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<div class='sp-1'></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                empty_state(
                    "Queue is clear",
                    "Every flagged customer has been processed. Run a new scan to refresh the risk pool.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown("<div class='sp-2'></div>", unsafe_allow_html=True)
            _, mid, _ = st.columns([1, 1, 1])
            with mid:
                if st.button("Scan for new targets", key="rescan_button"):
                    log_event("Initiating new network scan...")
                    with st.spinner("Scanning for new targets..."):
                        try:
                            results = retention_app.invoke(
                                {"threshold": threshold, "risky_users": [], "final_reports": []}
                            )
                            st.session_state.results = results
                            log_event(f"Rescan complete: {len(results.get('risky_users', []))} customers found")
                            get_analytics.clear()
                        except Exception as e:
                            log_event(f"Rescan error: {str(e)}")
                            st.error(f"Rescan failed: {str(e)}")
                    st.rerun()
    else:
        st.markdown(
            empty_state(
                "No scan on record",
                "Use the Control Panel in the sidebar to initiate your first network scan. "
                "The system will surface at-risk customers and generate retention strategies.",
            ),
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 2: ANALYTICS
# ============================================================
with tab2:
    analytics_df = get_analytics()

    if not analytics_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total actions", len(analytics_df))
        with col2:
            if "churn_risk_score" in analytics_df.columns:
                st.metric("Avg risk score", f"{analytics_df['churn_risk_score'].mean():.2f}")
            else:
                st.metric("Avg risk score", "N/A")
        with col3:
            st.metric("Unique customers", analytics_df["user_id"].nunique())
        with col4:
            if "offer_sent" in analytics_df.columns and not analytics_df["offer_sent"].empty:
                mode_offers = analytics_df["offer_sent"].mode()
                most_common = mode_offers[0] if len(mode_offers) > 0 else "N/A"
                st.metric("Most common offer", most_common)
            else:
                st.metric("Most common offer", "N/A")

        st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(section("Offer distribution"), unsafe_allow_html=True)
            if "offer_sent" in analytics_df.columns:
                fig = px.pie(
                    analytics_df, names="offer_sent", hole=0.72,
                    color_discrete_sequence=["#E2231A", "#F59E0B", "#22C55E", "#71717A", "#52525B"],
                )
                fig.update_traces(
                    textposition="outside",
                    textinfo="percent",
                    textfont=dict(size=11, color="#A1A1AA", family="JetBrains Mono"),
                    marker=dict(line=dict(color="#111113", width=2)),
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#FAFAFA", size=12),
                    showlegend=True,
                    legend=dict(
                        orientation="v", yanchor="middle", y=0.5,
                        xanchor="left", x=1.02,
                        bgcolor="rgba(0,0,0,0)",
                        font=dict(size=11, color="#A1A1AA"),
                        itemsizing="constant",
                    ),
                    margin=dict(l=16, r=16, t=16, b=16),
                    height=320,
                )
                st.plotly_chart(fig, width="stretch", key="offer_pie")
            else:
                st.caption("No offer data.")

        with col2:
            st.markdown(section("Risk score distribution"), unsafe_allow_html=True)
            if "churn_risk_score" in analytics_df.columns:
                fig2 = px.histogram(
                    analytics_df, x="churn_risk_score", nbins=20,
                    color_discrete_sequence=["#E2231A"],
                )
                fig2.update_traces(marker=dict(line=dict(color="#111113", width=1)), opacity=0.85)
                fig2 = plotly_base(fig2, height=320)
                fig2.update_xaxes(title="Churn risk score", color="#71717A")
                fig2.update_yaxes(title="Customers", color="#71717A")
                st.plotly_chart(fig2, width="stretch", key="risk_hist")

        st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)

        st.markdown(section("Activity timeline", "Deployment volume over time"), unsafe_allow_html=True)
        if "timestamp" in analytics_df.columns:
            try:
                analytics_df["date"] = pd.to_datetime(analytics_df["timestamp"]).dt.date
                timeline_data = analytics_df.groupby("date").size().reset_index(name="actions")
                fig3 = px.line(timeline_data, x="date", y="actions", color_discrete_sequence=["#E2231A"])
                fig3.update_traces(
                    line=dict(width=2), mode="lines+markers",
                    marker=dict(size=6, color="#E2231A", line=dict(color="#111113", width=2)),
                )
                fig3 = plotly_base(fig3, height=280)
                fig3.update_xaxes(title="", color="#71717A")
                fig3.update_yaxes(title="Actions", color="#71717A")
                st.plotly_chart(fig3, width="stretch", key="timeline")
            except Exception as e:
                log_event(f"Error creating timeline: {str(e)}")
                st.warning("Unable to display timeline chart")
    else:
        st.markdown(
            empty_state(
                "No analytics yet",
                "Run a network scan and deploy retention strategies to generate insight into offer performance and risk distribution.",
            ),
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 3: HISTORY
# ============================================================
with tab3:
    df = get_analytics()

    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total records", len(df))
        with col2:
            if "timestamp" in df.columns:
                try:
                    latest = pd.to_datetime(df["timestamp"]).max()
                    st.metric("Latest action", latest.strftime("%Y-%m-%d %H:%M"))
                except Exception:
                    st.metric("Latest action", "N/A")
            else:
                st.metric("Latest action", "N/A")
        with col3:
            st.metric("Data points", len(df.columns))

        st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)

        st.markdown(
            section("Audit trail", "Every deployed action, newest first", count=f"{len(df)} records"),
            unsafe_allow_html=True,
        )

        display_df = df.copy()
        if "timestamp" in display_df.columns:
            try:
                display_df = display_df.sort_values("timestamp", ascending=False)
            except Exception:
                pass

        cols = list(display_df.columns)
        headers = [c.replace("_", " ").title() for c in cols]
        rows = []
        for _, r in display_df.head(500).iterrows():
            cells = []
            for c in cols:
                v = r.get(c, "")
                if pd.isna(v):
                    v = "—"
                s = str(v)
                if len(s) > 42:
                    s = s[:39] + "…"
                if c in ("user_id", "timestamp"):
                    cls = "mono"
                elif any(k in c.lower() for k in ("spend", "score", "risk", "amount", "days")):
                    cls = "num"
                else:
                    cls = "muted"
                cells.append((s, cls))
            rows.append(cells)
        st.markdown(render_table(headers, rows, max_height=580), unsafe_allow_html=True)
    else:
        st.markdown(
            empty_state(
                "No history yet",
                "Execute retention actions to build your audit trail. Every deployment is logged here for compliance and review.",
            ),
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 4: EVALUATION
# ============================================================
with tab4:
    eval_data = get_model_evaluation()

    if not eval_data["available"]:
        st.warning(f"No live model evaluation to show: {eval_data['reason']}")
        st.markdown(
            "The dashboard falls back to the original hand-written formula "
            "(`backend/data_generator.py`) whenever the trained model isn't "
            "configured or reachable — that's by design (`USE_ML_MODEL` in "
            "`config/settings.py`). Set `USE_ML_MODEL=true`, "
            "`HF_MODEL_REPO`, and `HF_MODEL_REVISION` in `.env` to point at a "
            "published model and this tab will populate with its real metrics."
        )
    else:
        metrics = eval_data["metrics"]
        raw = eval_data["raw"]
        test_row = metrics["splits"][-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model version", metrics.get("model_version", "unknown"))
        with col2:
            st.metric("Test ROC-AUC (model)", f"{test_row['model']['roc_auc']:.4f}")
        with col3:
            delta = test_row["model"]["roc_auc"] - test_row["old_formula_roc_auc"]
            st.metric(
                "Test ROC-AUC (old formula)",
                f"{test_row['old_formula_roc_auc']:.4f}",
                delta=f"{delta:+.4f}",
                delta_color="inverse",
            )

        st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)

        st.markdown(section("Metrics by split"), unsafe_allow_html=True)

        rows_data = []
        html_rows = []
        for split in metrics["splits"]:
            m = split["model"]
            rows_data.append({
                "split": split["split"], "n": split["n"],
                "accuracy": m["accuracy"], "precision": m["precision"],
                "recall": m["recall"], "f1": m["f1"],
                "roc_auc (model)": m["roc_auc"],
                "roc_auc (old formula)": split["old_formula_roc_auc"],
            })
            html_rows.append([
                (split["split"], "mono"),
                (f"{split['n']:,}", "num"),
                (f"{m['accuracy']:.3f}", "num"),
                (f"{m['precision']:.3f}", "num"),
                (f"{m['recall']:.3f}", "num"),
                (f"{m['f1']:.3f}", "num"),
                (f"{m['roc_auc']:.3f}", "num"),
                (f"{split['old_formula_roc_auc']:.3f}", "num"),
            ])
        st.markdown(
            render_table(
                ["Split", "N", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC (model)", "ROC-AUC (old)"],
                html_rows, max_height=300,
            ),
            unsafe_allow_html=True,
        )

        st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2, gap="large")
        with chart_col1:
            st.markdown(section("Model vs. formula", "ROC-AUC per split"), unsafe_allow_html=True)
            bar_df = pd.DataFrame(rows_data)
            fig_bar = go.Figure(data=[
                go.Bar(name="Model", x=bar_df["split"], y=bar_df["roc_auc (model)"], marker_color="#E2231A"),
                go.Bar(name="Old formula", x=bar_df["split"], y=bar_df["roc_auc (old formula)"], marker_color="#3F3F46"),
            ])
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#FAFAFA", size=12),
                yaxis=dict(showgrid=True, gridcolor="#1F1F23", title="", range=[0, 1], color="#71717A", zeroline=False),
                xaxis=dict(title="", color="#71717A"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#A1A1AA")),
                margin=dict(l=16, r=16, t=32, b=16), height=320,
                bargap=0.35, bargroupgap=0.08,
            )
            st.plotly_chart(fig_bar, width="stretch", key="eval_auc_bar")

        with chart_col2:
            st.markdown(section("Top features", "Mean |SHAP| on test split"), unsafe_allow_html=True)
            top_features = metrics.get("top_features_test", [])
            if top_features:
                shap_df = pd.DataFrame(top_features).sort_values("mean_abs_shap")
                fig_shap = go.Figure(go.Bar(
                    x=shap_df["mean_abs_shap"], y=shap_df["feature"], orientation="h",
                    marker=dict(color="#E2231A", line=dict(color="rgba(0,0,0,0)")),
                ))
                fig_shap.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#FAFAFA", size=12),
                    xaxis=dict(showgrid=True, gridcolor="#1F1F23", title="", color="#71717A", zeroline=False),
                    yaxis=dict(title="", color="#A1A1AA", tickfont=dict(size=11)),
                    margin=dict(l=16, r=16, t=16, b=16), height=320,
                    bargap=0.4,
                )
                st.plotly_chart(fig_shap, width="stretch", key="eval_shap_bar")
            else:
                st.caption("No SHAP summary published with this model version.")

        if raw is not None:
            st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)

            y_true = np.array(raw["y_true"])
            y_proba = np.array(raw["model_proba"])

            curve_col1, curve_col2 = st.columns(2, gap="large")
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
                st.markdown(section("ROC curve"), unsafe_allow_html=True)
                fig_roc = go.Figure()
                fig_roc.add_trace(go.Scatter(
                    x=fprs, y=tprs, mode="lines", name="Model",
                    line=dict(color="#E2231A", width=2),
                ))
                fig_roc.add_trace(go.Scatter(
                    x=[0, 1], y=[0, 1], mode="lines", name="Baseline",
                    line=dict(color="#3F3F46", dash="dash", width=1),
                ))
                fig_roc.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#FAFAFA", size=12),
                    xaxis=dict(title="", showgrid=True, gridcolor="#1F1F23", color="#71717A", zeroline=False),
                    yaxis=dict(title="", showgrid=True, gridcolor="#1F1F23", color="#71717A", zeroline=False),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#A1A1AA"), orientation="h", y=1.02, x=0),
                    margin=dict(l=16, r=16, t=32, b=16), height=320,
                )
                st.plotly_chart(fig_roc, width="stretch", key="eval_roc")

            with curve_col2:
                st.markdown(section("Precision-Recall curve"), unsafe_allow_html=True)
                fig_pr = go.Figure()
                fig_pr.add_trace(go.Scatter(
                    x=recalls, y=precisions, mode="lines", name="Model",
                    line=dict(color="#E2231A", width=2),
                ))
                fig_pr.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#FAFAFA", size=12),
                    xaxis=dict(title="Recall", showgrid=True, gridcolor="#1F1F23", color="#71717A", zeroline=False),
                    yaxis=dict(title="Precision", showgrid=True, gridcolor="#1F1F23", color="#71717A", zeroline=False),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#A1A1AA"), orientation="h", y=1.02, x=0),
                    margin=dict(l=16, r=16, t=32, b=16), height=320,
                )
                st.plotly_chart(fig_pr, width="stretch", key="eval_pr")

            st.markdown("<div class='sp-4'></div>", unsafe_allow_html=True)
            st.markdown(section("Confusion matrix", "Test split, threshold = 0.5"), unsafe_allow_html=True)
            pred_50 = (y_proba >= 0.5).astype(int)
            tp = int(((pred_50 == 1) & (y_true == 1)).sum())
            fp = int(((pred_50 == 1) & (y_true == 0)).sum())
            fn = int(((pred_50 == 0) & (y_true == 1)).sum())
            tn = int(((pred_50 == 0) & (y_true == 0)).sum())
            cm = [[tn, fp], [fn, tp]]
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm, x=["Pred: Stay", "Pred: Churn"], y=["Actual: Stay", "Actual: Churn"],
                text=cm, texttemplate="%{text}",
                textfont=dict(size=16, color="#FAFAFA", family="JetBrains Mono"),
                colorscale=[[0, "#18181B"], [1, "#7A1410"]],
                showscale=False,
                hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
            ))
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#FAFAFA", size=12),
                margin=dict(l=16, r=16, t=16, b=16), height=280,
                xaxis=dict(color="#71717A", side="bottom"),
                yaxis=dict(color="#71717A", autorange="reversed"),
            )
            st.plotly_chart(fig_cm, width="stretch", key="eval_cm")
        else:
            st.info(
                "Per-row test predictions (`test_raw.json`) weren't published with "
                "this model version, so ROC/PR curves and confusion matrix "
                "can't be drawn — only the aggregate metrics above. "
                "Re-run `notebooks/02_train_model.py` and re-publish to unlock this section."
            )
