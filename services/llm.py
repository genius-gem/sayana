import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

print("GROQ_API_KEY =", os.getenv("GROQ_API_KEY"))
print("OPENROUTER_API_KEY =", os.getenv("OPENROUTER_API_KEY"))


GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-chat"
)


groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

openrouter_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def call_llm(
    prompt,
    temperature=0.3,
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
            "content": (
                "You are a professional medical education assistant "
                "specialized in Sayana Press. "
                "Only answer using the supplied context. "
                "If the answer is unavailable, say so honestly."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:

        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()

    except Exception as groq_error:

        logger.exception(
            "Groq API Error",
            exc_info=groq_error
        )

        try:

            response = openrouter_client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content.strip()

        except Exception as openrouter_error:

            logger.exception(
                "OpenRouter API Error",
                exc_info=openrouter_error
            )

            return (
                "I'm sorry, but the AI service is currently unavailable. "
                "Please try again later."
            )