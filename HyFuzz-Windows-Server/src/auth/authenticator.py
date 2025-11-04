"""Basic authentication workflow."""

from __future__ import annotations

import hashlib
import os
import warnings
from typing import Dict, Optional

from .auth_models import SessionToken, User
from .user_manager import UserManager
from .jwt_handler import JWTHandler


class Authenticator:
    def __init__(self, jwt_secret: Optional[str] = None) -> None:
        """
        Initialize the authenticator.

        Args:
            jwt_secret: JWT secret key. If None, will try to read from
                       JWT_SECRET environment variable. Falls back to
                       a default value for development ONLY.

        Security Warning:
            In production, ALWAYS set JWT_SECRET environment variable.
            The default value is insecure and only for development/testing.
        """
        self.users = UserManager()

        # Get JWT secret from parameter, environment, or fallback to development default
        if jwt_secret is None:
            jwt_secret = os.getenv("JWT_SECRET")
            if jwt_secret is None:
                # Development-only fallback
                warnings.warn(
                    "JWT_SECRET not set! Using insecure default. "
                    "Set JWT_SECRET environment variable in production.",
                    UserWarning,
                    stacklevel=2,
                )
                jwt_secret = "hyfuzz-dev-secret-CHANGE-IN-PRODUCTION"

        self.jwt = JWTHandler(secret=jwt_secret)

    def _hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> User:
        user = User(username=username, password_hash=self._hash(password))
        self.users.store(user)
        return user

    def login(self, username: str, password: str) -> Dict[str, str]:
        user = self.users.get(username)
        if not user or user.password_hash != self._hash(password):
            raise ValueError("invalid credentials")
        token = SessionToken.create(username)
        self.users.add_session(token)
        jwt_token = self.jwt.issue({"sub": username})
        return {"session": token.token, "jwt": jwt_token}


if __name__ == "__main__":
    # DEMO ONLY - For production, set JWT_SECRET environment variable
    auth = Authenticator(jwt_secret="demo-only-testing")
    auth.register("demo", "password")
    print("Demo login result:", auth.login("demo", "password"))
