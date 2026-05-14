import requests
import os
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def transcribe(file_path: str):
    with open(file_path, "rb") as f:
        audio = f.read()

    response = requests.post(
        "https://api.deepgram.com/v1/listen",
        headers={
            "Authorization": f"Token " + DEEPGRAM_API_KEY,
            "Content-Type": "audio/wav",
        },
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "diarize": "true",
            "utterances": "true"
        },
        data=audio,
    )

    data = response.json()

    utterances = data["results"]["utterances"]
    conversation = []
    for u in utterances:
        conversation.append({
             "speaker" : u["speaker"], 
             "text": u["transcript"]
        })

    return conversation