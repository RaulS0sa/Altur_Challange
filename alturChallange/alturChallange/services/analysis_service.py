import json
import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def transcript_analysis(conversation: str) -> str:
    promt = """
    You are analyzing a customer support phone call.

    Return STRICT JSON only (no markdown, no explanation).

    Output schema:
    {
        "summary": string (max 2 sentences),
        "tags": {
            "intent": "money_transfer | account_issue | support_request | other",
            "outcome": "completed | failed | unknown",
            "sentiment": "positive | neutral | negative",
            "customer_emotion": "calm | happy | sad | angry | frustrated | upset | anxious | depressed | stressed | overwhelmed | scared | anxious | negative",
            "agent_emotion": "calm | happy | sad | angry | frustrated | upset | anxious  | depressed | stressed | overwhelmed | scared | anxious | negative",
            "agent_performance": "good | helpful | unhelpful | poor",
            "escalation": "no | yes"
        }
    }

    Rules:
    - Be concise.
    - Do NOT include any extra keys.
    - Output MUST be valid JSON.
    - If uncertain, use "unknown".
    - Sentiment is based on CUSTOMER tone primarily.

    Conversation:
    """
    return promt + conversation



def run_analysis(conversation: str):
    prompt = transcript_analysis(conversation)

    response = requests.post(
        OLLAMA_URL + "/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
    )

    raw = response.json()["response"]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # fallback: force recovery
        return {
            "summary": "Failed to parse model output",
            "tags": {
                "intent": "other",
                "outcome": "unknown",
                "sentiment": "neutral"
            }
        }