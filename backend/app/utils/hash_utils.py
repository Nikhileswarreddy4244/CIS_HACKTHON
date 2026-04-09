"""
utils/hash_utils.py
-------------------
Cryptographic hashing and password helpers.
"""

import hashlib
import hmac
import os
from pathlib import Path

from passlib.context import CryptContext

# ── Password hashing (bcrypt) ─────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


# ── File content hashing (SHA-256) ────────────────────────────────────────────
CHUNK_SIZE = 65_536  # 64 KB


def hash_file(path: str | Path) -> str:
    """
    Compute the SHA-256 hash of a file on disk.
    Reads in chunks to handle large files efficiently.
    """
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_bytes(data: bytes) -> str:
    """Compute the SHA-256 hash of an in-memory byte string."""
    return hashlib.sha256(data).hexdigest()


# ── HMAC signature (for signed download URLs, etc.) ──────────────────────────
_SECRET = os.getenv("SECRET_KEY", "change-me-in-production").encode()


def sign_token(payload: str) -> str:
    """HMAC-SHA256 sign an arbitrary string payload."""
    return hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()


def verify_token(payload: str, signature: str) -> bool:
    """Constant-time comparison to verify an HMAC signature."""
    expected = sign_token(payload)
    return hmac.compare_digest(expected, signature)
