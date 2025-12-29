import sys
import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.monitor import monitor_churn_risks
from agents.decider import get_batch_retention_plans

class AgentState(TypedDict):
    threshold: float 
    risky_users: List[dict]
    final_reports: List[dict]

def monitor_node(state: AgentState):
    t = state.get("threshold", 0.7)
    users = monitor_churn_risks(threshold=t)
    return {"risky_users": users}

def decider_node(state: AgentState):
    # Performance ke liye top 5 ko batch mein process karein
    top_targets = state['risky_users'][:5]
    print(f"🤖 [DECIDER] Analyzing batch of {len(top_targets)} users...")
    reports = get_batch_retention_plans(top_targets)
    return {"final_reports": reports}

def auditor_node(state: AgentState):
    print("⚖️ [AUDITOR] Reviewing and finalizing AI strategies...")
    return {"final_reports": state["final_reports"]}

workflow = StateGraph(AgentState)
workflow.add_node("monitor", monitor_node)
workflow.add_node("decider", decider_node)
workflow.add_node("auditor", auditor_node)

workflow.add_edge(START, "monitor")
workflow.add_edge("monitor", "decider")
workflow.add_edge("decider", "auditor")
workflow.add_edge("auditor", END)

retention_app = workflow.compile()