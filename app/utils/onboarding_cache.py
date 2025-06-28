"""
In-memory cache for managing onboarding session state.

In a production environment, this would be replaced with a more robust
distributed cache like Redis to support scaling across multiple server instances.
For our current purposes, a simple dictionary provides the necessary functionality.
"""

from typing import Any
from uuid import UUID

from loguru import logger

# --- In-Memory Session Storage ---
# This dictionary will store session data, keyed by session_id.
_onboarding_sessions: dict[UUID, dict[str, Any]] = {}


def create_session(session_id: UUID) -> None:
    """
    Initializes a new, empty onboarding session in the cache.

    Args:
        session_id: The unique identifier for the new session.
    """
    if session_id in _onboarding_sessions:
        logger.warning(f"Session {session_id} already exists. Overwriting.")
    _onboarding_sessions[session_id] = {}
    logger.info(f"Onboarding session created: {session_id}")


def get_session(session_id: UUID) -> dict[str, Any] | None:
    """
    Retrieves the data for a given onboarding session.

    Args:
        session_id: The ID of the session to retrieve.

    Returns:
        A dictionary containing the session data, or None if not found.
    """
    return _onboarding_sessions.get(session_id)


def update_session(session_id: UUID, step_data: dict[str, Any]) -> bool:
    """
    Updates an existing onboarding session with new data from a completed step.

    Args:
        session_id: The ID of the session to update.
        step_data: A dictionary of data to merge into the session state.

    Returns:
        True if the session was updated successfully, False otherwise.
    """
    session = get_session(session_id)
    if session is None:
        logger.error(f"Attempted to update non-existent session: {session_id}")
        return False

    session.update(step_data)
    logger.info(f"Onboarding session updated: {session_id}")
    return True


def delete_session(session_id: UUID) -> None:
    """
    Removes an onboarding session from the cache after it's finalized.

    Args:
        session_id: The ID of the session to delete.
    """
    if session_id in _onboarding_sessions:
        del _onboarding_sessions[session_id]
        logger.info(f"Onboarding session deleted: {session_id}")
