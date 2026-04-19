"""
utils/json_parser.py
Safe JSON extraction from LLM responses.
Handles markdown fences, single quotes, and Pydantic validation.
"""

import json
import re
import logging
from typing import TypeVar, Type, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def parse_json_safe(raw_text: str, model: Type[T]) -> Optional[T]:
    """
    Safely parse a JSON string from an LLM response and validate with Pydantic.

    Handles common LLM response issues:
    - Markdown code fences (```json ... ```)
    - Leading/trailing whitespace
    - Single quotes instead of double quotes (best-effort)

    Args:
        raw_text: Raw text response from the LLM
        model: Pydantic model class to validate against

    Returns:
        Validated Pydantic model instance, or None on failure
    """
    if not raw_text:
        logger.error("parse_json_safe received empty text")
        return None

    cleaned = raw_text.strip()

    # Strip markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    # Extract JSON object or array if there's surrounding text
    json_match = re.search(r"\{[\s\S]*\}", cleaned)
    if json_match:
        cleaned = json_match.group(0)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e}\nRaw text:\n{raw_text[:500]}")
        return None

    try:
        return model.model_validate(parsed)
    except Exception as e:
        logger.error(f"Pydantic validation failed for {model.__name__}: {e}\nParsed: {parsed}")
        return None
