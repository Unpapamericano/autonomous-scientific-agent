"""Small JWT authentication boundary for the MVP API.

The password hash and user table are deliberately isolated from session
storage. Replace this module with the deployment's identity provider (Entra,
Auth0, or another OIDC service) before public multi-tenant operation.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$", 1)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 120_000)
    return hmac.compare_digest(actual.hex(), digest_hex)


class AuthStore:
    def __init__(self, database_path: str = "data/trombone_coach.db") -> None:
        self.database_path = database_path
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS users "
                "(email TEXT PRIMARY KEY, password_hash TEXT NOT NULL)"
            )

    def register(self, credentials: Credentials) -> None:
        with sqlite3.connect(self.database_path) as connection:
            try:
                connection.execute(
                    "INSERT INTO users VALUES (?, ?)",
                    (credentials.email.casefold(), _hash_password(credentials.password)),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("An account with this email already exists.") from exc

    def verify(self, credentials: Credentials) -> bool:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT password_hash FROM users WHERE email = ?", (credentials.email.casefold(),)
            ).fetchone()
        return bool(row and _verify_password(credentials.password, row[0]))


def create_token(email: str) -> str:
    secret = os.getenv("COACH_JWT_SECRET")
    if not secret:
        raise RuntimeError("COACH_JWT_SECRET must be configured before issuing tokens.")
    return jwt.encode(
        {"sub": email.casefold(), "exp": datetime.now(timezone.utc) + timedelta(hours=8)},
        secret,
        algorithm="HS256",
    )


def current_user(token: str | None = Depends(oauth2_scheme)) -> str | None:
    if not token:
        return None
    secret = os.getenv("COACH_JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Authentication is not configured.")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token.") from exc
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=401, detail="Authentication token has no subject.")
    return subject
