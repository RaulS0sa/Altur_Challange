import json
import os
from groq import Groq

# Set your GROQ_API_KEY in .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_analysis(conversation: str):
    prompt = f"""
    You are analyzing a customer support phone call.
    Return STRICT JSON only.

    Output schema:
    {{
        "summary": "string (max 2 sentences)",
        "tags": {{
            "intent": "money_transfer | account_issue | support_request | other",
            "outcome": "completed | failed | unknown",
            "sentiment": "positive | neutral | negative",
            "customer_emotion": "calm | happy | frustrated | angry",
            "agent_performance": "helpful | unhelpful",
            "escalation": "yes | no"
        }}
    }}

    Conversation:
    {conversation}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Extremely fast
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return {
            "summary": "Analysis failed.",
            "tags": {"intent": "other", "sentiment": "neutral"}
        }