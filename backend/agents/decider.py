import json
import os
import sys

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


def get_batch_retention_plans(users_list):
    """Send risky users to AI for personalized retention offers."""
    # Read from config/settings.py (env-backed), not hardcoded -- a model
    # rename or deprecation on Groq's side (e.g. llama-3.3-70b-versatile's
    # Aug 2026 move to enterprise-only) is then a one-line .env change,
    # not a code change.
    llm = ChatGroq(
        temperature=0.1,
        model_name=settings.groq_model,
        groq_api_key=settings.groq_api_key,
    )

    system_prompt = """
    You are SIA, the Jazz AI Strategist. Your goal is to retain high-value telecom customers.
    Recommend one of these offers: 'Magic Bundle', 'Network Discount', or 'Recharge Bonus'.
    Output MUST be a valid JSON list of objects with these keys: 'user_id', 'reasoning', 'offer'.
    """

    # Prompt structure matches the invocation variables
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze this customer batch: {users_info}")
    ])

    chain = prompt | llm
    
    # Pass JSON string of users to the human prompt variable
    response = chain.invoke({"users_info": json.dumps(users_list)})
    
    try:
        content = response.content.strip()
        # Clean potential markdown formatting
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Decider Agent Error: {e}")
        return []
