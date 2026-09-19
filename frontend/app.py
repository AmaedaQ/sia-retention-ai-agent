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
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><rect width='40' height='40' rx='11' fill='%23FF3B3B'/><text x='20' y='28' text-anchor='middle' fill='white' font-family='system-ui' font-weight='800' font-size='22'>J</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM — "Console v7"
# A complete reimagining: editorial typography, row-based
# lists, numbered sections, gradient hairline borders.
# Backend calls / session state / data functions untouched.
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

:root {
    --primary:       #FF3B3B;
    --primary-soft:  #FF6A6A;
    --primary-dim:   rgba(255, 59, 59, 0.12);
    --primary-glow:  rgba(255, 59, 59, 0.35);
    --accent:        #00E5FF;
    --accent-dim:    rgba(0, 229, 255, 0.12);
    --accent-glow:   rgba(0, 229, 255, 0.35);
    --success:       #00E0A4;
    --success-dim:   rgba(0, 224, 164, 0.12);
    --success-glow:  rgba(0, 224, 164, 0.35);
    --warning:       #FFB020;
    --warning-dim:   rgba(255, 176, 32, 0.12);
    --warning-glow:  rgba(255, 176, 32, 0.35);
    --violet:        #A78BFA;
    --violet-dim:    rgba(167, 139, 250, 0.12);

    --bg-void:       #040507;
    --bg-base:       #08090D;
    --bg-card:       #0C0E13;
    --bg-elevated:   #12151C;
    --bg-hover:      #191D26;

    --border:        rgba(255,255,255,0.06);
    --border-strong: rgba(255,255,255,0.12);

    --text-primary:   #F2F3F5;
    --text-secondary: #8E95A8;
    --text-muted:     #565D6E;

    --r-lg: 16px;
    --r-md: 12px;
    --r-sm: 8px;
}

/* ============ CANVAS ============ */
[data-testid="stAppViewContainer"] {
    background: var(--bg-void);
    background-image:
        radial-gradient(900px 500px at 8% -5%, rgba(255,59,59,0.09), transparent 60%),
        radial-gradient(700px 500px at 95% 0%, rgba(0,229,255,0.06), transparent 55%);
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.014) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.014) 1px, transparent 1px);
    background-size: 44px 44px;
    pointer-events: none;
    z-index: 0;
    mask-image: radial-gradient(ellipse 90% 70% at 50% 0%, black 20%, transparent 78%);
    -webkit-mask-image: radial-gradient(ellipse 90% 70% at 50% 0%, black 20%, transparent 78%);
}
.block-container {
    padding-top: 1.6rem !important;
    padding-bottom: 5rem !important;
    max-width: 1420px;
    position: relative;
    z-index: 1;
}
[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stToolbar"] { right: 1rem; top: 0.5rem; opacity: 0.45; transition: opacity 0.2s; }
[data-testid="stToolbar"]:hover { opacity: 1; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stStatusWidget"] { display: none !important; }

/* ============ TYPOGRAPHY (scoped — never override icon fonts) ============ */
html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
}
.stApp, .stApp .stMarkdown, .stApp p,
.stApp label,
.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stWidgetLabel"],
.stApp button, .stApp input, .stApp textarea, .stApp select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    font-family: 'Space Grotesk', 'Inter', sans-serif;
    letter-spacing: -0.02em;
}
/* Restore Material Symbols for Streamlit's native icons */
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
    background: linear-gradient(180deg, #08090D 0%, #050608 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.1rem;
    padding-bottom: 1.5rem;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] { z-index: 100 !important; }
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
    color: var(--text-primary) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    color: currentColor !important;
    fill: currentColor !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-muted) !important;
    font-size: 0.58rem !important;
    font-weight: 700 !important;
    letter-spacing: 2.2px !important;
    text-transform: uppercase !important;
    margin: 0 0 0.85rem 0 !important;
    padding-bottom: 0.55rem;
    border-bottom: 1px solid var(--border);
}

/* Brand block */
.brand-row {
    display: flex; align-items: center; gap: 12px;
    padding: 0 0 1.15rem 0;
    margin-bottom: 1.15rem;
    border-bottom: 1px solid var(--border);
}
.brand-mark {
    width: 44px; height: 44px;
    flex-shrink: 0;
    position: relative;
    filter: drop-shadow(0 6px 18px rgba(255,59,59,0.35));
}
.brand-mark svg { width: 100%; height: 100%; display: block; }
.brand-txt { line-height: 1.15; min-width: 0; }
.brand-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.98rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.015em;
}
.brand-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; color: var(--text-muted);
    letter-spacing: 0.7px; margin-top: 3px;
}

/* Terminal */
.term {
    background: #040507;
    border: 1px solid var(--border-strong);
    border-radius: var(--r-md);
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 6px 20px rgba(0,0,0,0.4);
}
.term-bar {
    display: flex; align-items: center; gap: 5px;
    padding: 9px 12px;
    background: #0A0C10;
    border-bottom: 1px solid var(--border);
}
.term-dot { width: 8px; height: 8px; border-radius: 50%; }
.term-dot.r { background: #FF5F57; }
.term-dot.y { background: #FEBC2E; }
.term-dot.g { background: #28C840; }
.term-name {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.56rem; color: var(--text-muted);
    letter-spacing: 0.7px; text-transform: uppercase;
}
.term-body {
    padding: 12px 13px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    height: 220px; overflow-y: auto; line-height: 1.7;
    scrollbar-width: thin;
    scrollbar-color: var(--primary) transparent;
}
.term-body::-webkit-scrollbar { width: 4px; }
.term-body::-webkit-scrollbar-track { background: transparent; }
.term-body::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 2px; }
.term-line {
    display: grid;
    grid-template-columns: 54px 8px 1fr;
    gap: 8px;
    margin-bottom: 3px;
    white-space: pre-wrap; word-break: break-word;
}
.term-line .ts {
    color: var(--text-muted);
    font-size: 0.62rem;
}
.term-line .bul {
    color: var(--primary-soft);
    font-size: 0.7rem;
    line-height: inherit;
}
.term-line .msg { color: var(--success); }
.term-line.warn .bul, .term-line.warn .msg { color: var(--warning); }
.term-line.err  .bul, .term-line.err  .msg { color: var(--primary-soft); }
.term-cursor {
    display: inline-block;
    width: 7px; height: 12px;
    background: var(--success);
    vertical-align: -2px;
    margin-left: 4px;
    animation: blink 1.05s steps(2) infinite;
}
@keyframes blink { 50% { opacity: 0; } }

/* Slider */
.stSlider { padding: 0.2rem 0 0.65rem 0; }
[data-testid="stSlider"] label {
    color: var(--text-secondary) !important;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div { background: var(--primary) !important; }
[data-testid="stSlider"] [role="slider"] {
    background: #fff !important;
    border: 2px solid var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(255,59,59,0.18) !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none; }
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: var(--primary) !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    border-radius: 5px !important;
    padding: 1px 6px !important;
}

/* ============ BUTTONS ============ */
.stButton > button {
    width: 100%;
    background: linear-gradient(180deg, #FF3B3B 0%, #C81B1B 100%);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: var(--r-sm);
    padding: 0.7rem 1rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.3px;
    transition: all 0.18s ease;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), 0 6px 18px rgba(255,59,59,0.28);
}
.stButton > button:hover {
    background: linear-gradient(180deg, #FF5252 0%, #D41D1D 100%);
    transform: translateY(-1px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.22), 0 10px 26px rgba(255,59,59,0.42);
}
.stButton > button:active { transform: translateY(0); }
.stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 3px rgba(255,59,59,0.30), 0 6px 18px rgba(255,59,59,0.28);
}

/* ============ HERO ============ */
.hero {
    position: relative;
    padding: 0 0 1.5rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.55rem;
}
.hero-eyebrow::before {
    content: "";
    width: 18px; height: 1px;
    background: var(--primary);
    box-shadow: 0 0 8px var(--primary-glow);
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem; font-weight: 700;
    letter-spacing: -1.2px; line-height: 1;
    color: var(--text-primary);
    margin: 0 0 0.55rem 0;
}
.hero-title .accent {
    background: linear-gradient(135deg, #FF3B3B 0%, #FF7A5C 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: var(--text-secondary);
    font-size: 0.9rem;
    max-width: 620px;
    line-height: 1.5;
}
.hero-pills {
    display: flex; gap: 0.5rem; flex-wrap: wrap;
    margin-top: 1rem;
}
.pill {
    display: inline-flex; align-items: center; gap: 7px;
    background: var(--bg-card);
    border: 1px solid var(--border-strong);
    padding: 0.45rem 0.85rem;
    border-radius: 100px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 600;
    letter-spacing: 0.7px; text-transform: uppercase;
    color: var(--text-secondary);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}
.pill .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 10px var(--success-glow);
    animation: pulse 2.4s ease-in-out infinite;
}
.pill.accent { border-color: rgba(0,229,255,0.28); }
.pill.accent .dot { background: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }
.pill.primary { border-color: rgba(255,59,59,0.32); }
.pill.primary .dot { background: var(--primary); box-shadow: 0 0 10px var(--primary-glow); }
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.45; transform: scale(0.82); }
}

/* ============ TABS ============ */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 4px;
    margin-bottom: 1.75rem;
    width: fit-content;
    max-width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: none;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    height: auto; background: transparent; border: none;
    border-radius: 8px;
    color: var(--text-muted);
    padding: 0.55rem 1.05rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600; font-size: 0.78rem;
    white-space: nowrap;
    letter-spacing: -0.005em;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); background: rgba(255,255,255,0.03); }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #fff;
    background: linear-gradient(180deg, #FF3B3B 0%, #C81B1B 100%);
    box-shadow: 0 2px 12px rgba(255,59,59,0.40), inset 0 1px 0 rgba(255,255,255,0.16);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ============ SECTION HEADER (numbered) ============ */
.sec-h {
    display: flex; align-items: center; gap: 14px;
    margin: 0 0 1.15rem 0;
}
.sec-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; font-weight: 700;
    color: var(--primary);
    letter-spacing: 1.5px;
    padding: 4px 8px;
    border: 1px solid rgba(255,59,59,0.35);
    border-radius: 6px;
    background: var(--primary-dim);
    box-shadow: inset 0 0 12px rgba(255,59,59,0.10);
    flex-shrink: 0;
}
.sec-rule {
    width: 22px; height: 1px;
    background: var(--border-strong);
    flex-shrink: 0;
}
.sec-meta { flex: 1; min-width: 0; }
.sec-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.015em;
}
.sec-sub {
    font-size: 0.74rem;
    color: var(--text-muted);
    margin-top: 2px;
}
.sec-count {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: var(--text-muted);
    letter-spacing: 0.6px; text-transform: uppercase;
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 100px;
    background: var(--bg-card);
    flex-shrink: 0;
}

/* ============ KPI TILES ============ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin-bottom: 2rem;
}
@media (max-width: 1000px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px)  { .kpi-grid { grid-template-columns: 1fr; } }

.kpi {
    position: relative;
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border-radius: var(--r-lg);
    padding: 1.1rem 1.2rem 0.9rem;
    display: flex; flex-direction: column;
    min-height: 168px;
    overflow: hidden;
    isolation: isolate;
    transition: transform 0.2s ease;
}
.kpi::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.015));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    z-index: 2;
}
.kpi::after {
    content: "";
    position: absolute;
    top: -50%; right: -25%;
    width: 180px; height: 180px;
    border-radius: 50%;
    opacity: 0.16;
    filter: blur(45px);
    pointer-events: none;
    z-index: 0;
    transition: opacity 0.3s ease;
}
.kpi.accent::after  { background: var(--accent); }
.kpi.primary::after { background: var(--primary); }
.kpi.warning::after { background: var(--warning); }
.kpi.success::after { background: var(--success); }
.kpi:hover { transform: translateY(-3px); }
.kpi:hover::after { opacity: 0.28; }

.kpi-top {
    display: flex; align-items: center; gap: 9px;
    margin-bottom: 0.85rem;
    position: relative;
    z-index: 1;
}
.kpi-icon {
    width: 30px; height: 30px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px;
    flex-shrink: 0;
}
.kpi-icon svg { width: 15px; height: 15px; }
.kpi.accent  .kpi-icon { background: var(--accent-dim);  color: var(--accent);       box-shadow: inset 0 0 0 1px rgba(0,229,255,0.22); }
.kpi.primary .kpi-icon { background: var(--primary-dim); color: var(--primary-soft); box-shadow: inset 0 0 0 1px rgba(255,59,59,0.22); }
.kpi.warning .kpi-icon { background: var(--warning-dim); color: var(--warning);      box-shadow: inset 0 0 0 1px rgba(255,176,32,0.22); }
.kpi.success .kpi-icon { background: var(--success-dim); color: var(--success);      box-shadow: inset 0 0 0 1px rgba(0,224,164,0.22); }
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--text-muted);
}
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem; font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1;
    letter-spacing: -1px;
    margin-bottom: 0.35rem;
    position: relative;
    z-index: 1;
}
.kpi.accent  .kpi-value { color: var(--accent); }
.kpi.primary .kpi-value { color: var(--primary-soft); }
.kpi.warning .kpi-value { color: var(--warning); }
.kpi.success .kpi-value { color: var(--success); }
.kpi-sub {
    font-size: 0.72rem; color: var(--text-muted);
    line-height: 1.35;
    position: relative;
    z-index: 1;
}
.kpi-spark-svg {
    display: block;
    margin-top: auto;
    padding-top: 0.75rem;
    position: relative;
    z-index: 1;
}

/* ============ ACTION ROW (queue) ============ */
.q-row {
    position: relative;
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border-radius: var(--r-md);
    padding: 1rem 1.1rem 1rem 1.25rem;
    display: grid;
    grid-template-columns: 44px 1fr;
    gap: 14px;
    align-items: start;
    margin-bottom: 0.6rem;
    transition: transform 0.15s ease;
    overflow: hidden;
}
.q-row::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.015));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}
.q-row::after {
    content: "";
    position: absolute; left: 0; top: 20%; bottom: 20%; width: 3px;
    background: linear-gradient(180deg, var(--primary), rgba(255,59,59,0.15));
    border-radius: 0 2px 2px 0;
    box-shadow: 0 0 14px var(--primary-glow);
}
.q-row:hover { transform: translateX(2px); }
.q-avatar {
    width: 44px; height: 44px; border-radius: 10px;
    background: linear-gradient(135deg, rgba(255,59,59,0.20), rgba(255,59,59,0.04));
    border: 1px solid rgba(255,59,59,0.30);
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem; font-weight: 700;
    color: var(--primary-soft);
    flex-shrink: 0;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
    position: relative;
    z-index: 1;
}
.q-body { min-width: 0; position: relative; z-index: 1; }
.q-title {
    display: flex; align-items: center; gap: 9px;
    flex-wrap: wrap;
    margin-bottom: 0.35rem;
}
.q-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.92rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.005em;
}
.chip {
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; font-weight: 700;
    padding: 0.24rem 0.6rem; border-radius: 100px;
    letter-spacing: 0.5px; white-space: nowrap;
    text-transform: uppercase;
}
.chip::before {
    content: "";
    width: 5px; height: 5px; border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 6px currentColor;
}
.chip.high { background: var(--primary-dim); color: #FF7A7A; border: 1px solid rgba(255,59,59,0.35); }
.chip.med  { background: var(--warning-dim); color: var(--warning); border: 1px solid rgba(255,176,32,0.35); }
.chip.low  { background: var(--success-dim); color: var(--success); border: 1px solid rgba(0,224,164,0.35); }
.offer-chip {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--accent-dim);
    border: 1px solid rgba(0,229,255,0.30);
    color: var(--accent);
    padding: 0.26rem 0.68rem;
    border-radius: 100px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.4px; white-space: nowrap;
    text-transform: uppercase;
}
.q-meta {
    font-size: 0.76rem;
    color: var(--text-secondary);
    margin-bottom: 0.55rem;
    line-height: 1.4;
}
.q-reason {
    font-size: 0.8rem; line-height: 1.55;
    color: var(--text-secondary);
    padding: 0.6rem 0.75rem;
    background: rgba(0,0,0,0.28);
    border-radius: var(--r-sm);
    border-left: 2px solid var(--border-strong);
}
.q-reason .lbl {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 0.28rem;
}

/* ============ PLAN BARS ============ */
.plan-row {
    display: flex; align-items: center; gap: 0.75rem;
    margin-bottom: 0.65rem;
}
.plan-name {
    width: 82px; flex-shrink: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem; font-weight: 600;
    color: var(--text-primary);
}
.plan-track {
    flex: 1; height: 6px;
    background: var(--bg-elevated);
    border-radius: 4px; overflow: hidden;
    border: 1px solid var(--border);
    position: relative;
}
.plan-fill {
    height: 100%;
    border-radius: 4px;
    box-shadow: 0 0 10px currentColor;
}
.plan-val {
    width: 46px; flex-shrink: 0; text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-secondary);
    font-variant-numeric: tabular-nums;
}

/* ============ MODEL CARD ============ */
.model-card {
    position: relative;
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border-radius: var(--r-md);
    padding: 1rem 1.15rem 1rem 1.3rem;
    overflow: hidden;
}
.model-card::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(180deg, rgba(0,229,255,0.28), rgba(0,229,255,0.03));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}
.model-card::after {
    content: "";
    position: absolute; left: 0; top: 22%; bottom: 22%; width: 3px;
    background: linear-gradient(180deg, var(--accent), rgba(0,229,255,0.15));
    border-radius: 0 2px 2px 0;
    box-shadow: 0 0 14px var(--accent-glow);
}
.mc-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}
.mc-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem; font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.4px;
}
.mc-sub {
    font-size: 0.76rem;
    color: var(--text-secondary);
    margin-top: 0.35rem;
    line-height: 1.45;
}

/* ============ EMPTY PANEL ============ */
.panel {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border: 1px dashed var(--border-strong);
    border-radius: var(--r-lg);
    padding: 3rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.panel::before {
    content: "";
    position: absolute; top: -50%; left: 50%; transform: translateX(-50%);
    width: 400px; height: 200px;
    background: radial-gradient(circle, rgba(255,59,59,0.08), transparent 70%);
    pointer-events: none;
}
.panel-icon {
    width: 56px; height: 56px; margin: 0 auto 1rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(255,59,59,0.14), rgba(0,229,255,0.08));
    border: 1px solid var(--border-strong);
    box-shadow: 0 8px 28px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
    position: relative;
    z-index: 1;
}
.panel-icon svg { width: 26px; height: 26px; color: var(--primary-soft); }
.panel-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem; font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    letter-spacing: -0.015em;
    position: relative;
    z-index: 1;
}
.panel-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 480px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

/* ============ CUSTOM TABLE ============ */
.table-wrap {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border-radius: var(--r-md);
    overflow: hidden;
    position: relative;
}
.table-wrap::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.015));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    z-index: 3;
}
.table-scroll {
    overflow: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--primary) transparent;
}
.table-scroll::-webkit-scrollbar { width: 8px; height: 8px; }
.table-scroll::-webkit-scrollbar-track { background: transparent; }
.table-scroll::-webkit-scrollbar-thumb {
    background: rgba(255,59,59,0.5);
    border-radius: 4px;
    border: 2px solid var(--bg-card);
}
table.dt {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.82rem;
    min-width: 580px;
}
table.dt thead th {
    position: sticky; top: 0;
    background: var(--bg-elevated);
    padding: 11px 16px;
    text-align: left;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.4px;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border-strong);
    white-space: nowrap;
    z-index: 2;
}
table.dt tbody td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
    white-space: nowrap;
}
table.dt tbody tr:last-child td { border-bottom: none; }
table.dt tbody tr:hover td { background: rgba(255,255,255,0.02); }
table.dt td.mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-primary);
}
table.dt td.muted { color: var(--text-secondary); }
table.dt td.num {
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
}

/* ============ NATIVE METRICS (fallback tabs) ============ */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1rem 1.15rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stMetric"]:hover { border-color: var(--border-strong); transform: translateY(-1px); }
[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.6px;
    font-variant-numeric: tabular-nums;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem !important;
}

/* ============ CHART CONTAINERS ============ */
.js-plotly-plot { border-radius: var(--r-md); overflow: hidden; }
[data-testid="stPlotlyChart"] {
    background: linear-gradient(180deg, var(--bg-card) 0%, #0A0C11 100%);
    border-radius: var(--r-md);
    padding: 0.5rem;
    position: relative;
}
[data-testid="stPlotlyChart"]::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.015));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    z-index: 3;
}

/* ============ ALERTS / TOASTS ============ */
.stAlert {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--r-md) !important;
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
    border-radius: var(--r-md) !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 24px rgba(0,224,164,0.14) !important;
}
[data-testid="stToast"] > div { color: var(--text-primary) !important; font-size: 0.85rem !important; }
[data-testid="stSpinner"] > div { border-top-color: var(--primary) !important; }

/* ============ DATAFRAME FALLBACK ============ */
[data-testid="stDataFrame"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    overflow: hidden;
}

/* ============ SPACER ============ */
.sp-1 { height: 0.5rem; }
.sp-2 { height: 1rem; }
.sp-3 { height: 1.5rem; }
.sp-4 { height: 2rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SVG ICONS
# ============================================================
def _svg(path: str, size: int = 16) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


ICON = {
    "users":   _svg('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "alert":   _svg('<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    "spend":   _svg('<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
    "send":    _svg('<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>'),
    "scan":    _svg('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    "check":   _svg('<polyline points="20 6 9 17 4 12"/>'),
    "chart":   _svg('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>'),
    "history": _svg('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    "model":   _svg('<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>'),
    "empty":   _svg('<circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/>'),
    "queue":   _svg('<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'),
    "pulse":   _svg('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'),
    "trending": _svg('<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'),
    "shield":  _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'),
}

# Inline brand mark — stylized "J." monogram, no external deps
BRAND_MARK = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44">
  <defs>
    <linearGradient id="jz-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FF5252"/>
      <stop offset="100%" stop-color="#B8001A"/>
    </linearGradient>
    <linearGradient id="jz-shine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgba(255,255,255,0.35)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="44" height="44" rx="12" fill="url(#jz-grad)"/>
  <rect x="0" y="0" width="44" height="22" rx="12" fill="url(#jz-shine)"/>
  <text x="20" y="30" text-anchor="middle" fill="#ffffff"
        font-family="'Space Grotesk', system-ui, sans-serif"
        font-weight="700" font-size="22">J</text>
  <circle cx="32" cy="30" r="2.4" fill="#ffffff"/>
</svg>
"""


# ============================================================
# HELPERS — sparkline, section header, table, chips
# ============================================================
_spark_seq = [0]


def _spark_uid() -> str:
    _spark_seq[0] += 1
    return f"spk{_spark_seq[0]}"


def sparkline(values, color="#00E5FF", width=200, height=30):
    """Inline SVG area sparkline. Returns '' if not enough data."""
    if values is None or len(values) < 2:
        return ""
    try:
        vals = []
        for v in values:
            if v is None:
                continue
            fv = float(v)
            if np.isnan(fv):
                continue
            vals.append(fv)
    except Exception:
        return ""
    if len(vals) < 2:
        return ""
    mn, mx = min(vals), max(vals)
    rng = (mx - mn) or 1.0
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = (i / (n - 1)) * width
        y = height - ((v - mn) / rng) * (height - 6) - 3
        pts.append(f"{x:.1f},{y:.1f}")
    path = "M " + " L ".join(pts)
    area = path + f" L {width},{height} L 0,{height} Z"
    uid = _spark_uid()
    return (
        f'<svg class="kpi-spark-svg" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="none" width="100%" height="{height}">'
        f'<defs><linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{color}" stop-opacity="0.4"/>'
        f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
        f'</linearGradient></defs>'
        f'<path d="{area}" fill="url(#{uid})"/>'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.5" '
        f'vector-effect="non-scaling-stroke"/></svg>'
    )


def section_header(num, label, sub=None, count=None):
    sub_html = f'<div class="sec-sub">{sub}</div>' if sub else ""
    count_html = f'<span class="sec-count">{count}</span>' if count else ""
    return (
        f'<div class="sec-h">'
        f'<span class="sec-num">{num}</span>'
        f'<span class="sec-rule"></span>'
        f'<div class="sec-meta"><div class="sec-label">{label}</div>{sub_html}</div>'
        f'{count_html}'
        f'</div>'
    )


def risk_chip(score):
    label, css = risk_tier(score)
    try:
        s = f"{float(score):.2f}"
    except (TypeError, ValueError):
        s = "—"
    return f'<span class="chip {css}">{label} · {s}</span>'


def render_table(headers, rows, max_height=420):
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


def empty_panel(icon_key, title, desc):
    return (
        f'<div class="panel">'
        f'<div class="panel-icon">{ICON[icon_key]}</div>'
        f'<div class="panel-title">{title}</div>'
        f'<div class="panel-desc">{desc}</div>'
        f'</div>'
    )


def kpi_tile(variant, icon_key, label, value, sub, spark_html=""):
    return (
        f'<div class="kpi {variant}">'
        f'<div class="kpi-top">'
        f'<div class="kpi-icon">{ICON[icon_key]}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'{spark_html}'
        f'</div>'
    )


def term_line_html(raw_line):
    """Render a log line as a 3-column grid row with level colouring."""
    s = str(raw_line)
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
    elif any(k in low for k in ("warn", "skipped")):
        cls = "warn"
    return f'<div class="term-line {cls}"><span class="ts">{ts}</span><span class="bul">▸</span><span class="msg">{msg}</span></div>'


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
# SIDEBAR — command rail
# ============================================================
with st.sidebar:
    st.markdown(
        f"""
        <div class="brand-row">
            <div class="brand-mark">{BRAND_MARK}</div>
            <div class="brand-txt">
                <div class="brand-name">Retention AI</div>
                <div class="brand-meta">JAZZ · v2.0.1</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Agent Stream")

    lines = "".join([term_line_html(x) for x in st.session_state.agent_logs[-14:]])
    st.markdown(
        f"""
        <div class="term">
            <div class="term-bar">
                <span class="term-dot r"></span>
                <span class="term-dot y"></span>
                <span class="term-dot g"></span>
                <span class="term-name">stream · live</span>
            </div>
            <div class="term-body">{lines}<span class="term-cursor"></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Risk Sensitivity")

    threshold = st.slider(
        "Flag threshold",
        min_value=0.40, max_value=0.95, value=0.70, step=0.05,
        help="Customers scoring at or above this value are flagged by the Monitor agent.",
        label_visibility="collapsed",
    )

    st.markdown("<div class='sp-1'></div>", unsafe_allow_html=True)

    if st.button("Run Network Scan", key="run_scan_btn"):
        log_event("Initiating network scan...")
        with st.spinner("Scanning portfolio for at-risk customers..."):
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
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">Jazz Telecom · Retention Engine</div>
        <div class="hero-title">Retention <span class="accent">AI</span></div>
        <div class="hero-sub">
            Live customer-churn intelligence. Monitor the portfolio, review
            agent reasoning, and deploy targeted retention offers in a single pass.
        </div>
        <div class="hero-pills">
            <div class="pill primary"><span class="dot"></span>System Active</div>
            <div class="pill accent"><span class="dot"></span>LangGraph Pipeline</div>
            <div class="pill"><span class="dot"></span>Model Online</div>
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
    portfolio = get_portfolio()
    logs_df = get_analytics()

    if portfolio.empty:
        st.markdown(
            empty_panel(
                "empty",
                "No customer data loaded",
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

        risk_series = (
            sorted(portfolio["churn_risk_score"].dropna().tolist())
            if "churn_risk_score" in portfolio.columns
            else []
        )
        spend_series = (
            portfolio["avg_monthly_spend"].dropna().tolist()[:120]
            if "avg_monthly_spend" in portfolio.columns
            else []
        )

        st.markdown(
            '<div class="kpi-grid">'
            + kpi_tile(
                "accent", "users", "Total Customers",
                f"{len(portfolio):,}",
                "in the active portfolio",
                sparkline(risk_series, color="#00E5FF"),
            )
            + kpi_tile(
                "primary", "alert", "At Risk Now",
                f"{at_risk_count:,}",
                f"scoring at ≥{threshold:.0%}",
                sparkline(sorted(risk_series, reverse=True)[:80], color="#FF3B3B"),
            )
            + kpi_tile(
                "warning", "spend", "Spend at Risk / Mo",
                f"{revenue_at_risk:,.0f}",
                "combined avg. monthly spend",
                sparkline(spend_series, color="#FFB020"),
            )
            + kpi_tile(
                "success", "send", "Offers Sent",
                f"{offers_sent_total}",
                f"{reach_pct}% of at-risk reached",
                sparkline([max(1, offers_sent_total + d) for d in (1, 2, 1, 3, 2, 4, 3)], color="#00E0A4"),
            )
            + '</div>',
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.55, 1])

        with left:
            st.markdown(
                section_header("01", "Highest-risk customers", "Top 10 by churn probability", count="TOP 10"),
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
                    (risk_chip(score), ""),
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
                section_header("02", "Avg. risk by plan", "Mean churn score, plan-wise"),
                unsafe_allow_html=True,
            )
            if "active_plan" in portfolio.columns and "churn_risk_score" in portfolio.columns:
                plan_risk = (
                    portfolio.groupby("active_plan")["churn_risk_score"]
                    .mean()
                    .sort_values(ascending=False)
                )
                colors = {"Premium": "#FF3B3B", "Flexi": "#FFB020", "Standard": "#00E0A4"}
                rows_html = ""
                for plan, val in plan_risk.items():
                    pct = min(100, max(0, val * 100))
                    color = colors.get(plan, "#00E5FF")
                    rows_html += (
                        f'<div class="plan-row">'
                        f'<div class="plan-name">{plan}</div>'
                        f'<div class="plan-track">'
                        f'<div class="plan-fill" style="width:{pct}%;background:{color};color:{color}"></div>'
                        f'</div>'
                        f'<div class="plan-val">{val:.2f}</div>'
                        f'</div>'
                    )
                st.markdown(rows_html, unsafe_allow_html=True)
            else:
                st.caption("Plan breakdown unavailable.")

            st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
            st.markdown(
                section_header("03", "Model health", "Active scoring pipeline"),
                unsafe_allow_html=True,
            )
            _eval = get_model_evaluation()
            if _eval["available"]:
                _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                ver = _eval["metrics"].get("model_version", "v1.0.0")
                st.markdown(
                    f'<div class="model-card">'
                    f'<div class="mc-label">Scoring with</div>'
                    f'<div class="mc-value">{ver}</div>'
                    f'<div class="mc-sub">Test ROC-AUC <b>{_test_auc:.3f}</b> · see Evaluation tab for full report</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="model-card">'
                    f'<div class="mc-label">Scoring mode</div>'
                    f'<div class="mc-value">Formula</div>'
                    f'<div class="mc-sub">{_eval["reason"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# TAB 1: ACTIVE QUEUE
# ============================================================
with tab1:
    if st.session_state.results is not None:
        final_reports = st.session_state.results.get("final_reports", [])
        active_reports = [r for r in final_reports if r.get("status") != "deployed"] if final_reports else []

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Flagged", len(st.session_state.results.get("risky_users", [])))
        with col2:
            st.metric("In Queue", len(active_reports))
        with col3:
            _eval = get_model_evaluation()
            if _eval["available"]:
                _test_auc = _eval["metrics"]["splits"][-1]["model"]["roc_auc"]
                st.metric("Test ROC-AUC", f"{_test_auc:.3f}")
            else:
                st.metric("Scoring Mode", "Formula")
        with col4:
            st.metric("AI Status", "Active")

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)

        st.markdown(
            section_header(
                "01", "Deployment Queue",
                "Flagged customers awaiting retention action",
                count=f"{len(active_reports)} PENDING",
            ),
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
                risk_chip_html = risk_chip(risk_score) if risk_score is not None else ""

                c_row, c_btn = st.columns([5.2, 1])

                with c_row:
                    st.markdown(
                        f'<div class="q-row">'
                        f'<div class="q-avatar">{initials}</div>'
                        f'<div class="q-body">'
                        f'<div class="q-title">'
                        f'<span class="q-id">{user_id}</span>'
                        f'{risk_chip_html}'
                        f'<span class="offer-chip">{offer}</span>'
                        f'</div>'
                        f'<div class="q-meta">Retention target · priority scan</div>'
                        f'<div class="q-reason"><span class="lbl">Agent reasoning</span>{reasoning}</div>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                with c_btn:
                    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
                    if st.button("Deploy →", key=f"deploy_{user_id}"):
                        try:
                            success = execute_retention_action(report)
                            if success:
                                log_event(f"Deployed strategy for {user_id}")
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

                st.markdown("<div class='sp-1'></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                empty_panel(
                    "check",
                    "Queue is clear",
                    "Every flagged customer has been processed. Run a new scan to refresh the risk pool.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown("<div class='sp-2'></div>", unsafe_allow_html=True)
            _, mid, _ = st.columns([1, 1, 1])
            with mid:
                if st.button("Scan for New Targets", key="rescan_button"):
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
            empty_panel(
                "scan",
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

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
        st.markdown(
            section_header("01", "Offer mix", "Distribution of deployed retention offers"),
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if "offer_sent" in analytics_df.columns:
                fig = px.pie(
                    analytics_df, names="offer_sent", hole=0.68,
                    color_discrete_sequence=["#FF3B3B", "#FF6A6A", "#00E5FF", "#FFB020", "#00E0A4"],
                )
                fig.update_traces(
                    textposition="outside",
                    textinfo="percent+label",
                    textfont=dict(size=11, color="#8E95A8"),
                    marker=dict(line=dict(color="#040507", width=2)),
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#F2F3F5", size=12),
                    showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=340,
                )
                st.plotly_chart(fig, width="stretch", key="offer_pie")

        with col2:
            if "churn_risk_score" in analytics_df.columns:
                fig2 = px.histogram(
                    analytics_df, x="churn_risk_score", nbins=20,
                    color_discrete_sequence=["#FF3B3B"],
                )
                fig2.update_traces(marker=dict(line=dict(color="#040507", width=1)), opacity=0.9)
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#F2F3F5", size=12),
                    xaxis=dict(showgrid=False, title="Risk Score", zeroline=False, color="#8E95A8"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Count", zeroline=False, color="#8E95A8"),
                    margin=dict(l=20, r=20, t=20, b=20), height=340, bargap=0.05,
                )
                st.plotly_chart(fig2, width="stretch", key="risk_hist")

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
        st.markdown(
            section_header("02", "Activity timeline", "Deployment volume over time"),
            unsafe_allow_html=True,
        )

        if "timestamp" in analytics_df.columns:
            try:
                analytics_df["date"] = pd.to_datetime(analytics_df["timestamp"]).dt.date
                timeline_data = analytics_df.groupby("date").size().reset_index(name="actions")
                fig3 = px.line(timeline_data, x="date", y="actions", color_discrete_sequence=["#FF3B3B"])
                fig3.update_traces(
                    line=dict(width=2.5), mode="lines+markers",
                    marker=dict(size=7, line=dict(color="#040507", width=2)),
                    fill="tozeroy", fillcolor="rgba(255,59,59,0.08)",
                )
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#F2F3F5", size=12),
                    xaxis=dict(showgrid=False, title="", color="#8E95A8", zeroline=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Actions", color="#8E95A8", zeroline=False),
                    hovermode="x unified", margin=dict(l=20, r=20, t=20, b=20), height=300,
                )
                st.plotly_chart(fig3, width="stretch", key="timeline")
            except Exception as e:
                log_event(f"Error creating timeline: {str(e)}")
                st.warning("Unable to display timeline chart")
    else:
        st.markdown(
            empty_panel(
                "chart",
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

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
        st.markdown(
            section_header("01", "Audit trail", "Every deployed action, newest first", count=f"{len(df)} RECORDS"),
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
                cls = ""
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
            empty_panel(
                "history",
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
            st.metric("Model Version", metrics.get("model_version", "unknown"))
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

        st.caption(
            "Both scores are computed on the exact same held-out test rows — "
            "the old formula is the literal one from `backend/data_generator.py`, "
            "scored here only for comparison."
        )

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
        st.markdown(
            section_header("01", "Metrics by split", "Aggregate accuracy & ranking"),
            unsafe_allow_html=True,
        )

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
                html_rows, max_height=320,
            ),
            unsafe_allow_html=True,
        )

        st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
        st.markdown(
            section_header("02", "Model vs. formula", "ROC-AUC per split"),
            unsafe_allow_html=True,
        )

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            bar_df = pd.DataFrame(rows_data)
            fig_bar = go.Figure(data=[
                go.Bar(name="Model", x=bar_df["split"], y=bar_df["roc_auc (model)"], marker_color="#FF3B3B"),
                go.Bar(name="Old formula", x=bar_df["split"], y=bar_df["roc_auc (old formula)"], marker_color="#4A5568"),
            ])
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#F2F3F5", size=12),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="ROC-AUC", range=[0, 1], color="#8E95A8", zeroline=False),
                xaxis=dict(title="", color="#8E95A8"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=20, r=20, t=40, b=20), height=340,
            )
            st.plotly_chart(fig_bar, width="stretch", key="eval_auc_bar")

        with chart_col2:
            top_features = metrics.get("top_features_test", [])
            if top_features:
                shap_df = pd.DataFrame(top_features).sort_values("mean_abs_shap")
                fig_shap = go.Figure(go.Bar(
                    x=shap_df["mean_abs_shap"], y=shap_df["feature"], orientation="h",
                    marker=dict(
                        color=shap_df["mean_abs_shap"],
                        colorscale=[[0, "#0B2530"], [1, "#00E5FF"]],
                        line=dict(color="rgba(0,0,0,0)"),
                    ),
                ))
                fig_shap.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#F2F3F5", size=12),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="mean |SHAP|", color="#8E95A8", zeroline=False),
                    yaxis=dict(title="", color="#8E95A8"),
                    margin=dict(l=20, r=20, t=20, b=20), height=340,
                )
                st.plotly_chart(fig_shap, width="stretch", key="eval_shap_bar")
            else:
                st.info("No SHAP summary published with this model version.")

        if raw is not None:
            st.markdown("<div class='sp-3'></div>", unsafe_allow_html=True)
            st.markdown(
                section_header("03", "Diagnostics", "Test-set ROC, PR, and confusion"),
                unsafe_allow_html=True,
            )

            y_true = np.array(raw["y_true"])
            y_proba = np.array(raw["model_proba"])

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
                    line=dict(color="#FF3B3B", width=3),
                    fill="tozeroy", fillcolor="rgba(255,59,59,0.08)",
                ))
                fig_roc.add_trace(go.Scatter(
                    x=[0, 1], y=[0, 1], mode="lines", name="Random",
                    line=dict(color="#4A5568", dash="dash", width=1.5),
                ))
                fig_roc.update_layout(
                    title=dict(text="ROC curve", font=dict(size=13, color="#8E95A8")),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#F2F3F5", size=12),
                    xaxis=dict(title="False Positive Rate", showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#8E95A8", zeroline=False),
                    yaxis=dict(title="True Positive Rate", showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#8E95A8", zeroline=False),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=20, r=20, t=40, b=20), height=340,
                )
                st.plotly_chart(fig_roc, width="stretch", key="eval_roc")

            with curve_col2:
                fig_pr = go.Figure()
                fig_pr.add_trace(go.Scatter(
                    x=recalls, y=precisions, mode="lines", name="Model",
                    line=dict(color="#00E5FF", width=3),
                    fill="tozeroy", fillcolor="rgba(0,229,255,0.08)",
                ))
                fig_pr.update_layout(
                    title=dict(text="Precision-Recall curve", font=dict(size=13, color="#8E95A8")),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#F2F3F5", size=12),
                    xaxis=dict(title="Recall", showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#8E95A8", zeroline=False),
                    yaxis=dict(title="Precision", showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#8E95A8", zeroline=False),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=20, r=20, t=40, b=20), height=340,
                )
                st.plotly_chart(fig_pr, width="stretch", key="eval_pr")

            st.markdown("<div class='sp-2'></div>", unsafe_allow_html=True)
            pred_50 = (y_proba >= 0.5).astype(int)
            tp = int(((pred_50 == 1) & (y_true == 1)).sum())
            fp = int(((pred_50 == 1) & (y_true == 0)).sum())
            fn = int(((pred_50 == 0) & (y_true == 1)).sum())
            tn = int(((pred_50 == 0) & (y_true == 0)).sum())
            cm = [[tn, fp], [fn, tp]]
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm, x=["Pred: Stay", "Pred: Churn"], y=["Actual: Stay", "Actual: Churn"],
                text=cm, texttemplate="<b>%{text}</b>",
                textfont=dict(size=18, color="#ffffff"),
                colorscale=[[0, "#0A0C11"], [1, "#FF3B3B"]],
                showscale=False,
                hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
            ))
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#F2F3F5", size=12),
                margin=dict(l=20, r=20, t=20, b=20), height=320,
                xaxis=dict(color="#8E95A8", side="bottom"),
                yaxis=dict(color="#8E95A8", autorange="reversed"),
            )
            st.plotly_chart(fig_cm, width="stretch", key="eval_cm")
        else:
            st.info(
                "Per-row test predictions (`test_raw.json`) weren't published with "
                "this model version, so ROC/PR curves and confusion matrix "
                "can't be drawn — only the aggregate metrics above. "
                "Re-run `notebooks/02_train_model.py` and re-publish to unlock this section."
            )
