"""
Input validation and password strength evaluation for ParkVision AI.
"""

import re
from typing import Tuple, Dict, Any

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def validate_email(email: str) -> Tuple[bool, str]:
    """Validates an email address format."""
    clean = email.strip()
    if not clean:
        return False, "Email address is required."
    if not EMAIL_REGEX.match(clean):
        return False, "Please enter a valid email address (e.g., analyst@company.com)."
    return True, ""


def evaluate_password_strength(password: str) -> Dict[str, Any]:
    """
    Evaluates password strength and returns score, label, color, and criteria checks.
    Minimum required length is 8 characters.
    """
    length_ok = len(password) >= 8
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password))

    # Calculate score based on criteria met
    score = 0
    if length_ok:
        score += 1
    if has_upper and has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_special:
        score += 1

    labels = {
        0: ("Very Weak", "#ef4444", 15),
        1: ("Weak", "#f97316", 30),
        2: ("Fair", "#f59e0b", 55),
        3: ("Good", "#3b82f6", 80),
        4: ("Strong", "#10b981", 100),
    }

    label, color, pct = labels.get(score, ("Weak", "#ef4444", 20))

    return {
        "score": score,
        "label": label,
        "color": color,
        "percentage": pct,
        "is_valid": length_ok,  # Minimum 8 characters is the hard requirement
        "checks": {
            "At least 8 characters": length_ok,
            "Uppercase & lowercase letters": has_upper and has_lower,
            "At least one number": has_digit,
            "At least one special symbol": has_special,
        },
    }


def validate_signup(
    full_name: str,
    email: str,
    password: str,
    confirm_password: str,
) -> Tuple[bool, str]:
    """Validates all signup fields."""
    if not full_name.strip():
        return False, "Full name is required."
    
    if len(full_name.strip()) < 2:
        return False, "Full name must be at least 2 characters."

    email_valid, email_err = validate_email(email)
    if not email_valid:
        return False, email_err

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if password != confirm_password:
        return False, "Passwords do not match."

    return True, ""
