"""
utils/gemini_client.py
Gemini 1.5 Flash API client with tenacity retry logic.
All agents use this single client — rate limit protection built in.
"""

import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini once on import
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. "
        "Create a .env file with: GEMINI_API_KEY=your_key_here\n"
        "Get a free key at: https://aistudio.google.com/app/apikey"
    )

genai.configure(api_key=_api_key)

# Generation config — tuned for structured JSON output
_generation_config = genai.GenerationConfig(
    temperature=0.1,       # Low temperature = more deterministic JSON
    max_output_tokens=2048,
    response_mime_type="text/plain",
)

_safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_gemini(system_prompt: str, user_content: str, max_tokens: int = 1024) -> str:
    """
    Call Gemini 1.5 Flash with a system prompt and user content.
    Retries up to 3 times with exponential backoff on any error.

    Args:
        system_prompt: The agent's system instructions
        user_content: The user's code/problem submission
        max_tokens: Maximum tokens in response (default 1024)

    Returns:
        Raw text response from Gemini

    Raises:
        Exception: After 3 failed retries
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=max_tokens,
        ),
        safety_settings=_safety_settings,
    )

    response = model.generate_content(user_content)

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text.strip()
