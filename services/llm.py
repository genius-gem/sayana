"""
llm.py

Handles communication with Groq and OpenRouter.
Automatically falls back to OpenRouter if Groq fails.
"""

import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI


# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ==========================================================
# CONFIGURATION
# ==========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-chat"
)


# ==========================================================
# CLIENTS
# ==========================================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)

openrouter_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# ==========================================================
# SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are SayanaBot, an AI healthcare assistant specializing in Sayana Press.

Rules:

1. Answer ONLY using the supplied context.
2. Never invent medical information.
3. Never repeat the same fact.
4. Keep answers between 50 and 150 words.
5. Use simple English.
6. Use bullet points only when helpful.
7. Avoid unnecessary introductions.
8. Do not repeat the user's question.
9. Do not use excessive blank lines.
10. Mention each fact only once.

If the answer is not found in the supplied context, reply exactly:

"I could not find that information in my knowledge base."

Never diagnose diseases.
Never prescribe medication.
Never replace a healthcare professional.
"""


# ==========================================================
# CLEAN RESPONSE
# ==========================================================

def clean_response(text):
    """
    Clean AI response before sending it
    to the frontend.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove quotation marks around the whole response
    text = text.strip('"')

    # Remove trailing spaces
    text = re.sub(r"[ \t]+\n", "\n", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    return text


# ==========================================================
# CALL LLM
# ==========================================================

def call_llm(
    prompt,
    temperature=0.1,
    max_tokens=700
):
    """
    Send prompt to Groq.

    Automatically falls back to OpenRouter
    if Groq is unavailable.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # ------------------------------------------------------
    # TRY GROQ
    # ------------------------------------------------------

    try:

        response = groq_client.chat.completions.create(

            model=GROQ_MODEL,

            messages=messages,

            temperature=temperature,

            max_tokens=max_tokens

        )

        answer = response.choices[0].message.content

        answer = clean_response(answer)

        return answer

    except Exception as groq_error:

        logger.exception(
            "Groq API Error",
            exc_info=groq_error
        )

    # ------------------------------------------------------
    # FALL BACK TO OPENROUTER
    # ------------------------------------------------------

    try:

        response = openrouter_client.chat.completions.create(

            model=OPENROUTER_MODEL,

            messages=messages,

            temperature=temperature,

            max_tokens=max_tokens

        )

        answer = response.choices[0].message.content

        answer = clean_response(answer)

        return answer

    except Exception as openrouter_error:

        logger.exception(
            "OpenRouter API Error",
            exc_info=openrouter_error
        )

        return (
            "I'm sorry, but the AI service is currently unavailable. "
            "Please try again later."
        )