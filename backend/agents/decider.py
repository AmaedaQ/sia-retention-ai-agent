import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def get_batch_retention_plans(users_list):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found. Check .env file.")
        return []

    llm = ChatGroq(
        temperature=0.1, 
        model_name="llama-3.3-70b-versatile", 
        groq_api_key=api_key
    )

    system_prompt = """
    You are SIA, the Strategic Intelligence Agent. Analyze the customer data batch.
    Identify the best retention strategy: 'Magic Bundle', 'Network Discount', or 'Recharge Bonus'.
    Output MUST be a valid JSON list only.
    Format: [{"user_id": "...", "reasoning": "...", "offer": "..."}]
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze this batch: {users_info}")
    ])

    try:
        chain = prompt | llm
        response = chain.invoke({"users_info": json.dumps(users_list)})
        content = response.content.strip()
        
        # Clean JSON if LLM adds markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"❌ AI Decision Error: {e}")
        return []