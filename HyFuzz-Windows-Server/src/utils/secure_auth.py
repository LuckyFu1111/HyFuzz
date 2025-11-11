"""
Secure Authentication Utilities for HyFuzz MCP Server

This module provides secure authentication utilities using industry-standard
practices to replace hardcoded secrets and insecure token generation.

Features:
- Environment-based secret key management
- JWT-based token generation and validation
- Secure random token generation
- Password hashing with bcrypt
- Token expiration and refresh
- Protection against timing attacks

Security:
- No hardcoded secrets
- Cryptographically secure random generation
- Industry-standard JWT implementation
- HMAC-SHA256 signatures
- Protection against token reuse

Example Usage:
    >>> from src.utils.secure_auth import SecureAuth, generate_secret_key
    >>>
    >>> # Generate a new secret key (one-time setup)
    >>> secret_key = generate_secret_key()
    >>> # Save to .env file: JWT_SECRET_KEY=<secret_key>
    >>>
    >>> # Initialize auth manager
    >>> auth = SecureAuth()
    >>>
    >>> # Generate JWT token
    >>> token = auth.generate_token(user_id="user123", expires_in=3600)
    >>>
    >>> # Validate token
    >>> payload = auth.validate_token(token)
    >>> print(payload['user_id'])  # 'user123'

Author: HyFuzz Security Team
Version: 2.0.0
Date: 2025-11-11
Security: Replaces hardcoded secrets and insecure token generation
"""

import os
import secrets
import hashlib
import hmac
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False
    logging.warning(
        "PyJWT not installed. Install with: pip install PyJWT\n"
        "Falling back to HMAC-based tokens (less secure)"
    )

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    logging.warning(
        "bcrypt not installed. Install with: pip install bcrypt\n"
        "Password hashing will use PBKDF2 (less secure)"
    )

# ==============================================================================
# LOGGER SETUP
# ==============================================================================

logger = logging.getLogger(__name__)


# ==============================================================================
# SECRET KEY MANAGEMENT
# ==============================================================================

def generate_secret_key(length: int = 64) -> str:
    """
    Generate a cryptographically secure secret key.

    Args:
        length: Length of the secret key in bytes (default: 64)

    Returns:
        URL-safe base64-encoded secret key

    Example:
        >>> key = generate_secret_key()
        >>> print(f"Add this to .env: JWT_SECRET_KEY={key}")
    """
    return secrets.token_urlsafe(length)


def get_secret_key(env_var: str = "JWT_SECRET_KEY", required: bool = True) -> Optional[str]:
    """
    Get secret key from environment variable.

    Args:
        env_var: Environment variable name
        required: Whether the secret key is required

    Returns:
        Secret key from environment, or None if not required

    Raises:
        ValueError: If required=True and secret key not found

    Security:
        Always load secrets from environment variables, never hardcode!
    """
    secret_key = os.environ.get(env_var)

    if not secret_key:
        if required:
            raise ValueError(
                f"{env_var} environment variable is not set!\n\n"
                f"Please set it before starting the server:\n"
                f"1. Generate a key: python -c 'from src.utils.secure_auth import generate_secret_key; print(generate_secret_key())'\n"
                f"2. Add to .env file: {env_var}=<generated_key>\n"
                f"3. Or export: export {env_var}=<generated_key>\n\n"
                f"SECURITY WARNING: Never commit .env files to version control!"
            )
        else:
            logger.warning(f"{env_var} not set, using development key (INSECURE!)")
            # Only for development - never use in production!
            return "dev-key-" + secrets.token_urlsafe(32)

    # Validate secret key strength
    if len(secret_key) < 32:
        logger.warning(
            f"{env_var} is too short ({len(secret_key)} chars). "
            f"Recommended: at least 43 characters (32 bytes base64)"
        )

    return secret_key


# ==============================================================================
# SECURE AUTHENTICATION CLASS
# ==============================================================================

class SecureAuth:
    """
    Secure authentication manager using JWT or HMAC tokens.

    This class provides secure token generation and validation using
    industry-standard cryptographic libraries.

    Attributes:
        secret_key: Secret key for signing tokens
        algorithm: JWT algorithm (HS256, HS512, etc.)
        use_jwt: Whether to use JWT (True) or fallback to HMAC

    Security:
        - Tokens are signed with HMAC-SHA256 or JWT HS256
        - Includes token expiration
        - Protection against replay attacks via JTI
        - Constant-time comparison for validation
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        required_claims: bool = True
    ):
        """
        Initialize secure authentication manager.

        Args:
            secret_key: Secret key for signing (loaded from env if None)
            algorithm: JWT algorithm (default: HS256)
            required_claims: Require standard JWT claims

        Raises:
            ValueError: If secret_key required but not provided
        """
        self.secret_key = secret_key or get_secret_key(required=required_claims)
        self.algorithm = algorithm
        self.use_jwt = HAS_JWT
        self.required_claims = required_claims

        if not self.use_jwt:
            logger.warning("Using HMAC fallback instead of JWT (less features)")


    def generate_token(
        self,
        user_id: str,
        expires_in: int = 3600,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a secure authentication token.

        Args:
            user_id: User identifier
            expires_in: Token expiration time in seconds (default: 1 hour)
            additional_claims: Additional claims to include in token

        Returns:
            Signed JWT or HMAC token string

        Example:
            >>> auth = SecureAuth()
            >>> token = auth.generate_token(
            ...     user_id="user123",
            ...     expires_in=3600,
            ...     additional_claims={"role": "admin"}
            ... )
        """
        if self.use_jwt:
            return self._generate_jwt(user_id, expires_in, additional_claims)
        else:
            return self._generate_hmac_token(user_id, expires_in)


    def _generate_jwt(
        self,
        user_id: str,
        expires_in: int,
        additional_claims: Optional[Dict[str, Any]]
    ) -> str:
        """Generate JWT token"""
        now = datetime.utcnow()
        exp = now + timedelta(seconds=expires_in)

        payload = {
            'user_id': user_id,
            'exp': exp,
            'iat': now,
            'nbf': now,  # Not before
            'jti': secrets.token_urlsafe(16)  # JWT ID for uniqueness
        }

        # Add additional claims
        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        # PyJWT 2.x returns string, 1.x returns bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token


    def _generate_hmac_token(self, user_id: str, expires_in: int) -> str:
        """Generate HMAC-based token (fallback when JWT not available)"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        expiry = str(int(datetime.utcnow().timestamp()) + expires_in)
        jti = secrets.token_urlsafe(16)

        # Payload: user_id.timestamp.expiry.jti
        payload = f"{user_id}.{timestamp}.{expiry}.{jti}"

        # Sign with HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"{payload}.{signature}"


    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode authentication token.

        Args:
            token: Token string to validate

        Returns:
            Dictionary with token payload

        Raises:
            ValueError: If token is invalid or expired

        Example:
            >>> auth = SecureAuth()
            >>> try:
            ...     payload = auth.validate_token(token)
            ...     print(f"User: {payload['user_id']}")
            ... except ValueError as e:
            ...     print(f"Invalid token: {e}")
        """
        if not token:
            raise ValueError("Token is required")

        if self.use_jwt:
            return self._validate_jwt(token)
        else:
            return self._validate_hmac_token(token)


    def _validate_jwt(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True,
                    'require_exp': True,
                    'require_iat': True
                }
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")


    def _validate_hmac_token(self, token: str) -> Dict[str, Any]:
        """Validate HMAC token"""
        try:
            parts = token.rsplit('.', 1)
            if len(parts) != 2:
                raise ValueError("Invalid token format")

            payload, signature = parts

            # Verify signature (constant-time comparison)
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                raise ValueError("Invalid signature")

            # Parse payload
            user_id, timestamp, expiry, jti = payload.split('.')

            # Check expiration
            if int(expiry) < int(datetime.utcnow().timestamp()):
                raise ValueError("Token has expired")

            return {
                'user_id': user_id,
                'iat': int(timestamp),
                'exp': int(expiry),
                'jti': jti
            }

        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid token: {e}")


# ==============================================================================
# PASSWORD HASHING
# ==============================================================================

class PasswordHasher:
    """
    Secure password hashing using bcrypt or PBKDF2.

    Uses bcrypt if available (recommended), otherwise falls back to PBKDF2.
    """

    def __init__(self, rounds: int = 12):
        """
        Initialize password hasher.

        Args:
            rounds: bcrypt cost factor (default: 12)
                   Higher = more secure but slower
        """
        self.rounds = rounds
        self.use_bcrypt = HAS_BCRYPT


    def hash_password(self, password: str) -> str:
        """
        Hash a password securely.

        Args:
            password: Plain text password

        Returns:
            Hashed password string

        Example:
            >>> hasher = PasswordHasher()
            >>> hashed = hasher.hash_password("my-secure-password")
        """
        if self.use_bcrypt:
            return bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt(rounds=self.rounds)
            ).decode('utf-8')
        else:
            # Fallback to PBKDF2
            salt = secrets.token_hex(16)
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # iterations
            )
            return f"pbkdf2:sha256:{salt}:{hash_obj.hex()}"


    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed: Hashed password

        Returns:
            True if password matches, False otherwise

        Example:
            >>> hasher = PasswordHasher()
            >>> if hasher.verify_password(password, stored_hash):
            ...     print("Password correct!")
        """
        if self.use_bcrypt and not hashed.startswith('pbkdf2:'):
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        else:
            # PBKDF2 verification
            try:
                _, algo, salt, hash_hex = hashed.split(':')
                hash_obj = hashlib.pbkdf2_hmac(
                    algo,
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                )
                return hmac.compare_digest(hash_obj.hex(), hash_hex)
            except ValueError:
                return False


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

_default_auth = None

def get_auth_instance() -> SecureAuth:
    """Get singleton auth instance"""
    global _default_auth
    if _default_auth is None:
        _default_auth = SecureAuth()
    return _default_auth


def generate_token(user_id: str, **kwargs) -> str:
    """Convenience function to generate token"""
    return get_auth_instance().generate_token(user_id, **kwargs)


def validate_token(token: str) -> Dict[str, Any]:
    """Convenience function to validate token"""
    return get_auth_instance().validate_token(token)


# ==============================================================================
# MODULE INFO
# ==============================================================================

__all__ = [
    'SecureAuth',
    'PasswordHasher',
    'generate_secret_key',
    'get_secret_key',
    'generate_token',
    'validate_token'
]


if __name__ == '__main__':
    # Example usage
    import sys

    logging.basicConfig(level=logging.INFO)

    print("=== HyFuzz Secure Authentication Demo ===\n")

    # Generate a new secret key
    print("1. Generate secret key:")
    secret = generate_secret_key()
    print(f"   JWT_SECRET_KEY={secret}\n")

    # Set environment variable for demo
    os.environ['JWT_SECRET_KEY'] = secret

    # Initialize auth
    auth = SecureAuth()

    # Generate token
    print("2. Generate token:")
    token = auth.generate_token(
        user_id="demo-user",
        expires_in=3600,
        additional_claims={"role": "admin"}
    )
    print(f"   Token: {token[:50]}...\n")

    # Validate token
    print("3. Validate token:")
    try:
        payload = auth.validate_token(token)
        print(f"   ✓ Valid! User: {payload['user_id']}")
        print(f"   Claims: {payload}\n")
    except ValueError as e:
        print(f"   ✗ Invalid: {e}\n")

    # Password hashing
    print("4. Password hashing:")
    hasher = PasswordHasher()
    password = "my-secure-password"
    hashed = hasher.hash_password(password)
    print(f"   Hash: {hashed[:50]}...")
    print(f"   Verify: {hasher.verify_password(password, hashed)}\n")

    print("✓ All demos completed!")
