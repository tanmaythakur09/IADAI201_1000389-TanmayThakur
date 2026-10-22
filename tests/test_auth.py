"""
Unit tests for authentication, password hashing, signup validation, and lockout logic.
"""

import time
import pytest
from auth.security import hash_password, verify_password
from auth.validation import validate_email, evaluate_password_strength, validate_signup


class TestPasswordHashing:
    def test_hash_and_verify_success(self):
        password = "SecurePassword@2026"
        p_hash, salt = hash_password(password)
        assert p_hash is not None
        assert salt is not None
        assert len(salt) == 64  # 32 bytes hex encoded
        assert verify_password(password, p_hash, salt) is True

    def test_hash_and_verify_wrong_password(self):
        password = "CorrectPassword123"
        p_hash, salt = hash_password(password)
        assert verify_password("WrongPassword123", p_hash, salt) is False

    def test_random_salts_produce_different_hashes(self):
        password = "IdenticalPassword"
        h1, s1 = hash_password(password)
        h2, s2 = hash_password(password)
        assert s1 != s2
        assert h1 != h2
        assert verify_password(password, h1, s1) is True
        assert verify_password(password, h2, s2) is True


class TestSignupValidation:
    def test_valid_signup(self):
        valid, msg = validate_signup("Alice Analyst", "alice@example.com", "Password@123", "Password@123")
        assert valid is True
        assert msg == ""

    def test_empty_or_short_name(self):
        valid, msg = validate_signup("", "test@test.com", "Password@123", "Password@123")
        assert valid is False
        assert "name is required" in msg.lower()

        valid, msg = validate_signup("A", "test@test.com", "Password@123", "Password@123")
        assert valid is False
        assert "at least 2 characters" in msg.lower()

    def test_invalid_email(self):
        valid, msg = validate_signup("Bob Smith", "not-an-email", "Password@123", "Password@123")
        assert valid is False
        assert "valid email" in msg.lower()

    def test_password_too_short(self):
        valid, msg = validate_signup("Bob Smith", "bob@example.com", "Pass1", "Pass1")
        assert valid is False
        assert "at least 8 characters" in msg.lower()

    def test_password_mismatch(self):
        valid, msg = validate_signup("Bob Smith", "bob@example.com", "Password@123", "Different@123")
        assert valid is False
        assert "do not match" in msg.lower()


class TestPasswordStrength:
    def test_strength_scoring(self):
        short = evaluate_password_strength("abc")
        assert short["is_valid"] is False

        strong = evaluate_password_strength("MyStrongP@ssw0rd")
        assert strong["is_valid"] is True
        assert strong["score"] >= 3


class TestLockoutLogic:
    def test_session_lockout_after_five_attempts(self, monkeypatch):
        # Mock Streamlit session state
        mock_state = {
            "failed_login_attempts": 0,
            "lockout_until": None,
        }
        monkeypatch.setattr("streamlit.session_state", mock_state)

        from auth.session import record_failed_login, check_lockout, reset_failed_login

        # First 4 attempts should not lock out
        for i in range(1, 5):
            attempts, lockout = record_failed_login()
            assert attempts == i
            assert lockout is None
            is_locked, _ = check_lockout()
            assert is_locked is False

        # 5th attempt should trigger 5-minute lockout (300 seconds)
        attempts, lockout = record_failed_login()
        assert attempts == 5
        assert lockout == 300
        is_locked, remaining = check_lockout()
        assert is_locked is True
        assert 295 <= remaining <= 300

        # Successful login resets the lockout
        reset_failed_login()
        is_locked, remaining = check_lockout()
        assert is_locked is False
        assert mock_state["failed_login_attempts"] == 0


class TestSessionAndUserScoping:
    def test_logout_clears_all_keys(self, monkeypatch):
        class MockSession(dict):
            def clear(self):
                super().clear()

        mock_state = MockSession({
            "authenticated": True,
            "is_guest": True,
            "user": {"full_name": "Tanmay", "email": "tanmay@parkvision.ai"},
            "last_analysis": {"total": 40},
            "display_name": "Tanmay",
            "avatar_initial": "T",
            "guest_analyses": [{"id": 1}],
            "guest_feedback": [{"id": 1}],
        })
        monkeypatch.setattr("streamlit.session_state", mock_state)
        from auth.session import logout
        logout()
        assert "last_analysis" not in mock_state
        assert "display_name" not in mock_state
        assert "guest_analyses" not in mock_state
        assert "guest_feedback" not in mock_state
        assert mock_state["authenticated"] is False
        assert mock_state["is_guest"] is False
        assert mock_state["user"] is None

    def test_database_user_analyses_scoped_by_email(self, tmp_path, monkeypatch):
        from db import database
        test_db = tmp_path / "test_scope.db"
        monkeypatch.setattr(database, "DB_PATH", test_db)
        database.init_db()

        # Save analysis for tanmay
        database.save_analysis(
            user_id=3,
            user_email="tanmay@parkvision.ai",
            image_name="real_lot.jpg",
            total_slots=40,
            occupied_slots=28,
            available_slots=12,
            occupancy_pct=70.0,
            congestion="Moderate",
            recommendation="Good parking",
        )

        # Tanmay should see 1 record
        tanmay_records = database.get_user_analyses_by_email("tanmay@parkvision.ai")
        assert len(tanmay_records) == 1
        assert tanmay_records[0]["image_name"] == "real_lot.jpg"

        # Other user gets empty list
        other_records = database.get_user_analyses_by_email("unknown@parkvision.ai")
        assert other_records == []

