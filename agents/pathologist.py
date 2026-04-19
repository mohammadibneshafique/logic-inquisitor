"""
agents/pathologist.py
Agent 3: The Pathologist — Bug & Problem Classifier
Performs deep semantic analysis. Never suggests fixes. Classify only.
"""

import json
import logging
from models.schemas import InquisitorState, PathologistOutput, SeverityMatrix
from prompts.agent_prompts import PATHOLOGIST_PROMPT
from utils.gemini_client import call_gemini
from utils.json_parser import parse_json_safe

logger = logging.getLogger(__name__)


def pathologist_node(state: InquisitorState) -> InquisitorState:
    """
    The Pathologist: performs a semantic autopsy on the submitted code.
    Identifies bug type, problem category, complexity, and severity.
    NEVER suggests fixes — classify and diagnose only.

    Args:
        state: Current InquisitorState with linguist_output populated

    Returns:
        Updated state with pathologist_output populated (or error set)
    """
    logger.info("[Pathologist] Starting semantic analysis...")

    if state.linguist_output is None:
        state.error = "Pathologist cannot run: Linguist output is missing."
        return state

    try:
        linguist_context = state.linguist_output.model_dump_json(indent=2)
        user_content = (
            f"LINGUIST CONTEXT REPORT:\n{linguist_context}\n\n"
            f"CODE SUBMISSION:\n```{state.linguist_output.language}\n"
            f"{state.raw_input}\n```\n\n"
            f"Perform your semantic autopsy now. Do NOT suggest any fix."
        )

        raw_response = call_gemini(
            system_prompt=PATHOLOGIST_PROMPT,
            user_content=user_content,
            max_tokens=1024,
        )

        output = parse_json_safe(raw_response, PathologistOutput)

        if output is None:
            logger.error("[Pathologist] Failed to parse response")
            state.error = "The Pathologist agent failed to parse the response. Please try again."
            state.pathologist_output = PathologistOutput(
                bug_type="unknown",
                problem_category="unknown",
                complexity_tier="beginner",
                conceptual_gap="Analysis failed — please retry.",
                severity=SeverityMatrix(impact=1, frequency=1, detectability=1, overall="low"),
                reasoning="Analysis failed due to parsing error.",
            )
        else:
            logger.info(f"[Pathologist] Bug type: {output.bug_type} | Severity: {output.severity.overall}")
            state.pathologist_output = output

    except Exception as e:
        logger.error(f"[Pathologist] Exception: {e}")
        state.error = f"Pathologist agent error: {str(e)}"
        state.pathologist_output = PathologistOutput(
            bug_type="unknown",
            problem_category="unknown",
            complexity_tier="beginner",
            conceptual_gap="Analysis failed due to API error.",
            severity=SeverityMatrix(impact=1, frequency=1, detectability=1, overall="low"),
            reasoning="Analysis failed due to API error.",
        )

    return state
