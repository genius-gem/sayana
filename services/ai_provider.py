import os

import requests

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# GROQ CLIENT
# ==========================================

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)


def ask_groq(prompt):

    response = groq_client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        max_tokens=500
    )

    return (
        response
        .choices[0]
        .message
        .content
    )


# ==========================================
# OPENROUTER
# ==========================================

def ask_openrouter(prompt):

    api_key = os.getenv(
        "OPENROUTER_API_KEY"
    )

    headers = {

        "Authorization":
        f"Bearer {api_key}",

        "Content-Type":
        "application/json"
    }

    payload = {

        "model":
        "meta-llama/llama-3.3-70b-instruct",

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ]
    }

    response = requests.post(

        "https://openrouter.ai/api/v1/chat/completions",

        headers=headers,

        json=payload,

        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["choices"][0]
        ["message"]["content"]
    )