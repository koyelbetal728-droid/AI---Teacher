# security.py
"""
Security utilities for the AI Teacher backend.

This module provides password hashing and JWT-based
authentication helpers.

The implementation is intentionally kept simple so it can
be extended later with refresh tokens, roles, permissions,
or OAuth authentication.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext

from app.config import settings


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against a stored hash.
    """

    if not plain_password or not hashed_password:
        return False

    try:
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT configuration
# ---------------------------------------------------------------------------

def _get_secret_key() -> str:
    """
    Get the JWT secret key from application settings.
    """

    secret_key = getattr(
        settings,
        "jwt_secret_key",
        None,
    )

    if not secret_key:
        secret_key = getattr(
            settings,
            "secret_key",
            None,
        )

    if not secret_key:
        raise RuntimeError(
            "JWT secret key is not configured. "
            "Set JWT_SECRET_KEY in the environment."
        )

    return secret_key


def _get_algorithm() -> str:
    """
    Get the configured JWT signing algorithm.
    """

    return getattr(
        settings,
        "jwt_algorithm",
        "HS256",
    )


def _get_expiration_minutes() -> int:
    """
    Get the configured JWT expiration time.
    """

    value = getattr(
        settings,
        "access_token_expire_minutes",
        None,
    )

    if value is None:
        value = getattr(
            settings,
            "jwt_expiration_minutes",
            60,
        )

    return int(value)


# ---------------------------------------------------------------------------
# JWT creation
# ---------------------------------------------------------------------------

def create_access_token(
    subject: str | int,
    *,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject:
            Unique identifier of the authenticated user.

        expires_delta:
            Optional custom token lifetime.

        extra_claims:
            Additional claims to include in the token.
    """

    now = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=_get_expiration_minutes()
        )

    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        _get_secret_key(),
        algorithm=_get_algorithm(),
    )


def create_refresh_token(
    subject: str | int,
    *,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create a longer-lived refresh token.

    If no refresh-token expiration setting exists, a default
    lifetime of 7 days is used.
    """

    now = datetime.now(timezone.utc)

    if expires_delta is None:
        refresh_minutes = getattr(
            settings,
            "refresh_token_expire_minutes",
            60 * 24 * 7,
        )

        expires_delta = timedelta(
            minutes=int(refresh_minutes)
        )

    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        _get_secret_key(),
        algorithm=_get_algorithm(),
    )


# ---------------------------------------------------------------------------
# JWT decoding / validation
# ---------------------------------------------------------------------------

def decode_token(
    token: str,
    *,
    verify_expiration: bool = True,
) -> Optional[dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Returns the decoded payload when valid.
    Returns None when the token is invalid or expired.
    """

    if not token:
        return None

    try:
        options = {
            "verify_exp": verify_expiration,
        }

        payload = jwt.decode(
            token,
            _get_secret_key(),
            algorithms=[_get_algorithm()],
            options=options,
        )

        if not isinstance(payload, dict):
            return None

        return payload

    except jwt.PyJWTError:
        return None
    except Exception:
        return None


def get_token_subject(
    token: str,
) -> Optional[str]:
    """
    Extract the subject/user ID from a JWT token.
    """

    payload = decode_token(token)

    if not payload:
        return None

    subject = payload.get("sub")

    if subject is None:
        return None

    return str(subject)


def is_token_expired(
    token: str,
) -> bool:
    """
    Check whether a JWT token is expired.

    Invalid tokens are treated as expired.
    """

    if not token:
        return True

    payload = decode_token(
        token,
        verify_expiration=False,
    )

    if not payload:
        return True

    expiration = payload.get("exp")

    if expiration is None:
        return True

    try:
        expiration_time = datetime.fromtimestamp(
            float(expiration),
            tz=timezone.utc,
        )

        return expiration_time <= datetime.now(timezone.utc)

    except (TypeError, ValueError, OSError):
        return True


def validate_token(
    token: str,
) -> bool:
    """
    Return True when a token is valid and not expired.
    """

    return decode_token(token) is not None


# ---------------------------------------------------------------------------
# Authorization helpers
# ---------------------------------------------------------------------------

def get_token_claim(
    token: str,
    claim: str,
    default: Any = None,
) -> Any:
    """
    Retrieve an arbitrary claim from a valid token.
    """

    payload = decode_token(token)

    if not payload:
        return default

    return payload.get(claim, default)


def has_role(
    token: str,
    role: str,
) -> bool:
    """
    Check whether the token contains the requested role.
    """

    token_role = get_token_claim(token, "role")

    if isinstance(token_role, list):
        return role in token_role

    return token_role == role


def has_permission(
    token: str,
    permission: str,
) -> bool:
    """
    Check whether the token contains a requested permission.
    """

    permissions = get_token_claim(
        token,
        "permissions",
        [],
    )

    if isinstance(permissions, str):
        permissions = [permissions]

    if not isinstance(permissions, list):
        return False

    return permission in permissions