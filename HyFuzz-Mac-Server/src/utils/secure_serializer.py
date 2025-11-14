"""
Secure Serialization Module for HyFuzz

This module provides secure alternatives to pickle for serializing and deserializing
data. It supports:
1. JSON serialization (safe, widely compatible)
2. Signed pickle with HMAC verification (for performance-critical cases)

Security Features:
- HMAC-based integrity verification for pickle data
- JSON as primary serialization format
- Protection against tampering and code injection
- Configurable secret keys via environment variables

Usage:
    from src.utils.secure_serializer import SecureSerializer

    serializer = SecureSerializer()

    # JSON serialization (recommended)
    data = serializer.dumps_json(my_data)
    loaded = serializer.loads_json(data)

    # Signed pickle (for complex objects)
    data = serializer.dumps_signed_pickle(my_data)
    loaded = serializer.loads_signed_pickle(data)

Author: HyFuzz Team
Version: 1.0.0
Date: 2025
"""

import json
import pickle
import hmac
import hashlib
import logging
import os
from typing import Any, Optional, Dict, List
from pathlib import Path
from datetime import datetime
from dataclasses import asdict, is_dataclass

logger = logging.getLogger(__name__)


class SerializationError(Exception):
    """Raised when serialization fails"""
    pass


class DeserializationError(Exception):
    """Raised when deserialization fails"""
    pass


class IntegrityError(Exception):
    """Raised when data integrity check fails"""
    pass


class SecureSerializer:
    """
    Secure data serializer with multiple backends.

    Provides safe serialization alternatives to raw pickle, with integrity
    verification and support for both JSON and signed pickle formats.
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize secure serializer.

        Args:
            secret_key: Secret key for HMAC signing. If not provided,
                       will use SERIALIZATION_SECRET from environment,
                       or generate a temporary one (not suitable for production)
        """
        self.secret_key = secret_key or os.getenv("SERIALIZATION_SECRET")

        if not self.secret_key:
            logger.warning(
                "No secret key provided for serialization. "
                "Using a temporary key. Set SERIALIZATION_SECRET environment "
                "variable for production use."
            )
            # Generate temporary key (will be different each run)
            self.secret_key = os.urandom(32).hex()

        self.secret_key_bytes = self.secret_key.encode('utf-8')

    def _compute_hmac(self, data: bytes) -> bytes:
        """
        Compute HMAC signature for data.

        Args:
            data: Data to sign

        Returns:
            HMAC signature bytes
        """
        return hmac.new(
            self.secret_key_bytes,
            data,
            hashlib.sha256
        ).digest()

    def _verify_hmac(self, data: bytes, signature: bytes) -> bool:
        """
        Verify HMAC signature.

        Args:
            data: Original data
            signature: HMAC signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = self._compute_hmac(data)
        return hmac.compare_digest(expected_signature, signature)

    # =========================================================================
    # JSON SERIALIZATION (RECOMMENDED - SAFE AND PORTABLE)
    # =========================================================================

    def dumps_json(self, obj: Any) -> str:
        """
        Serialize object to JSON string.

        Args:
            obj: Object to serialize

        Returns:
            JSON string

        Raises:
            SerializationError: If serialization fails
        """
        try:
            # Handle dataclasses
            if is_dataclass(obj) and not isinstance(obj, type):
                obj = asdict(obj)

            # Handle dict of dataclasses
            if isinstance(obj, dict):
                obj = {
                    k: asdict(v) if (is_dataclass(v) and not isinstance(v, type)) else v
                    for k, v in obj.items()
                }

            return json.dumps(obj, default=self._json_default)
        except Exception as e:
            logger.error(f"JSON serialization failed: {e}")
            raise SerializationError(f"Failed to serialize to JSON: {e}")

    def loads_json(self, data: str) -> Any:
        """
        Deserialize object from JSON string.

        Args:
            data: JSON string

        Returns:
            Deserialized object

        Raises:
            DeserializationError: If deserialization fails
        """
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"JSON deserialization failed: {e}")
            raise DeserializationError(f"Failed to deserialize from JSON: {e}")

    def dump_json(self, obj: Any, file_path: Path) -> None:
        """
        Serialize object to JSON file.

        Args:
            obj: Object to serialize
            file_path: Path to output file

        Raises:
            SerializationError: If serialization fails
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(obj, f, default=self._json_default, indent=2)
            logger.debug(f"Serialized to JSON file: {file_path}")
        except Exception as e:
            logger.error(f"JSON file serialization failed: {e}")
            raise SerializationError(f"Failed to serialize to JSON file: {e}")

    def load_json(self, file_path: Path) -> Any:
        """
        Deserialize object from JSON file.

        Args:
            file_path: Path to input file

        Returns:
            Deserialized object

        Raises:
            DeserializationError: If deserialization fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"JSON file deserialization failed: {e}")
            raise DeserializationError(f"Failed to deserialize from JSON file: {e}")

    @staticmethod
    def _json_default(obj: Any) -> Any:
        """
        JSON encoder for non-standard types.

        Args:
            obj: Object to encode

        Returns:
            JSON-serializable representation
        """
        # Handle datetime
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle Path
        if isinstance(obj, Path):
            return str(obj)

        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        # Handle dataclasses
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        # Try to convert to dict
        if hasattr(obj, '__dict__'):
            return obj.__dict__

        # Fallback to string representation
        return str(obj)

    # =========================================================================
    # SIGNED PICKLE SERIALIZATION (FOR COMPLEX OBJECTS)
    # =========================================================================

    def dumps_signed_pickle(self, obj: Any) -> bytes:
        """
        Serialize object to signed pickle bytes.

        The format is: HMAC(32 bytes) + pickle_data

        Args:
            obj: Object to serialize

        Returns:
            Signed pickle bytes

        Raises:
            SerializationError: If serialization fails
        """
        try:
            # Serialize with pickle
            pickle_data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

            # Compute HMAC signature
            signature = self._compute_hmac(pickle_data)

            # Combine signature and data
            signed_data = signature + pickle_data

            logger.debug(f"Created signed pickle: {len(signed_data)} bytes")
            return signed_data

        except Exception as e:
            logger.error(f"Signed pickle serialization failed: {e}")
            raise SerializationError(f"Failed to serialize to signed pickle: {e}")

    def loads_signed_pickle(self, data: bytes) -> Any:
        """
        Deserialize object from signed pickle bytes.

        Args:
            data: Signed pickle bytes

        Returns:
            Deserialized object

        Raises:
            DeserializationError: If deserialization fails
            IntegrityError: If signature verification fails
        """
        try:
            # Minimum size check (32 bytes for HMAC + some data)
            if len(data) < 33:
                raise IntegrityError("Data too short to contain valid signature")

            # Extract signature and pickle data
            signature = data[:32]
            pickle_data = data[32:]

            # Verify HMAC signature
            if not self._verify_hmac(pickle_data, signature):
                raise IntegrityError(
                    "HMAC signature verification failed. "
                    "Data may have been tampered with or was signed with a different key."
                )

            # Deserialize pickle data
            obj = pickle.loads(pickle_data)

            logger.debug("Successfully deserialized signed pickle")
            return obj

        except IntegrityError:
            raise
        except Exception as e:
            logger.error(f"Signed pickle deserialization failed: {e}")
            raise DeserializationError(f"Failed to deserialize from signed pickle: {e}")

    def dump_signed_pickle(self, obj: Any, file_path: Path) -> None:
        """
        Serialize object to signed pickle file.

        Args:
            obj: Object to serialize
            file_path: Path to output file

        Raises:
            SerializationError: If serialization fails
        """
        try:
            signed_data = self.dumps_signed_pickle(obj)
            with open(file_path, 'wb') as f:
                f.write(signed_data)
            logger.debug(f"Serialized to signed pickle file: {file_path}")
        except Exception as e:
            logger.error(f"Signed pickle file serialization failed: {e}")
            raise SerializationError(f"Failed to serialize to signed pickle file: {e}")

    def load_signed_pickle(self, file_path: Path) -> Any:
        """
        Deserialize object from signed pickle file.

        Args:
            file_path: Path to input file

        Returns:
            Deserialized object

        Raises:
            DeserializationError: If deserialization fails
            IntegrityError: If signature verification fails
        """
        try:
            with open(file_path, 'rb') as f:
                signed_data = f.read()
            return self.loads_signed_pickle(signed_data)
        except (DeserializationError, IntegrityError):
            raise
        except Exception as e:
            logger.error(f"Signed pickle file deserialization failed: {e}")
            raise DeserializationError(f"Failed to deserialize from signed pickle file: {e}")


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

# Create a global serializer instance for convenience
_global_serializer: Optional[SecureSerializer] = None


def get_serializer() -> SecureSerializer:
    """
    Get global serializer instance.

    Returns:
        SecureSerializer instance
    """
    global _global_serializer
    if _global_serializer is None:
        _global_serializer = SecureSerializer()
    return _global_serializer


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def dumps_json(obj: Any) -> str:
    """Serialize object to JSON string using global serializer"""
    return get_serializer().dumps_json(obj)


def loads_json(data: str) -> Any:
    """Deserialize object from JSON string using global serializer"""
    return get_serializer().loads_json(data)


def dump_json(obj: Any, file_path: Path) -> None:
    """Serialize object to JSON file using global serializer"""
    return get_serializer().dump_json(obj, file_path)


def load_json(file_path: Path) -> Any:
    """Deserialize object from JSON file using global serializer"""
    return get_serializer().load_json(file_path)


def dumps_signed_pickle(obj: Any) -> bytes:
    """Serialize object to signed pickle using global serializer"""
    return get_serializer().dumps_signed_pickle(obj)


def loads_signed_pickle(data: bytes) -> Any:
    """Deserialize object from signed pickle using global serializer"""
    return get_serializer().loads_signed_pickle(data)


def dump_signed_pickle(obj: Any, file_path: Path) -> None:
    """Serialize object to signed pickle file using global serializer"""
    return get_serializer().dump_signed_pickle(obj, file_path)


def load_signed_pickle(file_path: Path) -> Any:
    """Deserialize object from signed pickle file using global serializer"""
    return get_serializer().load_signed_pickle(file_path)


# ==============================================================================
# END OF MODULE
# ==============================================================================
