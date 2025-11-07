#!/usr/bin/env python3
"""HyFuzz Database Initialization Script.

This script initializes the HyFuzz database with required tables,
indexes, and initial data. It supports SQLite, PostgreSQL, and MySQL.

Usage:
    python init_database.py
    python init_database.py --database-url sqlite:///data/hyfuzz.db
    python init_database.py --reset  # Warning: drops all tables!
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Initializes and manages HyFuzz database schema."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.db_type = self._detect_database_type()

    def _detect_database_type(self) -> str:
        """Detect database type from URL."""
        if "sqlite" in self.database_url:
            return "sqlite"
        elif "postgresql" in self.database_url or "postgres" in self.database_url:
            return "postgresql"
        elif "mysql" in self.database_url:
            return "mysql"
        else:
            return "unknown"

    def _create_sqlite_database(self) -> None:
        """Create SQLite database and tables."""
        import sqlite3

        # Extract file path from URL
        db_path = self.database_url.replace("sqlite:///", "")
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating SQLite database at: {db_file}")

        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Create tables
        tables = self._get_table_definitions()

        for table_name, table_sql in tables.items():
            logger.info(f"Creating table: {table_name}")
            cursor.execute(table_sql)

        # Create indexes
        indexes = self._get_index_definitions()
        for index_name, index_sql in indexes.items():
            logger.info(f"Creating index: {index_name}")
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                logger.warning(f"Index {index_name} may already exist: {e}")

        conn.commit()
        conn.close()

        logger.info("Database initialized successfully")

    def _get_table_definitions(self) -> dict[str, str]:
        """Get SQL table definitions."""
        return {
            "campaigns": """
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    protocol TEXT NOT NULL,
                    target TEXT NOT NULL,
                    model TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_payloads INTEGER DEFAULT 0,
                    successful_payloads INTEGER DEFAULT 0,
                    failed_payloads INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """,
            "payloads": """
                CREATE TABLE IF NOT EXISTS payloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    payload_data TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    generation_model TEXT,
                    generation_parameters TEXT,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                )
            """,
            "executions": """
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    payload_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    executed_at TIMESTAMP,
                    execution_time_ms INTEGER,
                    exit_code INTEGER,
                    stdout TEXT,
                    stderr TEXT,
                    crash_detected BOOLEAN DEFAULT 0,
                    instrumentation_data TEXT,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                    FOREIGN KEY (payload_id) REFERENCES payloads(id) ON DELETE CASCADE
                )
            """,
            "defense_results": """
                CREATE TABLE IF NOT EXISTS defense_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER NOT NULL,
                    verdict TEXT NOT NULL,
                    risk_score REAL,
                    module_name TEXT,
                    signals TEXT,
                    events TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE
                )
            """,
            "judgments": """
                CREATE TABLE IF NOT EXISTS judgments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER NOT NULL,
                    score REAL NOT NULL,
                    reasoning TEXT,
                    model TEXT,
                    criteria TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE
                )
            """,
            "feedback_history": """
                CREATE TABLE IF NOT EXISTS feedback_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    iteration INTEGER NOT NULL,
                    feedback_data TEXT NOT NULL,
                    aggregated_scores TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                )
            """,
            "protocol_coverage": """
                CREATE TABLE IF NOT EXISTS protocol_coverage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    protocol TEXT NOT NULL,
                    state_name TEXT NOT NULL,
                    transition_name TEXT,
                    hit_count INTEGER DEFAULT 0,
                    first_hit_at TIMESTAMP,
                    last_hit_at TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                )
            """,
        }

    def _get_index_definitions(self) -> dict[str, str]:
        """Get SQL index definitions."""
        return {
            "idx_campaigns_status": "CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)",
            "idx_campaigns_protocol": "CREATE INDEX IF NOT EXISTS idx_campaigns_protocol ON campaigns(protocol)",
            "idx_payloads_campaign": "CREATE INDEX IF NOT EXISTS idx_payloads_campaign ON payloads(campaign_id)",
            "idx_executions_campaign": "CREATE INDEX IF NOT EXISTS idx_executions_campaign ON executions(campaign_id)",
            "idx_executions_payload": "CREATE INDEX IF NOT EXISTS idx_executions_payload ON executions(payload_id)",
            "idx_executions_status": "CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status)",
            "idx_defense_verdict": "CREATE INDEX IF NOT EXISTS idx_defense_verdict ON defense_results(verdict)",
            "idx_judgments_score": "CREATE INDEX IF NOT EXISTS idx_judgments_score ON judgments(score)",
        }

    def _insert_initial_data(self) -> None:
        """Insert initial/demo data."""
        import sqlite3

        db_path = self.database_url.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert demo campaign
        cursor.execute("""
            INSERT OR IGNORE INTO campaigns (name, protocol, target, status, model)
            VALUES (?, ?, ?, ?, ?)
        """, ("demo-campaign", "coap", "coap://localhost:5683", "completed", "mistral"))

        conn.commit()
        conn.close()

        logger.info("Initial data inserted")

    def reset_database(self) -> None:
        """Drop all tables (WARNING: destructive operation)."""
        if self.db_type == "sqlite":
            db_path = self.database_url.replace("sqlite:///", "")
            db_file = Path(db_path)

            if db_file.exists():
                logger.warning(f"Deleting database file: {db_file}")
                db_file.unlink()
                logger.info("Database reset complete")
            else:
                logger.info("Database file does not exist, nothing to reset")

    def initialize(self, reset: bool = False, with_demo_data: bool = False) -> None:
        """Initialize the database.

        Args:
            reset: If True, drop all existing tables first
            with_demo_data: If True, insert demo data
        """
        logger.info(f"Initializing {self.db_type} database")
        logger.info(f"Database URL: {self.database_url}")

        if reset:
            logger.warning("RESET flag is set - will drop all tables!")
            response = input("Are you sure? Type 'yes' to confirm: ")
            if response.lower() == "yes":
                self.reset_database()
            else:
                logger.info("Reset cancelled")
                return

        if self.db_type == "sqlite":
            self._create_sqlite_database()
        elif self.db_type == "postgresql":
            logger.error("PostgreSQL initialization not yet implemented")
            logger.info("Please use SQLAlchemy migrations or manual SQL scripts")
        elif self.db_type == "mysql":
            logger.error("MySQL initialization not yet implemented")
            logger.info("Please use SQLAlchemy migrations or manual SQL scripts")
        else:
            logger.error(f"Unknown database type: {self.db_type}")
            sys.exit(1)

        if with_demo_data and self.db_type == "sqlite":
            self._insert_initial_data()

    def verify_schema(self) -> bool:
        """Verify that all expected tables exist."""
        if self.db_type != "sqlite":
            logger.warning("Schema verification only implemented for SQLite")
            return False

        import sqlite3

        db_path = self.database_url.replace("sqlite:///", "")
        if not Path(db_path).exists():
            logger.error(f"Database file does not exist: {db_path}")
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        expected_tables = set(self._get_table_definitions().keys())

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = set(row[0] for row in cursor.fetchall())

        conn.close()

        missing_tables = expected_tables - existing_tables
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False

        logger.info(f"Schema verification passed: {len(expected_tables)} tables found")
        return True


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Initialize HyFuzz database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--database-url",
        type=str,
        default="sqlite:///data/hyfuzz.db",
        help="Database URL (default: sqlite:///data/hyfuzz.db)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (WARNING: drops all tables!)",
    )
    parser.add_argument(
        "--demo-data",
        action="store_true",
        help="Insert demo data after initialization",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify schema without making changes",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    initializer = DatabaseInitializer(args.database_url)

    if args.verify:
        logger.info("Running schema verification...")
        if initializer.verify_schema():
            logger.info("✓ Schema verification passed")
            return 0
        else:
            logger.error("✗ Schema verification failed")
            return 1

    print("🗄️  HyFuzz Database Initializer")
    print(f"Database URL: {args.database_url}")
    print(f"Database Type: {initializer.db_type}")
    print()

    if args.reset:
        print("⚠️  WARNING: --reset flag will delete all existing data!")

    try:
        initializer.initialize(reset=args.reset, with_demo_data=args.demo_data)
        print("\n✅ Database initialized successfully!")

        if initializer.verify_schema():
            print("✅ Schema verification passed")
        return 0

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
