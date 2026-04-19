"""
agents/socrates.py
Agent 4: The Socrates — Hint Ladder Engine (Crown Jewel)
Generates the 3-tier Socratic hint ladder. NEVER reveals the answer.
"""

import logging
from models.schemas import InquisitorState, SocratesOutput
from prompts.agent_prompts import SOCRATES_PROMPT
from utils.gemini_client import call_gemini
from utils.json_parser import parse_json_safe

logger = logging.getLogger(__name__)


def socrates_node(state: InquisitorState) -> InquisitorState:
    """
    The Socrates: generates a 3-tier Socratic hint ladder.
    Takes Linguist + Pathologist outputs as context.
    NEVER reveals the bug name, fix, or solution.

    Args:
        state: Current InquisitorState with pathologist_output populated

    Returns:
        Updated state with socrates_output populated
    """
    logger.info("[Socrates] Generating Socratic hint ladder...")

    if state.pathologist_output is None:
        state.error = "Socrates cannot run: Pathologist output is missing."
        return state

    try:
        analysis_context = {
            "linguist": state.linguist_output.model_dump() if state.linguist_output else {},
            "pathologist": state.pathologist_output.model_dump(),
        }

        import json
        user_content = (
            f"SPECIALIST AGENT ANALYSIS:\n{json.dumps(analysis_context, indent=2)}\n\n"
            f"ORIGINAL CODE SUBMISSION:\n```{state.linguist_output.language if state.linguist_output else ''}\n"
            f"{state.raw_input}\n```\n\n"
            f"Generate your three-tier Socratic hint ladder. "
            f"Remember: NEVER name the bug, NEVER write corrected code, NEVER give the answer."
        )

        raw_response = call_gemini(
            system_prompt=SOCRATES_PROMPT,
            user_content=user_content,
            max_tokens=1024,
        )

        output = parse_json_safe(raw_response, SocratesOutput)

        if output is None:
            logger.error("[Socrates] Failed to parse response")
            state.error = "The Socrates agent failed to parse the response. Please try again."
            state.socrates_output = SocratesOutput(
                tier1="Consider what assumptions your program makes about its inputs. Are those assumptions always valid?",
                tier2="Look carefully at the boundaries in your code — where does your program start and where does it stop?",
                tier3="Trace through your code with the smallest possible valid input. What happens at the very edge?",
                concept_url="https://cs50.harvard.edu/x/",
                concept_name="Boundary Conditions",
                current_tier=1,
            )
        else:
            logger.info(f"[Socrates] Generated hint ladder for concept: {output.concept_name}")
            state.socrates_output = output

    except Exception as e:
        logger.error(f"[Socrates] Exception: {e}")
        state.error = f"Socrates agent error: {str(e)}"
        state.socrates_output = SocratesOutput(
            tier1="Consider what assumptions your program makes about its inputs. Are those assumptions always valid?",
            tier2="Look carefully at the boundaries in your code — where does your program start and where does it stop?",
            tier3="Trace through your code with the smallest possible valid input. What happens at the very edge?",
            concept_url="https://cs50.harvard.edu/x/",
            concept_name="Boundary Conditions",
            current_tier=1,
        )

    return state


def escalate_hint(state: InquisitorState, target_tier: int) -> InquisitorState:
    """
    Re-run Socrates with explicit tier escalation context.
    Called when user clicks "I'm still stuck".

    Args:
        state: Current state with existing socrates_output
        target_tier: The tier to escalate to (2 or 3)

    Returns:
        Updated state with refreshed socrates_output at new tier
    """
    logger.info(f"[Socrates] Escalating to Tier {target_tier}...")

    if state.pathologist_output is None or state.socrates_output is None:
        return state

    try:
        import json
        analysis_context = {
            "linguist": state.linguist_output.model_dump() if state.linguist_output else {},
            "pathologist": state.pathologist_output.model_dump(),
            "previous_hints_seen": target_tier - 1,
        }

        user_content = (
            f"The developer has seen Tier {target_tier - 1} hints and is still stuck.\n\n"
            f"ANALYSIS CONTEXT:\n{json.dumps(analysis_context, indent=2)}\n\n"
            f"CODE SUBMISSION:\n```\n{state.raw_input}\n```\n\n"
            f"Regenerate the hint ladder. The developer needs Tier {target_tier} guidance now. "
            f"Make Tier {target_tier} appropriately more specific than Tier {target_tier - 1}, "
            f"but still NEVER reveal the bug name or fix."
        )

        raw_response = call_gemini(
            system_prompt=SOCRATES_PROMPT,
            user_content=user_content,
            max_tokens=1024,
        )

        output = parse_json_safe(raw_response, SocratesOutput)

        if output:
            output.current_tier = target_tier
            state.socrates_output = output
            state.current_hint_tier = target_tier

    except Exception as e:
        logger.error(f"[Socrates escalation] Exception: {e}")
        # Keep existing output, just update tier
        if state.socrates_output:
            state.socrates_output.current_tier = target_tier
        state.current_hint_tier = target_tier

    return state
