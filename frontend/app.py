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
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%23e2231a'/><text y='.92em' font-size='72' x='50%' text-anchor='middle' fill='white' font-family='system-ui' font-weight='800'>R</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM — Signal Room v5
# ------------------------------------------------------------
# Fixes vs. v4:
#   1. Font rule is TARGETED (not universal) → sidebar chevron
#      now renders correctly (was being crushed by Inter override).
#   2. KPI tiles use min-height only, not fixed → no clipping.
#   3. Tab bar scrolls horizontally on narrow viewports.
#   4. Deeper surface hierarchy + accent glow rhythm.
#   5. Sidebar collapse button is explicitly restyled and visible.
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

/* ============================================================
   1. DESIGN TOKENS
   ============================================================ */
:root {
    --primary:        #e2231a;
    --primary-soft:   #ff5c50;
    --primary-dim:    rgba(226, 35, 26, 0.14);
    --primary-glow:   rgba(226, 35, 26, 0.35);
    --accent:         #22d3ee;
    --accent-dim:     rgba(34, 211, 238, 0.14);
    --accent-glow:    rgba(34, 211, 238, 0.35);
    --success:        #2dd4a7;
    --success-dim:    rgba(45, 212, 167, 0.14);
    --warning:        #f2a93c;
    --warning-dim:    rgba(242, 169, 60, 0.14);
    --bg-0:           #06070b;
    --bg-1:           #0a0c11;
    --bg-card:        #0f1218;
    --bg-elevated:    #161a24;
    --bg-hover:       #1b2030;
    --border:         rgba(255, 255, 255, 0.055);
    --border-strong:  rgba(255, 255, 255, 0.11);
    --text-primary:   #eef0f4;
    --text-secondary: #8c93a4;
    --text-muted:     #555c6c;
    --radius:         14px;
    --radius-sm:      10px;
    --radius-xs:      8px;
    --shadow-sm:      0 1px 2px rgba(0,0,0,0.3);
    --shadow:         0 4px 16px rgba(0,0,0,0.35);
    --shadow-lg:      0 12px 40px rgba(0,0,0,0.45);
}

/* ============================================================
   2. CANVAS & GLOBAL RESET
   ============================================================ */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 55% at 8% -8%, rgba(226,35,26,0.10), transparent 55%),
        radial-gradient(ellipse 60% 50% at 95% 4%, rgba(34,211,238,0.07), transparent 55%),
        var(--bg-0);
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed; inset: 0;
    background-image: radial-gradient(rgba(255,255,255,0.035) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
    z-index: 0;
    mask-image: radial-gradient(ellipse at 50% 0%, black 20%, transparent 75%);
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1380px;
    position: relative;
    z-index: 1;
}
[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stToolbar"] { right: 1rem; top: 0.75rem; }
[data-testid="stSidebarNav"] { display: none; }

/* ============================================================
   3. TYPOGRAPHY (TARGETED — do not use universal selectors,
      they crush Material Symbols icon font used by Streamlit)
   ============================================================ */
html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}
.stApp,
.stApp .stMarkdown,
.stApp p,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp label,
.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stWidgetLabel"],
.stApp button,
.stApp input,
.stApp textarea,
.stApp select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    font-family: 'Sora', sans-serif;
    letter-spacing: -0.02em;
}

/* RESTORE Material Symbols so icons (sidebar chevron, expanders,
   slider handles, etc.) render as glyphs — not tofu boxes. */
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

/* ============================================================
   4. SIDEBAR
   ============================================================ */
[data-testid="stSidebar"] {
    background: var(--bg-1);
    border-right: 1px solid var(--border);
    box-shadow: inset -1px 0 0 rgba(255,255,255,0.02);
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.1rem;
    padding-bottom: 1.5rem;
}

/* Make the collapse chevron explicitly visible + on-theme */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
    z-index: 100 !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--border-strong) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    color: currentColor !important;
    fill: currentColor !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-muted) !important;
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    margin: 0 0 0.85rem 0 !important;
    padding-bottom: 0.55rem;
    border-bottom: 1px solid var(--border);
}

/* Brand block */
.brand-block {
    display: flex; align-items: center; gap: 11px;
    padding: 0 0 1.1rem 0;
    margin-bottom: 1.1rem;
    border-bottom: 1px solid var(--border);
}
.brand-mark {
    width: 40px; height: 40px; border-radius: 11px;
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.06);
}
.brand-mark img { width: 26px; height: 26px; object-fit: contain; }
.brand-name {
    font-family: 'Sora', sans-serif;
    font-size: 0.92rem; font-weight: 700;
    color: var(--text-primary); line-height: 1.15;
    letter-spacing: -0.01em;
}
.brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; color: var(--text-muted);
    letter-spacing: 0.6px; margin-top: 2px;
}

/* Terminal */
.terminal-shell {
    background: #050608;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.terminal-bar {
    display: flex; align-items: center; gap: 5px;
    padding: 8px 11px;
    background: #0a0c10;
    border-bottom: 1px solid var(--border);
}
.terminal-dot { width: 8px; height: 8px; border-radius: 50%; }
.terminal-dot.r { background: #ff5f57; }
.terminal-dot.y { background: #febc2e; }
.terminal-dot.g { background: #28c840; }
.terminal-title {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.56rem; color: var(--text-muted);
    letter-spacing: 0.7px; text-transform: uppercase;
}
.terminal-box {
    padding: 11px 12px 13px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: var(--success);
    height: 220px;
    overflow-y: auto;
    line-height: 1.65;
    scrollbar-width: thin;
    scrollbar-color: var(--primary) transparent;
}
.terminal-box::-webkit-scrollbar { width: 4px; }
.terminal-box::-webkit-scrollbar-track { background: transparent; }
.terminal-box::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 2px; }
.terminal-line { margin-bottom: 3px; white-space: pre-wrap; word-break: break-word; }
.terminal-line::before { content: "> "; color: var(--primary-soft); font-weight: 700; }

/* Slider */
.stSlider { padding: 0.2rem 0 0.65rem 0; }
[data-testid="stSlider"] label {
    color: var(--text-secondary) !important;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div { background: var(--primary) !important; }
[data-testid="stSlider"] [role="slider"] {
    background: #fff !important;
    border: 2px solid var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(226,35,26,0.20) !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none; }
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: var(--primary) !important;
    color: white !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    border-radius: 5px !important;
    padding: 1px 6px !important;
}

/* ============================================================
   5. BUTTONS
   ============================================================ */
.stButton > button {
    width: 100%;
    background: linear-gradient(180deg, #ef2a20 0%, #c81a12 100%);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: var(--radius-xs);
    padding: 0.66rem 1rem;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.76rem;
    letter-spacing: 0.2px;
    transition: all 0.15s ease;
    box-shadow: 0 1px 0 rgba(255,255,255,0.10) inset, 0 6px 16px rgba(226,35,26,0.25);
}
.stButton > button:hover {
    background: linear-gradient(180deg, #ff3a2f 0%, #d41d14 100%);
    transform: translateY(-1px);
    box-shadow: 0 1px 0 rgba(255,255,255,0.14) inset, 0 10px 24px rgba(226,35,26,0.35);
}
.stButton > button:active { transform: translateY(0); }
.stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 3px rgba(226,35,26,0.25), 0 6px 16px rgba(226,35,26,0.25);
}

.deploy-btn .stButton > button {
    background: transparent;
    border: 1px solid rgba(226,35,26,0.45);
    color: #ff8a82;
    box-shadow: none;
}
.deploy-btn .stButton > button:hover {
    background: linear-gradient(180deg, #ef2a20 0%, #c81a12 100%);
    color: #fff;
    border-color: var(--primary);
    box-shadow: 0 8px 20px rgba(226,35,26,0.30);
}

/* ============================================================
   6. HERO HEADER
   ============================================================ */
.hero {
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 1.5rem; flex-wrap: wrap;
    padding: 0 0 1.35rem 0;
    margin-bottom: 1.35rem;
    border-bottom: 1px solid var(--border);
    position: relative;
}
.hero::after {
    content: "";
    position: absolute; left: 0; bottom: -1px; width: 140px; height: 1px;
    background: linear-gradient(90deg, var(--primary), transparent);
    box-shadow: 0 0 12px var(--primary-glow);
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.95rem; font-weight: 800;
    letter-spacing: -0.6px; line-height: 1.05;
    color: var(--text-primary); margin: 0;
}
.hero-title .accent {
    color: var(--primary);
    text-shadow: 0 0 30px rgba(226,35,26,0.35);
}
.hero-sub {
    color: var(--text-secondary);
    font-size: 0.86rem; margin-top: 0.35rem;
    letter-spacing: 0.1px;
}
.hero-meta { display: flex; gap: 0.45rem; flex-wrap: wrap; align-items: center; }

.pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border-strong);
    padding: 0.42rem 0.75rem;
    border-radius: 100px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 600;
    letter-spacing: 0.6px; text-transform: uppercase;
    color: var(--text-secondary);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}
.pill .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
    animation: pulse 2.4s ease-in-out infinite;
}
.pill.accent { border-color: rgba(34,211,238,0.25); }
.pill.accent .dot { background: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
.pill.primary { border-color: rgba(226,35,26,0.30); }
.pill.primary .dot { background: var(--primary); box-shadow: 0 0 8px var(--primary-glow); }
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.5; transform: scale(0.9); }
}

/* ============================================================
   7. TABS
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 4px;
    margin-bottom: 1.5rem;
    width: fit-content;
    max-width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    height: auto; background: transparent; border: none;
    border-radius: 7px;
    color: var(--text-muted);
    padding: 0.55rem 1.05rem;
    font-family: 'Sora', sans-serif;
    font-weight: 600; font-size: 0.76rem;
    white-space: nowrap;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); background: rgba(255,255,255,0.03); }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #fff;
    background: linear-gradient(180deg, #ef2a20 0%, #c81a12 100%);
    box-shadow: 0 2px 10px rgba(226,35,26,0.35), inset 0 1px 0 rgba(255,255,255,0.14);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ============================================================
   8. NATIVE METRICS (used on Queue/Analytics/History/Eval)
   ============================================================ */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.03);
    transition: border-color 0.15s ease;
}
[data-testid="stMetric"]:hover { border-color: var(--border-strong); }
[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.05px !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.4px;
    font-variant-numeric: tabular-nums;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem !important;
}

/* ============================================================
   9. SECTION HEADS
   ============================================================ */
.section-head {
    display: flex; align-items: center; gap: 10px;
    margin: 0 0 1rem 0;
}
.section-head .bar {
    width: 3px; height: 16px;
    background: var(--primary);
    border-radius: 2px;
    flex-shrink: 0;
    box-shadow: 0 0 10px var(--primary-glow);
}
.section-head .label {
    font-family: 'Sora', sans-serif;
    font-size: 0.94rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.section-head .count {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem; color: var(--text-muted);
    letter-spacing: 0.5px; text-transform: uppercase;
}

/* ============================================================
   10. KPI TILES (Dashboard) — auto-height, no clipping
   ============================================================ */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
@media (max-width: 960px) { .kpi-row { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 540px) { .kpi-row { grid-template-columns: 1fr; } }

.kpi-tile {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0c0f15 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem 1.05rem;
    display: flex; flex-direction: column;
    gap: 0.15rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.03);
    transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
    min-height: 118px;
}
.kpi-tile:hover {
    border-color: var(--border-strong);
    transform: translateY(-2px);
    box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.05);
}
.kpi-tile::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.10), transparent);
}
.kpi-tile .kpi-head {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 0.5rem;
}
.kpi-tile .kpi-icon {
    width: 26px; height: 26px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 7px;
    flex-shrink: 0;
}
.kpi-tile .kpi-icon svg { width: 14px; height: 14px; }
.kpi-tile .kpi-label {
    font-size: 0.6rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.05px;
    color: var(--text-secondary);
}
.kpi-tile .kpi-value {
    font-family: 'Sora', sans-serif;
    font-size: 1.6rem; font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1.15;
    letter-spacing: -0.4px;
}
.kpi-tile .kpi-sub {
    font-size: 0.72rem; color: var(--text-muted);
    margin-top: 0.15rem;
    line-height: 1.3;
}
.kpi-tile.is-accent .kpi-value { color: var(--accent); }
.kpi-tile.is-primary .kpi-value { color: var(--primary-soft); }
.kpi-tile.is-warning .kpi-value { color: var(--warning); }
.kpi-tile.is-success .kpi-value { color: var(--success); }

/* ============================================================
   11. ACTION CARDS (Queue)
   ============================================================ */
.action-card {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0c0f15 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.05rem 1.2rem 1.05rem 1.35rem;
    margin-bottom: 0.7rem;
    position: relative;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.03);
    transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
}
.action-card::before {
    content: "";
    position: absolute; left: 0; top: 12px; bottom: 12px;
    width: 3px;
    background: linear-gradient(180deg, var(--primary), rgba(226,35,26,0.25));
    border-radius: 0 2px 2px 0;
    box-shadow: 0 0 10px var(--primary-glow);
}
.action-card:hover {
    border-color: var(--border-strong);
    transform: translateY(-1px);
    box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.05);
}
.action-card .ac-top {
    display: flex; align-items: center;
    justify-content: space-between; gap: 0.75rem;
    margin-bottom: 0.75rem; flex-wrap: wrap;
}
.action-card .ac-id { display: flex; align-items: center; gap: 10px; min-width: 0; }
.action-card .avatar {
    width: 38px; height: 38px; border-radius: 10px;
    background: linear-gradient(135deg, rgba(226,35,26,0.22), rgba(226,35,26,0.06));
    border: 1px solid rgba(226,35,26,0.30);
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; font-weight: 700;
    color: var(--primary-soft);
    flex-shrink: 0;
}
.action-card .uid {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.1px;
}
.action-card .meta {
    font-size: 0.62rem; color: var(--text-muted);
    letter-spacing: 0.5px; text-transform: uppercase; margin-top: 2px;
}
.offer-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--accent-dim);
    border: 1px solid rgba(34, 211, 238, 0.32);
    color: var(--accent);
    padding: 0.34rem 0.75rem;
    border-radius: 100px;
    font-size: 0.66rem; font-weight: 700;
    letter-spacing: 0.4px; white-space: nowrap;
    font-family: 'Inter', sans-serif;
}
.action-card .reasoning {
    color: var(--text-secondary);
    font-size: 0.82rem; line-height: 1.6;
    padding: 0.8rem 0.95rem;
    background: rgba(0,0,0,0.28);
    border-radius: var(--radius-xs);
    border-left: 2px solid var(--border-strong);
}
.action-card .reasoning .r-label {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; color: var(--text-muted);
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 0.35rem;
}

/* ============================================================
   12. RISK CHIPS
   ============================================================ */
.risk-chip {
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem; font-weight: 700;
    padding: 0.28rem 0.65rem; border-radius: 100px;
    letter-spacing: 0.3px; white-space: nowrap;
}
.risk-chip::before {
    content: "";
    width: 5px; height: 5px; border-radius: 50%;
    background: currentColor;
}
.risk-chip.high {
    background: var(--primary-dim); color: #ff6b61;
    border: 1px solid rgba(226,35,26,0.35);
}
.risk-chip.med {
    background: var(--warning-dim); color: var(--warning);
    border: 1px solid rgba(242,169,60,0.35);
}
.risk-chip.low {
    background: var(--success-dim); color: var(--success);
    border: 1px solid rgba(45,212,167,0.35);
}

/* ============================================================
   13. EMPTY-STATE PANELS
   ============================================================ */
.panel {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0c0f15 100%);
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius);
    padding: 2.4rem 1.75rem;
    text-align: center;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.panel .panel-icon {
    width: 46px; height: 46px; margin: 0 auto 0.85rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 12px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-strong);
}
.panel .panel-icon svg { width: 22px; height: 22px; color: var(--text-secondary); }
.panel .title {
    font-family: 'Sora', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: var(--text-primary); margin-bottom: 0.4rem;
}
.panel .desc {
    font-size: 0.84rem; color: var(--text-secondary);
    line-height: 1.6; max-width: 460px; margin: 0 auto;
}

/* ============================================================
   14. PLAN RISK BARS (Dashboard right rail)
   ============================================================ */
.plan-row {
    display: flex; align-items: center; gap: 0.75rem;
    margin-bottom: 0.6rem;
}
.plan-row .plan-name {
    width: 78px; flex-shrink: 0;
    font-size: 0.78rem; font-weight: 600; color: var(--text-primary);
}
.plan-row .plan-track {
    flex: 1; height: 8px;
    background: var(--bg-elevated); border-radius: 4px; overflow: hidden;
    border: 1px solid var(--border);
}
.plan-row .plan-fill { height: 100%; border-radius: 4px; }
.plan-row .plan-val {
    width: 44px; flex-shrink: 0; text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: var(--text-secondary);
}

/* ============================================================
   15. MODEL HEALTH CARD
   ============================================================ */
.model-card {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0c0f15 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.05rem 1.15rem;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.03);
    position: relative;
    overflow: hidden;
}
.model-card::before {
    content: "";
    position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: linear-gradient(180deg, var(--accent), rgba(34,211,238,0.2));
    box-shadow: 0 0 10px var(--accent-glow);
}
.model-card .mc-label {
    font-size: 0.6rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.05px;
    color: var(--text-muted); margin-bottom: 0.3rem;
}
.model-card .mc-value {
    font-family: 'Sora', sans-serif;
    font-size: 1.2rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.2px;
}
.model-card .mc-sub {
    font-size: 0.72rem; color: var(--text-secondary);
    margin-top: 0.25rem; line-height: 1.4;
}

/* ============================================================
   16. CHARTS + DATAFRAMES
   ============================================================ */
[data-testid="stDataFrame"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}
[data-testid="stDataFrame"] > div { border-radius: var(--radius); }
.js-plotly-plot { border-radius: var(--radius); overflow: hidden; }
[data-testid="stPlotlyChart"] {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0c0f15 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.5rem;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.03);
}

/* ============================================================
   17. ALERTS / TOASTS / SPINNER
   ============================================================ */
.stAlert {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
}
.stAlert [data-testid="stMarkdownContainer"] p {
    color: var(--text-primary) !important;
    font-size: 0.85rem !important;
    line-height: 1.6 !important;
}
[data-testid="stToast"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--success) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-lg), 0 0 20px rgba(45,212,167,0.12) !important;
}
[data-testid="stToast"] > div { color: var(--text-primary) !important; font-size: 0.85rem !important; }
[data-testid="stSpinner"] > div { border-top-color: var(--primary) !important; }

/* ============================================================
   18. UTILITY
   ============================================================ */
.hr { height: 1px; background: var(--border); margin: 1.25rem 0; border: 0; }
.two-col {
    display: grid; grid-template-columns: 1.45fr 1fr;
    gap: 1.15rem; margin-bottom: 1.15rem;
}
@media (max-width: 960px) { .two-col { grid-template-columns: 1fr; } }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SVG ICON HELPERS (no emojis)
# ============================================================
def _svg(path: str, size: int = 16, color: str = "currentColor") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


ICON = {
    "users": _svg('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "alert": _svg('<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    "spend": _svg('<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
    "send": _svg('<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>'),
    "scan": _svg('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    "check": _svg('<polyline points="20 6 9 17 4 12"/>'),
    "chart": _svg('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>'),
    "history": _svg('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    "model": _svg('<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>'),
    "empty": _svg('<circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/>'),
    "queue": _svg('<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'),
}


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
    """Add timestamped event to agent logs"""
    ts = time.strftime("%H:%M:%S")
    st.session_state.agent_logs.append(f"[{ts}] {msg}")
    if len(st.session_state.agent_logs) > 50:
        st.session_state.agent_logs = st.session_state.agent_logs[-50:]


def risk_tier(score):
    """Buckets a churn_risk_score into (label, css-class)."""
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
    """Load and merge analytics data with caching"""
    if os.path.exists(LOG_PATH) and os.path.exists(USER_DATA_PATH):
        try:
            logs = pd.read_csv(LOG_PATH)
            users = pd.read_csv(USER_DATA_PATH)
            if not logs.empty and not users.empty:
                merged_df = pd.merge(logs, users, on="user_id", how="left")
                return merged_df
        except Exception as e:
            log_event(f"Error loading analytics: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=60)
def get_portfolio():
    """Full customer base for Dashboard KPIs."""
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
    """Pull published evaluation artifacts from Hugging Face."""
    if not settings.use_ml_model:
        return {
            "available": False,
            "reason": "USE_ML_MODEL is off -- scoring with original formula.",
            "metrics": None,
            "raw": None,
        }
    if not settings.hf_model_repo:
        return {
            "available": False,
            "reason": "HF_MODEL_REPO is not configured.",
            "metrics": None,
            "raw": None,
        }
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
        return {
            "available": False,
            "reason": f"could not fetch published evaluation artifacts: {e}",
            "metrics": None,
            "raw": None,
        }


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand-block">
            <div class="brand-mark">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Jazz_logo.svg/1200px-Jazz_logo.svg.png" alt="Jazz" />
            </div>
            <div>
                <div class="brand-name">Retention AI</div>
                <div class="brand-sub">JAZZ · v2.0.1</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Control Panel")

    logs_to_display = st.session_state.agent_logs[-15:]
    logs_html = "".join(
        [f'<div class="terminal-line">{log}</div>' for log in logs_to_display]
    )
    st.markdown(
        f"""
        <div class="terminal-shell">
            <div class="terminal-bar">
                <span class="terminal-dot r"></span>
                <span class="terminal-dot y"></span>
                <span class="terminal-dot g"></span>
                <span class="terminal-title">agent · stream</span>
            </div>
            <div class="terminal-box">{logs_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    threshold = st.slider(
        "Risk Sensitivity",
        min_value=0.40,
        max_value=0.95,
        value=0.70,
        step=0.05,
        help="Customers above this score are flagged by the Monitor agent.",
    )

    if st.button("Run Network Scan", key="run_scan_btn"):
        log_event("Initiating network scan...")
        with st.spinner("Scanning portfolio for at-risk customers..."):
            try:
                results = retention_app.invoke(
                    {
                        "threshold": threshold,
                        "risky_users": [],
                        "final_reports": [],
                    }
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
    <div class="hero">
        <div>
            <div class="hero-title">Retention <span class="accent">AI</span></div>
            <div class="hero-sub">Intelligent customer retention system for Jazz Telecom</div>
        </div>
        <div class="hero-meta">
            <div class="pill primary"><span class="dot"></span>System Active</div>
            <div class="pill accent"><span class="dot"></span>LangGraph Pipeline</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================
tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["Dashboard", "Active Queue", "Analytics", "History", "Evaluation"]
)


# ============================================================
# TAB 0: DASHBOARD
# ============================================================
with tab0:
    st.markdown(
        '<div class="section-head"><span class="bar"></span><span class="label">Business Overview</span></div>',
        unsafe_allow_html=True,
    )

    portfolio = get_portfolio()
    logs_df = get_analytics()

    if portfolio.empty:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-icon">{ICON["empty"]}</div>
                <div class="title">No customer data loaded</div>
                <div class="desc">backend/data/jazz_users.csv was not found or is empty.</div>
            </div>
            """,
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
        reach_pct = (
            round(100.0 * offers_sent_total / at_risk_count, 1) if at_risk_count else 0
        )

        st.markdown(
            f"""
            <div class="kpi-row">
                <div class="kpi-tile is-accent">
                    <div class="kpi-head">
                        <div class="kpi-icon" style="background:var(--accent-dim);color:var(--accent)">{ICON["users"]}</div>
                        <div class="kpi-label">Total Customers</div>
                    </div>
                    <div class="kpi-value">{len(portfolio):,}</div>
                    <div class="kpi-sub">in the active portfolio</div>
                </div>
                <div class="kpi-tile is-primary">
                    <div class="kpi-head">
                        <div class="kpi-icon" style="background:var(--primary-dim);color:var(--primary-soft)">{ICON["alert"]}</div>
                        <div class="kpi-label">At Risk Now</div>
                    </div>
                    <div class="kpi-value">{at_risk_count:,}</div>
                    <div class="kpi-sub">scoring at ≥{threshold:.0%}</div>
                </div>
                <div class="kpi-tile is-warning">
                    <div class="kpi-head">
                        <div class="kpi-icon" style="background:var(--warning-dim);color:var(--warning)">{ICON["spend"]}</div>
                        <div class="kpi-label">Spend at Risk / Mo</div>
                    </div>
                    <div class="kpi-value">{revenue_at_risk:,.0f}</div>
                    <div class="kpi-sub">combined avg. monthly spend</div>
                </div>
                <div class="kpi-tile is-success">
                    <div class="kpi-head">
                        <div class="kpi-icon" style="background:var(--success-dim);color:var(--success)">{ICON["send"]}</div>
                        <div class="kpi-label">Offers Sent</div>
                    </div>
                    <div class="kpi-value">{offers_sent_total}</div>
                    <div class="kpi-sub">{reach_pct}% of at-risk reached</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.45, 1])

        with left:
            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Highest-risk customers</span><span class="count">top 10</span></div>',
                unsafe_allow_html=True,
            )
            top_risk = portfolio.nlargest(10, "churn_risk_score")[
                [
                    c
                    for c in [
                        "user_id",
                        "plan_type",
                        "avg_monthly_spend",
                        "days_since_last_recharge",
                        "churn_risk_score",
                    ]
                    if c in portfolio.columns
                ]
            ].copy()
            top_risk.columns = [
                "Customer",
                "Plan",
                "Spend/mo",
                "Days since recharge",
                "Risk",
            ][: len(top_risk.columns)]
            st.dataframe(top_risk, width="stretch", hide_index=True, height=360)

        with right:
            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Avg. risk by plan</span></div>',
                unsafe_allow_html=True,
            )
            if "plan_type" in portfolio.columns and "churn_risk_score" in portfolio.columns:
                plan_risk = (
                    portfolio.groupby("plan_type")["churn_risk_score"]
                    .mean()
                    .sort_values(ascending=False)
                )
                colors = {
                    "Premium": "#e2231a",
                    "Flexi": "#f2a93c",
                    "Standard": "#2dd4a7",
                }
                rows_html = ""
                for plan, val in plan_risk.items():
                    pct = min(100, max(0, val * 100))
                    color = colors.get(plan, "#22d3ee")
                    rows_html += f"""
                    <div class="plan-row">
                        <div class="plan-name">{plan}</div>
                        <div class="plan-track"><div class="plan-fill" style="width:{pct}%;background:{color}"></div></div>
                        <div class="plan-val">{val:.2f}</div>
                    </div>
                    """
                st.markdown(rows_html, unsafe_allow_html=True)
            else:
                st.caption("Plan breakdown unavailable.")

            st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Model health</span></div>',
                unsafe_allow_html=True,
            )
            _eval = get_model_evaluation()
            if _eval["available"]:
                _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                ver = _eval["metrics"].get("model_version", "v1.0.0")
                st.markdown(
                    f"""
                    <div class="model-card">
                        <div class="mc-label">Scoring with</div>
                        <div class="mc-value">{ver}</div>
                        <div class="mc-sub">Test ROC-AUC {_test_auc:.3f} — see Evaluation tab</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="model-card">
                        <div class="mc-label">Scoring mode</div>
                        <div class="mc-value">Formula</div>
                        <div class="mc-sub">{_eval["reason"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# TAB 1: ACTIVE QUEUE
# ============================================================
with tab1:
    if st.session_state.results is not None:
        final_reports = st.session_state.results.get("final_reports", [])
        active_reports = [
            r for r in final_reports if r.get("status") != "deployed"
        ] if final_reports else []

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Flagged", len(st.session_state.results.get("risky_users", [])))
        with col2:
            st.metric("In Queue", len(active_reports))
        with col3:
            _eval = get_model_evaluation()
            if _eval["available"]:
                _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                st.metric(
                    "Model ROC-AUC (test)",
                    f"{_test_auc:.3f}",
                    help=f"From {settings.hf_model_repo}@{settings.hf_model_revision}",
                )
            else:
                st.metric("Scoring Mode", "Formula")
        with col4:
            st.metric("AI Status", "Active")

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="section-head">
                <span class="bar"></span>
                <span class="label">Deployment Queue</span>
                <span class="count">{len(active_reports)} awaiting review</span>
            </div>
            """,
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
                initials = str(user_id)[:2].upper() if user_id != "N/A" else "??"
                risk_score = risky_by_id.get(str(user_id))
                risk_label, risk_css = risk_tier(risk_score)
                risk_chip_html = (
                    f'<span class="risk-chip {risk_css}">{risk_label} · {risk_score:.2f}</span>'
                    if risk_score is not None
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="action-card">
                        <div class="ac-top">
                            <div class="ac-id">
                                <div class="avatar">{initials}</div>
                                <div>
                                    <div class="uid">{user_id}</div>
                                    <div class="meta">Customer · Retention Target</div>
                                </div>
                            </div>
                            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                                {risk_chip_html}
                                <span class="offer-badge">{offer}</span>
                            </div>
                        </div>
                        <div class="reasoning">
                            <span class="r-label">Agent Reasoning</span>
                            {reasoning}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_btn, _ = st.columns([2, 3])
                with col_btn:
                    st.markdown('<div class="deploy-btn">', unsafe_allow_html=True)
                    if st.button("Deploy Retention Strategy", key=f"deploy_{user_id}"):
                        try:
                            success = execute_retention_action(report)
                            if success:
                                log_event(f"Successfully deployed strategy for {user_id}")
                                st.toast(f"Strategy deployed for {user_id}")
                                time.sleep(0.5)
                                get_analytics.clear()
                                st.rerun()
                            else:
                                log_event(f"Failed to deploy strategy for {user_id}")
                                st.toast(f"Deployment failed for {user_id}")
                        except Exception as e:
                            log_event(f"Error deploying for {user_id}: {str(e)}")
                            st.error(f"Deployment error: {str(e)}")
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="panel-icon">{ICON["check"]}</div>
                    <div class="title">Queue Clear</div>
                    <div class="desc">All flagged customers have been processed. Run a new scan to refresh the risk pool.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            _, mid, _ = st.columns([1, 1, 1])
            with mid:
                if st.button("Scan for New Targets", key="rescan_button"):
                    log_event("Initiating new network scan...")
                    with st.spinner("Scanning for new targets..."):
                        try:
                            results = retention_app.invoke(
                                {
                                    "threshold": threshold,
                                    "risky_users": [],
                                    "final_reports": [],
                                }
                            )
                            st.session_state.results = results
                            log_event(
                                f"Rescan complete: {len(results.get('risky_users', []))} customers found"
                            )
                            get_analytics.clear()
                        except Exception as e:
                            log_event(f"Rescan error: {str(e)}")
                            st.error(f"Rescan failed: {str(e)}")
                    st.rerun()
    else:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-icon">{ICON["scan"]}</div>
                <div class="title">No Scan On Record</div>
                <div class="desc">Use the Control Panel in the sidebar to initiate your first network scan. The system will surface at-risk customers and generate retention strategies.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 2: ANALYTICS
# ============================================================
with tab2:
    st.markdown(
        '<div class="section-head"><span class="bar"></span><span class="label">Performance Analytics</span></div>',
        unsafe_allow_html=True,
    )

    analytics_df = get_analytics()

    if not analytics_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Actions", len(analytics_df))
        with col2:
            if "churn_risk_score" in analytics_df.columns:
                st.metric("Avg Risk Score", f"{analytics_df['churn_risk_score'].mean():.2f}")
            else:
                st.metric("Avg Risk Score", "N/A")
        with col3:
            st.metric("Unique Customers", analytics_df["user_id"].nunique())
        with col4:
            if "offer_sent" in analytics_df.columns and not analytics_df["offer_sent"].empty:
                mode_offers = analytics_df["offer_sent"].mode()
                most_common = mode_offers[0] if len(mode_offers) > 0 else "N/A"
                st.metric("Most Common Offer", most_common)
            else:
                st.metric("Most Common Offer", "N/A")

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            if "offer_sent" in analytics_df.columns:
                st.markdown(
                    '<div class="section-head"><span class="bar"></span><span class="label">Offer Distribution</span></div>',
                    unsafe_allow_html=True,
                )
                fig = px.pie(
                    analytics_df,
                    names="offer_sent",
                    hole=0.65,
                    color_discrete_sequence=["#e2231a", "#ff5c50", "#22d3ee", "#f2a93c", "#2dd4a7"],
                )
                fig.update_traces(
                    textposition="outside",
                    textinfo="percent+label",
                    textfont=dict(size=11, color="#8c93a4"),
                    marker=dict(line=dict(color="#06070b", width=2)),
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#eef0f4", size=12),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=340,
                )
                st.plotly_chart(fig, width="stretch", key="offer_pie")

        with col2:
            if "churn_risk_score" in analytics_df.columns:
                st.markdown(
                    '<div class="section-head"><span class="bar"></span><span class="label">Risk Score Distribution</span></div>',
                    unsafe_allow_html=True,
                )
                fig2 = px.histogram(
                    analytics_df,
                    x="churn_risk_score",
                    nbins=20,
                    color_discrete_sequence=["#e2231a"],
                )
                fig2.update_traces(
                    marker=dict(line=dict(color="#06070b", width=1)),
                    opacity=0.9,
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#eef0f4", size=12),
                    xaxis=dict(
                        showgrid=False, title="Risk Score", zeroline=False, color="#8c93a4"
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        title="Count",
                        zeroline=False,
                        color="#8c93a4",
                    ),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=340,
                    bargap=0.05,
                )
                st.plotly_chart(fig2, width="stretch", key="risk_hist")

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

        if "timestamp" in analytics_df.columns:
            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Activity Timeline</span></div>',
                unsafe_allow_html=True,
            )
            try:
                analytics_df["date"] = pd.to_datetime(analytics_df["timestamp"]).dt.date
                timeline_data = (
                    analytics_df.groupby("date").size().reset_index(name="actions")
                )
                fig3 = px.line(
                    timeline_data,
                    x="date",
                    y="actions",
                    color_discrete_sequence=["#e2231a"],
                )
                fig3.update_traces(
                    line=dict(width=2.5),
                    mode="lines+markers",
                    marker=dict(size=7, line=dict(color="#06070b", width=2)),
                    fill="tozeroy",
                    fillcolor="rgba(226,35,26,0.07)",
                )
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#eef0f4", size=12),
                    xaxis=dict(showgrid=False, title="", color="#8c93a4", zeroline=False),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        title="Actions",
                        color="#8c93a4",
                        zeroline=False,
                    ),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                )
                st.plotly_chart(fig3, width="stretch", key="timeline")
            except Exception as e:
                log_event(f"Error creating timeline: {str(e)}")
                st.warning("Unable to display timeline chart")
    else:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-icon">{ICON["chart"]}</div>
                <div class="title">No Analytics Yet</div>
                <div class="desc">Run a network scan and deploy retention strategies to generate insight into offer performance and risk distribution.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 3: HISTORY
# ============================================================
with tab3:
    st.markdown(
        '<div class="section-head"><span class="bar"></span><span class="label">Action History</span></div>',
        unsafe_allow_html=True,
    )

    df = get_analytics()

    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            if "timestamp" in df.columns:
                try:
                    latest = pd.to_datetime(df["timestamp"]).max()
                    st.metric("Latest Action", latest.strftime("%Y-%m-%d %H:%M"))
                except Exception:
                    st.metric("Latest Action", "N/A")
            else:
                st.metric("Latest Action", "N/A")
        with col3:
            st.metric("Data Points", len(df.columns))

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

        display_df = df.copy()
        if "timestamp" in display_df.columns:
            try:
                display_df = display_df.sort_values("timestamp", ascending=False)
            except Exception:
                pass

        st.dataframe(display_df, width="stretch", hide_index=True, height=500)
    else:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-icon">{ICON["history"]}</div>
                <div class="title">No History Yet</div>
                <div class="desc">Execute retention actions to build your audit trail. Every deployment is logged here for compliance and review.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 4: EVALUATION
# ============================================================
with tab4:
    st.markdown(
        '<div class="section-head"><span class="bar"></span><span class="label">Model Evaluation</span></div>',
        unsafe_allow_html=True,
    )

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

        badge_col, auc_col, formula_col = st.columns(3)
        with badge_col:
            st.metric(
                "Model Version",
                metrics.get("model_version", "unknown"),
                help=f"Published at huggingface.co/{settings.hf_model_repo}",
            )
        with auc_col:
            st.metric("Test ROC-AUC (model)", f"{test_row['model']['roc_auc']:.4f}")
        with formula_col:
            delta = test_row["model"]["roc_auc"] - test_row["old_formula_roc_auc"]
            st.metric(
                "Test ROC-AUC (old formula)",
                f"{test_row['old_formula_roc_auc']:.4f}",
                delta=f"{delta:+.4f} vs. model",
                delta_color="inverse",
            )

        st.caption(
            "Both scores are computed on the exact same held-out test rows — "
            "the old formula is the literal one from `backend/data_generator.py`, "
            "scored here only for comparison."
        )

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-head"><span class="bar"></span><span class="label">Metrics by split</span></div>',
            unsafe_allow_html=True,
        )
        rows = []
        for split in metrics["splits"]:
            m = split["model"]
            rows.append(
                {
                    "split": split["split"],
                    "n": split["n"],
                    "accuracy": m["accuracy"],
                    "precision": m["precision"],
                    "recall": m["recall"],
                    "f1": m["f1"],
                    "roc_auc (model)": m["roc_auc"],
                    "roc_auc (old formula)": split["old_formula_roc_auc"],
                }
            )
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Model vs. old formula (ROC-AUC)</span></div>',
                unsafe_allow_html=True,
            )
            bar_df = pd.DataFrame(rows)
            fig_bar = go.Figure(
                data=[
                    go.Bar(
                        name="Model",
                        x=bar_df["split"],
                        y=bar_df["roc_auc (model)"],
                        marker_color="#e2231a",
                    ),
                    go.Bar(
                        name="Old formula",
                        x=bar_df["split"],
                        y=bar_df["roc_auc (old formula)"],
                        marker_color="#4a5568",
                    ),
                ]
            )
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#eef0f4", size=12),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.05)",
                    title="ROC-AUC",
                    range=[0, 1],
                    color="#8c93a4",
                    zeroline=False,
                ),
                xaxis=dict(title="", color="#8c93a4"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(0,0,0,0)",
                ),
                margin=dict(l=20, r=20, t=40, b=20),
                height=340,
            )
            st.plotly_chart(fig_bar, width="stretch", key="eval_auc_bar")

        with chart_col2:
            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Top features (mean |SHAP|)</span></div>',
                unsafe_allow_html=True,
            )
            top_features = metrics.get("top_features_test", [])
            if top_features:
                shap_df = pd.DataFrame(top_features).sort_values("mean_abs_shap")
                fig_shap = go.Figure(
                    go.Bar(
                        x=shap_df["mean_abs_shap"],
                        y=shap_df["feature"],
                        orientation="h",
                        marker=dict(
                            color=shap_df["mean_abs_shap"],
                            colorscale=[[0, "#0e3a4a"], [1, "#22d3ee"]],
                            line=dict(color="rgba(0,0,0,0)"),
                        ),
                    )
                )
                fig_shap.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#eef0f4", size=12),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        title="mean |SHAP value|",
                        color="#8c93a4",
                        zeroline=False,
                    ),
                    yaxis=dict(title="", color="#8c93a4"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=340,
                )
                st.plotly_chart(fig_shap, width="stretch", key="eval_shap_bar")
            else:
                st.info("No SHAP summary published with this model version.")

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

        if raw is not None:
            y_true = np.array(raw["y_true"])
            y_proba = np.array(raw["model_proba"])

            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">ROC & Precision-Recall (test set)</span></div>',
                unsafe_allow_html=True,
            )
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
                fig_roc.add_trace(
                    go.Scatter(
                        x=fprs,
                        y=tprs,
                        mode="lines",
                        name="Model",
                        line=dict(color="#e2231a", width=3),
                        fill="tozeroy",
                        fillcolor="rgba(226,35,26,0.08)",
                    )
                )
                fig_roc.add_trace(
                    go.Scatter(
                        x=[0, 1],
                        y=[0, 1],
                        mode="lines",
                        name="Random",
                        line=dict(color="#4a5568", dash="dash", width=1.5),
                    )
                )
                fig_roc.update_layout(
                    title=dict(text="ROC curve", font=dict(size=13, color="#8c93a4")),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#eef0f4", size=12),
                    xaxis=dict(
                        title="False Positive Rate",
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        color="#8c93a4",
                        zeroline=False,
                    ),
                    yaxis=dict(
                        title="True Positive Rate",
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        color="#8c93a4",
                        zeroline=False,
                    ),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=340,
                )
                st.plotly_chart(fig_roc, width="stretch", key="eval_roc")

            with curve_col2:
                fig_pr = go.Figure()
                fig_pr.add_trace(
                    go.Scatter(
                        x=recalls,
                        y=precisions,
                        mode="lines",
                        name="Model",
                        line=dict(color="#22d3ee", width=3),
                        fill="tozeroy",
                        fillcolor="rgba(34,211,238,0.08)",
                    )
                )
                fig_pr.update_layout(
                    title=dict(
                        text="Precision-Recall curve", font=dict(size=13, color="#8c93a4")
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#eef0f4", size=12),
                    xaxis=dict(
                        title="Recall",
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        color="#8c93a4",
                        zeroline=False,
                    ),
                    yaxis=dict(
                        title="Precision",
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.05)",
                        color="#8c93a4",
                        zeroline=False,
                    ),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=340,
                )
                st.plotly_chart(fig_pr, width="stretch", key="eval_pr")

            st.markdown(
                '<div class="section-head"><span class="bar"></span><span class="label">Confusion matrix (threshold = 0.5)</span></div>',
                unsafe_allow_html=True,
            )
            pred_50 = (y_proba >= 0.5).astype(int)
            tp = int(((pred_50 == 1) & (y_true == 1)).sum())
            fp = int(((pred_50 == 1) & (y_true == 0)).sum())
            fn = int(((pred_50 == 0) & (y_true == 1)).sum())
            tn = int(((pred_50 == 0) & (y_true == 0)).sum())
            cm = [[tn, fp], [fn, tp]]
            fig_cm = go.Figure(
                data=go.Heatmap(
                    z=cm,
                    x=["Pred: Stay", "Pred: Churn"],
                    y=["Actual: Stay", "Actual: Churn"],
                    text=cm,
                    texttemplate="<b>%{text}</b>",
                    textfont=dict(size=18, color="#ffffff"),
                    colorscale=[[0, "#0a0c11"], [1, "#e2231a"]],
                    showscale=False,
                    hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
                )
            )
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#eef0f4", size=12),
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                xaxis=dict(color="#8c93a4", side="bottom"),
                yaxis=dict(color="#8c93a4", autorange="reversed"),
            )
            st.plotly_chart(fig_cm, width="stretch", key="eval_cm")
        else:
            st.info(
                "Per-row test predictions (`test_raw.json`) weren't published with "
                "this model version, so ROC/PR curves and confusion matrix "
                "can't be drawn — only the aggregate metrics above. "
                "Re-run `notebooks/02_train_model.py` and re-publish to unlock this section."
            )
