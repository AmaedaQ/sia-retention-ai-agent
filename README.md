# SIA: Strategic Intelligence Agent
## Enterprise-Grade Autonomous Retention Engine for Telecommunications

SIA (Strategic Intelligence Agent) is an autonomous multi-agent system designed to combat customer churn in the telecommunications industry.  
It leverages **stateful agent orchestration** and **low-latency LLM reasoning** to convert subscriber data into **actionable, personalized retention strategies**.

---

## System Architecture

SIA operates on a **Stateful Directed Acyclic Graph (DAG)**, ensuring controlled data flow, agent isolation, and session-aware reasoning.

### Core Agents

**Monitor Agent**
- Continuously scans subscriber data using neural churn-risk thresholds
- Uses smart memory to exclude users already processed

**Strategy Decider (Llama-3.3-70B via Groq)**
- Performs low-latency reasoning on high-risk subscribers
- Generates personalized interventions:
  - Magic Bundles
  - Network Discounts
  - Recharge Incentives

**Execution Auditor**
- Validates strategy logic before execution
- Writes all actions to an immutable audit ledger
- Updates BI dashboards for real-time tracking

---

## Tech Stack

| Layer              | Technology                                   |
|--------------------|----------------------------------------------|
| Agentic Framework  | LangGraph (Stateful Orchestration)            |
| Reasoning Engine   | Llama-3.3-70B-Versatile (Groq Cloud)          |
| Frontend / UI      | Streamlit (Custom Glassmorphic UI)            |
| Data Analytics     | Pandas, NumPy, Plotly Express                |
| State Management   | Python TypedDict, Streamlit Session State     |

---

## Strategic Modules

### 1. Real-Time Monitoring & Deployment
- Batch execution in 5-user segments to preserve LLM reasoning quality
- Real-time log cross-checking removes processed users immediately

### 2. Predictive Analytics
- Revenue Protection Matrix showing defended Monthly Recurring Revenue (MRR)
- Live churn-risk distribution across the subscriber base

### 3. Audit Ledger
- Full transparency with timestamped autonomous decisions
- Designed for compliance and human oversight

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Groq API Key (https://console.groq.com)

### Clone Repository
```bash
git clone https://github.com/AmaedaQ/sia-retention-ai-agent.git
cd sia-retention-ai-agent
pip install -r requirements.txt
````

### Environment Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_actual_api_key_here
```

### Run the System

```bash
# Generate synthetic subscriber data
python backend/data_generator.py

# Launch the application
streamlit run frontend/app.py
```

---

## Core Business Impact

* **Revenue Preservation**
  Automatically identifies and retains high-value subscribers before churn.

* **Operational Scalability**
  Eliminates manual churn analysis using sub-second AI-driven reasoning.

* **Hyper-Personalization**
  Replaces generic campaigns with individualized retention strategies.

## Roadmap: real ML risk scoring (in progress)

The churn-risk score currently comes from a hand-written formula over
synthetic data — honest, but not a trained model. Phase 0 (data/model
contracts, config, tests) and Phase 1 (real dataset pipeline) are done;
Phase 2 (a trained XGBoost model, real test ROC-AUC 0.79 vs. the old
formula's 0.51, published at
[amaedaqureshi/sia-churn-model](https://huggingface.co/amaedaqureshi/sia-churn-model))
and Phase 3 (wiring that model into `backend/models/loader.py` and
`backend/models/predict.py`, behind the `USE_ML_MODEL` feature flag, with
a safe fallback to the original formula on any failure) are both done.
Phase 4 (retiring the formula path once the model's been trusted in
practice, and redeploying the dashboard with real metrics instead of the
hardcoded 94.2%) is what's left. All of this runs on free-tier compute
(Google Colab + Hugging Face Hub). See `backend/schemas.py` and
`config/settings.py` for the contracts this is built around.

**Phase 1 status:** `notebooks/01_data_pipeline.py` loads the real
[IBM/Kaggle Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
(~7,043 customers, 26.58% churn rate), cleans it, adds four clearly
documented synthetic bridge columns for fields this dataset doesn't have,
validates every row against the `Subscriber` schema, and writes a
stratified train/val/test split to `data/processed/` — see
`data/processed/DATASET_CARD.md` for exactly what's real vs. synthetic,
and `notebooks/README.md` for how to push the result to Hugging Face.

---

---

## Contribution & Contact

Developed by **Amaeda Qureshi**.
Contributions to agent logic, analytics, or UI/UX are welcome via pull requests.

* GitHub: [https://github.com/AmaedaQ](https://github.com/AmaedaQ)
* LinkedIn: [https://www.linkedin.com/in/amaeda-qureshi-305bb928a](https://www.linkedin.com/in/amaeda-qureshi-305bb928a)

---

**Built for the Future of Autonomous Telecom Operations**
