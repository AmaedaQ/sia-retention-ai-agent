import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load .env for local development
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

def get_batch_retention_plans(users_list):
    """Send risky users to AI for personalized retention offers."""
    api_key = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(
        temperature=0.1, 
        model_name="llama-3.3-70b-versatile", 
        groq_api_key=api_key
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