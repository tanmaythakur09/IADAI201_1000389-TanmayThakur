"""
Session state and lockout management for ParkVision AI.
"""

import time
import streamlit as st
from typing import Tuple, Dict, Any, Optional

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes


def init_session_state() -> None:
    """Initializes authentication and navigation session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "is_guest" not in st.session_state:
        st.session_state["is_guest"] = False

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "failed_login_attempts" not in st.session_state:
        st.session_state["failed_login_attempts"] = 0

    if "lockout_until" not in st.session_state:
        st.session_state["lockout_until"] = None

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"

    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "signin"


def check_lockout() -> Tuple[bool, int]:
    """
    Checks if the user is currently locked out due to excessive failed attempts.
    
    Returns:
        tuple[bool, int]: (is_locked, remaining_seconds)
    """
    lockout_until = st.session_state.get("lockout_until")
    if lockout_until is not None:
        remaining = int(lockout_until - time.time())
        if remaining > 0:
            return True, remaining
        else:
            # Lockout expired, reset attempts
            st.session_state["lockout_until"] = None
            st.session_state["failed_login_attempts"] = 0
            return False, 0
    return False, 0


def record_failed_login() -> Tuple[int, Optional[int]]:
    """
    Records a failed login attempt. Locks the session for 5 minutes if reaching 5 attempts.
    
    Returns:
        tuple[int, Optional[int]]: (attempts_count, lockout_duration_if_triggered)
    """
    current_attempts = st.session_state.get("failed_login_attempts", 0) + 1
    st.session_state["failed_login_attempts"] = current_attempts

    if current_attempts >= MAX_FAILED_ATTEMPTS:
        st.session_state["lockout_until"] = time.time() + LOCKOUT_DURATION_SECONDS
        return current_attempts, LOCKOUT_DURATION_SECONDS
    return current_attempts, None


def reset_failed_login() -> None:
    """Resets failed login attempts upon successful login."""
    st.session_state["failed_login_attempts"] = 0
    st.session_state["lockout_until"] = None


def login_user(user: Dict[str, Any]) -> None:
    """Sets session state for an authenticated user."""
    reset_failed_login()
    st.session_state["authenticated"] = True
    st.session_state["is_guest"] = False
    st.session_state["user"] = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
    }
    st.session_state["current_page"] = "Dashboard"


def login_as_guest() -> None:
    """Sets session state for guest access."""
    reset_failed_login()
    st.session_state["authenticated"] = True
    st.session_state["is_guest"] = True
    st.session_state["user"] = {
        "id": None,
        "full_name": "Guest Visitor",
        "email": "guest@parkvision.ai",
    }
    st.session_state["current_page"] = "Dashboard"


def logout() -> None:
    """Clears all session state keys completely upon sign out."""
    st.session_state.clear()
    init_session_state()
