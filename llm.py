 
import json
import os
from typing import Any
import requests
 
api_key = os.getenv('ASI_API_KEY')
if not api_key:
    raise ValueError("ASI_API_KEY environment variable not set.")
HEADERS = {
'Content-Type': 'application/json',
'Accept': 'application/json',
'Authorization': f'Bearer {api_key}'
}
 
URL = "https://api.asi1.ai/v1/chat/completions"
 
MODEL = "asi1-mini"
 
 
async def get_completion(context: str,prompt: str,) -> str:
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": context + " " + prompt
            }
        ],
        "temperature": 0,
        "stream": False,
        "max_tokens": 0
    })
 
    response = requests.request("POST", URL, headers=HEADERS, data=payload)
 
    return response.json()
 
 
 