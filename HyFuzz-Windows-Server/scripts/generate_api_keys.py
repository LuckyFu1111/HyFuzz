#!/usr/bin/env python3
"""HyFuzz API Key Generator.

Generate secure API keys for HyFuzz platform authentication.

Usage:
    python generate_api_keys.py                  # Generate one key
    python generate_api_keys.py --count 5        # Generate 5 keys
    python generate_api_keys.py --name "Client1" # Named key
"""
import argparse
import json
import secrets
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def save_api_key(name: str, key: str, db_path: Path):
    """Save API key to database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing keys
    if db_path.exists():
        with open(db_path) as f:
            data = json.load(f)
    else:
        data = {"keys": []}

    # Add new key
    data["keys"].append({
        "name": name,
        "key": key,
        "created_at": datetime.utcnow().isoformat(),
        "active": True
    })

    # Save
    with open(db_path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Generate HyFuzz API keys")
    parser.add_argument("--name", "-n", default="default", help="Key name")
    parser.add_argument("--count", "-c", type=int, default=1, help="Number of keys")
    parser.add_argument("--db-path", type=Path, default=PROJECT_ROOT / "data" / "api_keys.json")
    args = parser.parse_args()

    print("\nGenerated API Keys:")
    print("=" * 70)

    for i in range(args.count):
        name = f"{args.name}_{i+1}" if args.count > 1 else args.name
        key = generate_api_key()
        save_api_key(name, key, args.db_path)
        print(f"{name:20} {key}")

    print("=" * 70)
    print(f"✓ Keys saved to: {args.db_path}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
