"""
utils/session.py
Streamlit session state management helpers.
"""

import uuid
import streamlit as st
from models.schemas import SubmissionRecord, InquisitorState


def init_session_state() -> None:
    """Initialize all session state variables if not already present."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "submission_history" not in st.session_state:
        st.session_state.submission_history = []

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if "current_tier" not in st.session_state:
        st.session_state.current_tier = 1

    if "is_analyzing" not in st.session_state:
        st.session_state.is_analyzing = False

    if "agent_statuses" not in st.session_state:
        st.session_state.agent_statuses = {
            "linguist": "idle",
            "pathologist": "idle",
            "socrates": "idle",
            "archivist": "idle",
        }

    if "code_input" not in st.session_state:
        st.session_state.code_input = ""


def reset_agent_statuses() -> None:
    """Reset all agent statuses to idle before a new run."""
    st.session_state.agent_statuses = {
        "linguist": "idle",
        "pathologist": "idle",
        "socrates": "idle",
        "archivist": "idle",
    }


def set_agent_status(agent: str, status: str) -> None:
    """Update a single agent's status."""
    st.session_state.agent_statuses[agent] = status


def add_submission_to_history(result: InquisitorState) -> None:
    """Extract key fields from a result and add to session history."""
    import time
    if result.linguist_output and result.pathologist_output:
        record = SubmissionRecord(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            language=result.linguist_output.language,
            bug_type=result.pathologist_output.bug_type,
            problem_category=result.pathologist_output.problem_category,
            complexity_tier=result.pathologist_output.complexity_tier,
        )
        st.session_state.submission_history.append(record)
