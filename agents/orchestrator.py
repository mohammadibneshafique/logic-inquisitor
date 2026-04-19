"""
agents/orchestrator.py
Agent 1: The Inquisitor — Master Orchestrator
LangGraph state machine that runs all 5 agents in the correct order.
"""

import logging
from langgraph.graph import StateGraph, END, START
from models.schemas import InquisitorState
from agents.linguist import linguist_node
from agents.pathologist import pathologist_node
from agents.socrates import socrates_node
from agents.archivist import archivist_node

logger = logging.getLogger(__name__)


def _error_check(state: InquisitorState) -> str:
    """Conditional edge: route to END if a critical error occurred."""
    if state.error and state.linguist_output is None:
        return "end_with_error"
    return "continue"


def build_pipeline():
    """
    Build and compile the LangGraph multi-agent pipeline.

    Execution order:
        START → linguist → pathologist → socrates → END
                                       ↘ archivist → END

    Returns:
        Compiled LangGraph application
    """
    graph = StateGraph(InquisitorState)

    # Register all agent nodes
    graph.add_node("linguist", linguist_node)
    graph.add_node("pathologist", pathologist_node)
    graph.add_node("socrates", socrates_node)
    graph.add_node("archivist", archivist_node)

    # Define execution flow
    graph.add_edge(START, "linguist")
    graph.add_edge("linguist", "pathologist")
    graph.add_edge("pathologist", "socrates")
    graph.add_edge("pathologist", "archivist")
    graph.add_edge("socrates", END)
    graph.add_edge("archivist", END)

    return graph.compile()


# Compile the pipeline once at module import time
PIPELINE = build_pipeline()
logger.info("[Inquisitor] LangGraph pipeline compiled and ready.")


def run_inquisitor(
    raw_input: str,
    session_id: str,
    session_history: list,
) -> InquisitorState:
    """
    Main entry point for the entire multi-agent pipeline.
    Validates input, initializes state, invokes the graph, returns result.

    Args:
        raw_input: User's code, error message, or problem description
        session_id: Unique session identifier (from st.session_state)
        session_history: List of SubmissionRecord from this session

    Returns:
        Final InquisitorState with all agent outputs populated

    Raises:
        ValueError: If raw_input is empty
    """
    if not raw_input or not raw_input.strip():
        raise ValueError("Input cannot be empty. Please paste your code or describe your problem.")

    logger.info(f"[Inquisitor] Starting pipeline for session {session_id[:8]}...")

    initial_state = InquisitorState(
        raw_input=raw_input.strip(),
        session_id=session_id,
        session_history=session_history,
    )

    try:
        result = PIPELINE.invoke(initial_state)
        logger.info("[Inquisitor] Pipeline completed successfully.")
        return result
    except Exception as e:
        logger.error(f"[Inquisitor] Pipeline failed: {e}")
        initial_state.error = f"Pipeline error: {str(e)}"
        return initial_state
