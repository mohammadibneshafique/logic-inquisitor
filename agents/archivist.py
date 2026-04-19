"""
agents/archivist.py
Agent 5: The Archivist — Session Memory & Pattern Tracker
Activates only after 3+ submissions. Generates learning profiles.
"""

import json
import logging
from models.schemas import InquisitorState, ArchivistOutput, PatternCard
from prompts.agent_prompts import ARCHIVIST_PROMPT
from utils.gemini_client import call_gemini
from utils.json_parser import parse_json_safe

logger = logging.getLogger(__name__)


def archivist_node(state: InquisitorState) -> InquisitorState:
    """
    The Archivist: analyzes session history to detect recurring patterns.
    Only activates when 3 or more submissions have been made.
    Returns empty output for fewer submissions (by design).

    Args:
        state: Current InquisitorState with session_history populated

    Returns:
        Updated state with archivist_output populated
    """
    submission_count = len(state.session_history)
    logger.info(f"[Archivist] Checking session history: {submission_count} submissions")

    # Only activate after 3+ submissions
    if submission_count < 3:
        logger.info(f"[Archivist] Not enough submissions ({submission_count}/3). Returning empty output.")
        state.archivist_output = ArchivistOutput(
            submission_count=submission_count,
            pattern_cards=[],
            recurring_bug_types=[],
            recommended_topics=[],
        )
        return state

    try:
        history_data = [record.model_dump() for record in state.session_history]
        user_content = (
            f"SESSION SUBMISSION HISTORY ({submission_count} submissions):\n"
            f"{json.dumps(history_data, indent=2)}\n\n"
            f"Analyze patterns and generate a supportive learning profile."
        )

        raw_response = call_gemini(
            system_prompt=ARCHIVIST_PROMPT,
            user_content=user_content,
            max_tokens=1024,
        )

        output = parse_json_safe(raw_response, ArchivistOutput)

        if output is None:
            logger.error("[Archivist] Failed to parse response")
            state.archivist_output = ArchivistOutput(
                submission_count=submission_count,
                pattern_cards=[],
                recurring_bug_types=[],
                recommended_topics=[],
            )
        else:
            logger.info(f"[Archivist] Generated {len(output.pattern_cards)} pattern cards")
            state.archivist_output = output

    except Exception as e:
        logger.error(f"[Archivist] Exception: {e}")
        state.archivist_output = ArchivistOutput(
            submission_count=submission_count,
            pattern_cards=[],
            recurring_bug_types=[],
            recommended_topics=[],
        )

    return state
