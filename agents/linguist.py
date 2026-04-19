"""
agents/linguist.py
Agent 2: The Linguist — Language & Context Detector
Fast-path agent. First to run. Identifies language, framework, input type.
"""

import logging
from models.schemas import InquisitorState, LinguistOutput
from prompts.agent_prompts import LINGUIST_PROMPT
from utils.gemini_client import call_gemini
from utils.json_parser import parse_json_safe

logger = logging.getLogger(__name__)


def linguist_node(state: InquisitorState) -> InquisitorState:
    """
    The Linguist: analyzes submitted text to detect programming language,
    framework, runtime, input type, and code quality signals.

    Args:
        state: Current InquisitorState with raw_input populated

    Returns:
        Updated state with linguist_output populated (or error set)
    """
    logger.info("[Linguist] Starting language detection...")

    try:
        user_content = f"Analyze this submission:\n\n{state.raw_input}"
        raw_response = call_gemini(
            system_prompt=LINGUIST_PROMPT,
            user_content=user_content,
            max_tokens=512,
        )

        output = parse_json_safe(raw_response, LinguistOutput)

        if output is None:
            logger.error("[Linguist] Failed to parse response")
            state.error = "The Linguist agent failed to parse the response. Please try again."
            # Provide a safe fallback
            state.linguist_output = LinguistOutput(
                language="unknown",
                confidence=0.0,
                input_type="mixed",
                code_quality_signals=[],
                reasoning="Detection failed — please retry.",
            )
        else:
            logger.info(f"[Linguist] Detected: {output.language} (confidence: {output.confidence:.0%})")
            state.linguist_output = output

    except Exception as e:
        logger.error(f"[Linguist] Exception: {e}")
        state.error = f"Linguist agent error: {str(e)}"
        state.linguist_output = LinguistOutput(
            language="unknown",
            confidence=0.0,
            input_type="mixed",
            code_quality_signals=[],
            reasoning="Detection failed due to API error.",
        )

    return state
