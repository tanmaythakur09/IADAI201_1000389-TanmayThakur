"""
Cryptographic security module for ParkVision AI.
Uses PBKDF2-HMAC-SHA256 with 200,000+ iterations and per-user random salt.
Uses hmac.compare_digest for constant-time hash comparisons.
"""

import hashlib
import hmac
import secrets

PBKDF2_ITERATIONS = 200_000
HASH_NAME = "sha256"


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """
    Hashes a plaintext password using PBKDF2-HMAC-SHA256.
    
    Args:
        password: Raw user password string.
        salt: Optional salt bytes. If None, 32 cryptographically secure random bytes are generated.
        
    Returns:
        tuple[str, str]: (hex_hash, hex_salt)
    """
    if salt is None:
        salt = secrets.token_bytes(32)

    derived = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return derived.hex(), salt.hex()


def verify_password(password: str, stored_hash: str, stored_salt_hex: str) -> bool:
    """
    Verifies a password against the stored hash and salt in constant time.
    
    Args:
        password: Raw password attempt.
        stored_hash: Hex-encoded hash stored in the database.
        stored_salt_hex: Hex-encoded salt stored in the database.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    try:
        salt = bytes.fromhex(stored_salt_hex)
        derived = hashlib.pbkdf2_hmac(
            HASH_NAME,
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(derived.hex(), stored_hash)
    except Exception:
        return False
