#!/usr/bin/env python3
"""HyFuzz User Management Script.

This script creates new users for the HyFuzz platform with specified roles
and permissions. It supports interactive and non-interactive modes.

Usage:
    python create_user.py                          # Interactive mode
    python create_user.py --username admin --role admin
    python create_user.py --username user1 --role analyst --email user1@example.com
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import logging
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("hyfuzz.create_user")

# User roles and permissions
ROLES = {
    "admin": {
        "description": "Full system access",
        "permissions": ["read", "write", "delete", "admin", "execute"],
    },
    "analyst": {
        "description": "Campaign analysis and reporting",
        "permissions": ["read", "write", "execute"],
    },
    "operator": {
        "description": "Campaign execution only",
        "permissions": ["read", "execute"],
    },
    "viewer": {"description": "Read-only access", "permissions": ["read"]},
}


class UserManager:
    """Manages user creation and validation."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize user manager.

        Args:
            db_path: Path to user database file
        """
        self.db_path = db_path or PROJECT_ROOT / "data" / "users.json"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.users = self._load_users()

    def _load_users(self) -> dict:
        """Load existing users from database.

        Returns:
            Dictionary of users
        """
        if self.db_path.exists():
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load users database: {e}")
        return {"users": []}

    def _save_users(self) -> None:
        """Save users to database."""
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.users, f, indent=2)
            logger.debug(f"Saved users to {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
            raise

    def validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"

        if len(username) < 3:
            return False, "Username must be at least 3 characters"

        if len(username) > 32:
            return False, "Username must be at most 32 characters"

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            return False, "Username can only contain letters, numbers, - and _"

        # Check if username already exists
        for user in self.users.get("users", []):
            if user["username"] == username:
                return False, f"Username '{username}' already exists"

        return True, ""

    def validate_email(self, email: str) -> tuple[bool, str]:
        """Validate email format.

        Args:
            email: Email to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return True, ""  # Email is optional

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        return True, ""

    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        return True, ""

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt.

        Args:
            password: Password to hash
            salt: Salt to use (generates new if not provided)

        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA-256
        hash_obj = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        hashed = hash_obj.hex()

        return hashed, salt

    def create_user(
        self,
        username: str,
        password: str,
        role: str = "viewer",
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> dict:
        """Create a new user.

        Args:
            username: Username
            password: Password
            role: User role
            email: Email address (optional)
            full_name: Full name (optional)

        Returns:
            Created user dictionary

        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        valid, error = self.validate_username(username)
        if not valid:
            raise ValueError(f"Invalid username: {error}")

        valid, error = self.validate_password(password)
        if not valid:
            raise ValueError(f"Invalid password: {error}")

        if email:
            valid, error = self.validate_email(email)
            if not valid:
                raise ValueError(f"Invalid email: {error}")

        if role not in ROLES:
            raise ValueError(
                f"Invalid role '{role}'. Valid roles: {', '.join(ROLES.keys())}"
            )

        # Hash password
        password_hash, salt = self.hash_password(password)

        # Create user object
        user = {
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
            "email": email or "",
            "full_name": full_name or username,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "active": True,
            "permissions": ROLES[role]["permissions"],
        }

        # Add user to database
        self.users.setdefault("users", []).append(user)
        self._save_users()

        logger.info(f"✓ Created user '{username}' with role '{role}'")

        # Return user without sensitive data
        return {k: v for k, v in user.items() if k not in ["password_hash", "salt"]}


def interactive_create_user(manager: UserManager) -> dict:
    """Create user interactively.

    Args:
        manager: UserManager instance

    Returns:
        Created user dictionary
    """
    print("\n" + "=" * 60)
    print("HyFuzz User Creation (Interactive Mode)")
    print("=" * 60 + "\n")

    # Get username
    while True:
        username = input("Username: ").strip()
        valid, error = manager.validate_username(username)
        if valid:
            break
        print(f"  ✗ {error}")

    # Get password
    while True:
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("  ✗ Passwords do not match")
            continue

        valid, error = manager.validate_password(password)
        if valid:
            break
        print(f"  ✗ {error}")

    # Get email
    email = input("Email (optional): ").strip() or None

    # Get full name
    full_name = input("Full name (optional): ").strip() or None

    # Select role
    print("\nAvailable roles:")
    for role, info in ROLES.items():
        print(f"  - {role}: {info['description']}")

    while True:
        role = input(f"Role [viewer]: ").strip() or "viewer"
        if role in ROLES:
            break
        print(f"  ✗ Invalid role. Choose from: {', '.join(ROLES.keys())}")

    # Create user
    try:
        user = manager.create_user(
            username=username,
            password=password,
            role=role,
            email=email,
            full_name=full_name,
        )
        print(f"\n✓ User created successfully!")
        print(f"  Username: {user['username']}")
        print(f"  Role: {user['role']}")
        print(f"  Permissions: {', '.join(user['permissions'])}")
        return user
    except ValueError as e:
        print(f"\n✗ Failed to create user: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create HyFuzz users",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available roles:
{chr(10).join(f'  {role}: {info["description"]}' for role, info in ROLES.items())}
        """,
    )
    parser.add_argument("--username", "-u", help="Username")
    parser.add_argument("--password", "-p", help="Password (use with caution)")
    parser.add_argument(
        "--role",
        "-r",
        choices=list(ROLES.keys()),
        default="viewer",
        help="User role (default: viewer)",
    )
    parser.add_argument("--email", "-e", help="Email address")
    parser.add_argument("--full-name", "-n", help="Full name")
    parser.add_argument(
        "--db-path", type=Path, help="Path to user database file"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize manager
    manager = UserManager(db_path=args.db_path)

    # Interactive mode if no username provided
    if not args.username:
        interactive_create_user(manager)
        return 0

    # Non-interactive mode
    if not args.password:
        print("Error: --password is required in non-interactive mode")
        return 1

    try:
        user = manager.create_user(
            username=args.username,
            password=args.password,
            role=args.role,
            email=args.email,
            full_name=args.full_name,
        )

        print(f"✓ User created: {user['username']} ({user['role']})")
        return 0

    except ValueError as e:
        print(f"✗ Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
