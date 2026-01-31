import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import time

# Path setup for Cloud environment
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from backend.graph import retention_app
from backend.agents.action import execute_retention_action

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Retention AI | Jazz Telecom",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN CSS WITH 2026 DESIGN TRENDS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* === BASE THEME === */
    :root {
        --primary: #e30613;
        --primary-glow: rgba(227, 6, 19, 0.2);
        --accent: #00d4ff;
        --bg-dark: #0a0e14;
        --bg-card: #131820;
        --bg-elevated: #1a1f2e;
        --border: #2a3142;
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --success: #10b981;
        --warning: #f59e0b;
    }
    
    /* === GLOBAL RESET === */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #0d1117 100%);
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }
    
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    /* Hide default header */
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* === SIDEBAR MODERN REDESIGN === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-elevated) 100%);
        border-right: 1px solid var(--border);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--text-primary) !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary);
    }
    
    /* === TERMINAL CONSOLE === */
    .terminal-box {
        background: #000000;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--success);
        height: 280px;
        overflow-y: auto;
        line-height: 1.6;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);
    }
    
    .terminal-box::-webkit-scrollbar {
        width: 6px;
    }
    
    .terminal-box::-webkit-scrollbar-track {
        background: #000000;
    }
    
    .terminal-box::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 3px;
    }
    
    /* === SLIDER STYLING === */
    .stSlider {
        padding: 1rem 0;
    }
    
    [data-testid="stSlider"] label {
        color: var(--text-secondary) !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* === BUTTON REDESIGN === */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--primary) 0%, #b30510 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px var(--primary-glow);
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--primary-glow);
        background: linear-gradient(135deg, #ff0718 0%, var(--primary) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* === TOAST MESSAGE STYLING === */
    [data-testid="stToast"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--success) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    [data-testid="stToast"] > div {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* === TABS MODERN DESIGN === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-radius: 8px 8px 0 0;
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-elevated);
        color: var(--text-primary);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--bg-elevated);
        color: var(--primary);
        border-bottom: 3px solid var(--primary);
    }
    
    /* === METRICS CARDS === */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* === USER ACTION CARDS === */
    .action-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 4px solid var(--primary);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .action-card:hover {
        border-left-width: 6px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        transform: translateX(4px);
    }
    
    .action-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .user-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .offer-badge {
        background: linear-gradient(135deg, var(--primary) 0%, #b30510 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px var(--primary-glow);
    }
    
    .reasoning-text {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        margin-top: 0.5rem;
    }
    
    /* === HEADER SECTION === */
    .main-header {
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid var(--border);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 400;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--bg-elevated);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid var(--border);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* === DATAFRAME STYLING === */
    [data-testid="stDataFrame"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* === INFO/SUCCESS BOXES === */
    .stAlert {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* === PLOTLY CHARTS === */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* === SECTION HEADERS === */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border);
        letter-spacing: 0.5px;
    }
    
    /* === JAZZ LOGO STYLING === */
    [data-testid="stSidebar"] img {
        border-radius: 8px;
        padding: 0.5rem;
        background: white;
        margin-bottom: 1.5rem;
    }
    
    /* === SPINNER STYLING === */
    [data-testid="stSpinner"] > div {
        border-top-color: var(--primary) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA UTILITIES ---
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
    # Keep only last 50 logs to prevent memory issues
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

# --- SIDEBAR: CONTROL PANEL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Jazz_logo.svg/1200px-Jazz_logo.svg.png", width=80)
    
    st.markdown("### Control Panel")
    
    # Terminal Console
    logs_to_display = st.session_state.agent_logs[-15:]
    logs_html = "".join([f"<div style='margin-bottom:6px;'>{log}</div>" for log in logs_to_display])
    st.markdown(f'<div class="terminal-box">{logs_html}</div>', unsafe_allow_html=True)
    
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
    if st.button("🔍 Run Network Scan", key="scan_button"):
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

# --- MAIN HEADER ---
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
        <div class="main-header">
            <div class="main-title">Retention AI</div>
            <div class="main-subtitle">Intelligent Customer Retention System for Jazz Telecom</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: right;">
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span>SYSTEM ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Active Queue", "📈 Analytics", "📜 History"])

# --- TAB 1: ACTIVE QUEUE ---
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
                st.metric("Success Rate", "94.2%")
            with col4:
                st.metric("AI Status", "Active")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Deployment Queue</div>', unsafe_allow_html=True)
            
            # Action Cards
            for report in active_reports:
                user_id = report.get('user_id', 'N/A')
                offer = report.get('offer', 'N/A')
                reasoning = report.get('reasoning', 'No reasoning provided')
                
                st.markdown(f"""
                    <div class="action-card">
                        <div class="action-card-header">
                            <span class="user-id">Customer ID: {user_id}</span>
                            <span class="offer-badge">{offer}</span>
                        </div>
                        <div class="reasoning-text">{reasoning}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_btn, col_space = st.columns([2, 3])
                with col_btn:
                    if st.button("Deploy Retention Strategy", key=f"deploy_{user_id}"):
                        try:
                            success = execute_retention_action(report)
                            if success:
                                log_event(f"Successfully deployed strategy for {user_id}")
                                st.toast(f"✅ Strategy deployed for {user_id}", icon="✅")
                                time.sleep(0.5)
                                # Clear cache to refresh data
                                get_analytics.clear()
                                st.rerun()
                            else:
                                log_event(f"Failed to deploy strategy for {user_id}")
                                st.toast(f"❌ Deployment failed for {user_id}", icon="❌")
                        except Exception as e:
                            log_event(f"Error deploying for {user_id}: {str(e)}")
                            st.error(f"Deployment error: {str(e)}")
                
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.success("✅ All actions processed. Queue is empty.")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Scan for New Targets", key="rescan_button"):
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
        st.info("👆 Use the Control Panel in the sidebar to initiate your first network scan.")

# --- TAB 2: ANALYTICS ---
with tab2:
    st.markdown('<div class="section-header">Performance Analytics</div>', unsafe_allow_html=True)
    
    analytics_df = get_analytics()
    
    if not analytics_df.empty:
        # Top Metrics
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
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            if 'offer_sent' in analytics_df.columns:
                st.markdown("#### Offer Distribution")
                fig = px.pie(
                    analytics_df, 
                    names='offer_sent', 
                    hole=0.6,
                    color_discrete_sequence=['#e30613', '#ff4757', '#ff6b81', '#ffa502']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, width="stretch", key="offer_pie")
        
        with col2:
            if 'churn_risk_score' in analytics_df.columns:
                st.markdown("#### Risk Score Distribution")
                fig2 = px.histogram(
                    analytics_df, 
                    x='churn_risk_score', 
                    nbins=20,
                    color_discrete_sequence=['#e30613']
                )
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    xaxis=dict(showgrid=True, gridcolor='#2a3142', title="Risk Score"),
                    yaxis=dict(showgrid=True, gridcolor='#2a3142', title="Count"),
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig2, width="stretch", key="risk_hist")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Timeline Chart
        if 'timestamp' in analytics_df.columns:
            st.markdown("#### Activity Timeline")
            try:
                analytics_df['date'] = pd.to_datetime(analytics_df['timestamp']).dt.date
                timeline_data = analytics_df.groupby('date').size().reset_index(name='actions')
                
                fig3 = px.line(
                    timeline_data, 
                    x='date', 
                    y='actions', 
                    color_discrete_sequence=['#e30613']
                )
                fig3.update_traces(line=dict(width=3), mode='lines+markers')
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    xaxis=dict(showgrid=True, gridcolor='#2a3142', title="Date"),
                    yaxis=dict(showgrid=True, gridcolor='#2a3142', title="Actions"),
                    hovermode='x unified',
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig3, width="stretch", key="timeline")
            except Exception as e:
                log_event(f"Error creating timeline: {str(e)}")
                st.warning("Unable to display timeline chart")
    else:
        st.info("No analytics data available yet. Run a network scan to generate insights.")

# --- TAB 3: HISTORY ---
with tab3:
    st.markdown('<div class="section-header">Action History</div>', unsafe_allow_html=True)
    
    df = get_analytics()
    
    if not df.empty:
        # Summary metrics
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
        
        # Data table
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
<<<<<<< HEAD
        st.info("No historical data available yet. Execute retention actions to build your audit trail.")
=======
        st.info("No historical data available yet. Execute retention actions to build your audit trail.")
>>>>>>> 8e878a10fe2c403d1d0499ae03b911d4bd64ddb8
