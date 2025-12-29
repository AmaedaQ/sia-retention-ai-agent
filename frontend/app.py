import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.graph import retention_app
from backend.agents.action import execute_retention_action

st.set_page_config(
    page_title="SIA | Jazz Business Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📡"
)

# Clean, professional CSS – no childish feel
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main {
        background: #f9fafb;
        padding: 2rem 1rem;
    }

    h1 {
        color: #d60000;
        font-weight: 700;
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .subtitle {
        text-align: center;
        color: #4b5563;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }

    .stButton > button {
        background-color: #d60000;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.7rem 1.4rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #b30000;
    }

    .stMetric {
        background: white;
        border-radius: 12px;
        padding: 1.4rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    .stMetric label {
        color: #d60000;
        font-weight: 600;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMetric .stMetricValue {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-top: 0.4rem;
    }

    .stExpander {
        background: white;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .stExpander summary {
        color: #d60000;
        font-weight: 600;
        padding: 1rem;
    }

    .sidebar .sidebar-content {
        background: white;
        box-shadow: 2px 0 15px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #e5e7eb;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.05rem;
        font-weight: 600;
        color: #4b5563;
        padding: 0.8rem 1.5rem;
    }
    .stTabs [aria-selected="true"] {
        color: #d60000 !important;
        border-bottom: 3px solid #d60000 !important;
    }

    h2, h3 {
        color: #1f2937;
        font-weight: 600;
    }

    .explanation {
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>SIA – Jazz Autonomous Growth Engine</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-driven churn prevention and revenue retention platform</p>', unsafe_allow_html=True)

# Data paths
LOG_PATH = os.path.join(os.path.dirname(__file__), '../backend/data/action_logs.csv')
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), '../backend/data/jazz_users.csv')

def get_analytics():
    if os.path.exists(LOG_PATH) and os.path.exists(USER_DATA_PATH):
        logs = pd.read_csv(LOG_PATH)
        users = pd.read_csv(USER_DATA_PATH)
        if not logs.empty and not users.empty:
            return pd.merge(logs, users, on='user_id', how='left')
    return pd.DataFrame()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Jazz_logo.svg/1200px-Jazz_logo.svg.png", width=140)
    st.markdown("### Control Panel")
    threshold = st.slider(
        "Churn Risk Threshold",
        0.0, 1.0, 0.70, 0.05,
        help="Lower value = detect more potential churners"
    )
    if st.button("Run Network Analysis", use_container_width=True):
        with st.spinner("Processing customer base..."):
            st.session_state.results = retention_app.invoke({"threshold": threshold, "risky_users": [], "final_reports": []})
    st.markdown("---")
    st.caption("SIA v2026 • Confidential Business Tool")

# Tabs
tab1, tab2, tab3 = st.tabs(["Real-time Interventions", "Business Impact", "Action History"])

# Tab 1: Real-time Actions
with tab1:
    if 'results' in st.session_state:
        results = st.session_state.results
        df_risky = pd.DataFrame(results['risky_users'])

        if not df_risky.empty:
            cols = st.columns(3)
            cols[0].metric("At-Risk Customers", len(df_risky))
            cols[1].metric("Potential Revenue Loss", f"Rs. {int(df_risky['avg_monthly_spend'].sum()):,}")
            cols[2].metric("Generated Offers", len(results['final_reports']))

            st.markdown("### Recommended Retention Actions")
            st.markdown('<p class="explanation">Review AI-suggested personalized offers below and deploy directly</p>', unsafe_allow_html=True)

            for report in results['final_reports']:
                with st.expander(f"Customer {report['user_id']} – Offer: {report['offer']}"):
                    st.markdown("**AI Recommendation Rationale**")
                    st.write(report['reasoning'])
                    if st.button(f"Deploy Offer to Customer {report['user_id']}", key=report['user_id'], use_container_width=True):
                        if execute_retention_action(report):
                            st.success(f"Offer successfully deployed to customer {report['user_id']}")
                            st.rerun()
        else:
            st.info("No customers above the chosen risk threshold were detected.")
    else:
        st.info("Run a network analysis from the sidebar to identify at-risk customers.")

# Tab 2: Business Impact – clearer version
with tab2:
    st.markdown("### Business Impact Overview")
    st.markdown('<p class="explanation">Shows revenue protected and customers retained through deployed retention offers</p>', unsafe_allow_html=True)

    analytics_df = get_analytics()

    if not analytics_df.empty:
        cols = st.columns(2)
        with cols[0]:
            total_saved = analytics_df['avg_monthly_spend'].sum()
            st.metric(
                "Revenue Protected (Monthly Recurring)",
                f"Rs. {int(total_saved):,}",
                help="Sum of avg_monthly_spend of all retained customers"
            )
            st.markdown("**Offer Performance Breakdown**")
            fig = px.pie(
                analytics_df,
                names='offer_sent',
                title="Retention Success by Offer Type",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

        with cols[1]:
            st.metric(
                "Customers Retained",
                len(analytics_df),
                help="Number of customers who received an offer and are still active"
            )
            st.markdown("**Risk Profile of Retained Customers**")
            fig2 = px.histogram(
                analytics_df,
                x='churn_risk_score',
                title="Churn Risk Scores of Saved Customers",
                color_discrete_sequence=['#d60000'],
                nbins=15
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No retention actions have been deployed yet. Business impact will appear here once offers are executed.")

# Tab 3: History
with tab3:
    st.markdown("### Action History Log")
    st.markdown('<p class="explanation">Record of all deployed retention actions with timestamps and outcomes</p>', unsafe_allow_html=True)

    analytics_df = get_analytics()
    if not analytics_df.empty:
        display_cols = ['timestamp', 'user_id', 'offer_sent', 'status', 'avg_monthly_spend']
        st.dataframe(
            analytics_df[display_cols]
                .sort_values('timestamp', ascending=False)
                .rename(columns={
                    'timestamp': 'Date & Time',
                    'user_id': 'Customer ID',
                    'offer_sent': 'Offer Deployed',
                    'status': 'Outcome',
                    'avg_monthly_spend': 'Monthly Spend (Rs.)'
                }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No actions recorded yet.")