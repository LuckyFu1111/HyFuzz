"""
Database Fuzzing Tests for Ubuntu Client

Fuzzing tests for the simple SQLite database helper used in the Ubuntu client.
Tests SQL injection resistance, parameter fuzzing, and error handling.

Test Coverage:
- SQL injection attack patterns
- Query parameter fuzzing
- Data type fuzzing
- Concurrent access testing
- Special character handling
- Boundary value testing
"""

import pytest
import sqlite3
import tempfile
import os
import random
import string
from pathlib import Path
from typing import Any, List, Tuple

# Import database module
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from storage.database import execute


# ============================================================================
# Fuzzing Utilities
# ============================================================================

class SQLInjectionPatterns:
    """SQL injection attack patterns"""

    @staticmethod
    def get_patterns() -> List[str]:
        """Get SQL injection patterns"""
        return [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "'; DROP TABLE kv--",
            "' UNION SELECT * FROM kv--",
            "admin' --",
            "' OR 1=1#",
            "1' ORDER BY 1--",
            "' AND 1=0 UNION ALL SELECT NULL--",
        ]


class FuzzData:
    """Generate fuzzed data"""

    @staticmethod
    def boundary_values() -> List[Any]:
        """Boundary test values"""
        return [
            "",
            " ",
            "A" * 1000,
            "A" * 10000,
            None,
            0,
            -1,
            2**31 - 1,
            2**63 - 1,
        ]

    @staticmethod
    def special_characters() -> List[str]:
        """Special characters"""
        return [
            "'", '"', "`", ";", "--", "/*", "*/", "#", "\\",
            "%", "_", "\x00", "\n", "\r", "\t",
        ]

    @staticmethod
    def unicode_strings() -> List[str]:
        """Unicode test strings"""
        return [
            "Hello 世界",
            "Привет мир",
            "🔥💻🐛",
            "Test\u0000Data",
            "\uFEFF",
        ]


# ============================================================================
# Database Fuzzing Tests
# ============================================================================

class TestDatabaseExecuteFuzzing:
    """Test database execute function with fuzzed inputs"""

    @pytest.fixture
    def temp_db(self, monkeypatch, tmp_path):
        """Create temporary database for testing"""
        db_file = tmp_path / "test.db"

        # Patch the database path
        import storage.database as db_module
        monkeypatch.setattr(db_module, '_DB_PATH', db_file)

        # Initialize test table
        execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")

        yield db_file

        # Cleanup
        if db_file.exists():
            db_file.unlink()

    def test_fuzz_sql_injection_in_key(self, temp_db):
        """Test SQL injection attempts in key parameter"""
        for pattern in SQLInjectionPatterns.get_patterns():
            try:
                # Insert with injection pattern
                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (pattern, "test_value")
                )

                # Verify data was inserted correctly (not executed as SQL)
                results = execute("SELECT value FROM kv WHERE key = ?", (pattern,))

                if results:
                    assert results[0][0] == "test_value"

                # Cleanup
                execute("DELETE FROM kv WHERE key = ?", (pattern,))

            except sqlite3.Error as e:
                # Parameterized queries should prevent injection
                # Any error should be a legitimate SQL error, not injection
                assert "DROP" not in str(e).upper()

    def test_fuzz_sql_injection_in_value(self, temp_db):
        """Test SQL injection attempts in value parameter"""
        for i, pattern in enumerate(SQLInjectionPatterns.get_patterns()):
            try:
                key = f"test_key_{i}"

                # Insert with injection pattern in value
                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (key, pattern)
                )

                # Verify value was stored correctly
                results = execute("SELECT value FROM kv WHERE key = ?", (key,))

                if results:
                    # The injection pattern should be stored as plain text
                    assert results[0][0] == pattern

                # Cleanup
                execute("DELETE FROM kv WHERE key = ?", (key,))

            except sqlite3.Error:
                # Should handle gracefully
                pass

    def test_fuzz_boundary_values(self, temp_db):
        """Test boundary values in database operations"""
        for i, value in enumerate(FuzzData.boundary_values()):
            try:
                key = f"boundary_test_{i}"

                # Convert non-string values to string
                value_str = str(value) if value is not None else ""

                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (key, value_str)
                )

                # Retrieve and verify
                results = execute("SELECT value FROM kv WHERE key = ?", (key,))

                if results:
                    assert results[0][0] == value_str

            except (sqlite3.Error, TypeError):
                # Some boundary values might cause errors
                pass

    def test_fuzz_special_characters(self, temp_db):
        """Test special characters in database"""
        for i, char in enumerate(FuzzData.special_characters()):
            try:
                key = f"special_{i}"

                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (key, char)
                )

                # Verify special character was stored correctly
                results = execute("SELECT value FROM kv WHERE key = ?", (key,))

                if results:
                    assert results[0][0] == char

            except sqlite3.Error:
                # Some special characters might cause issues
                pass

    def test_fuzz_unicode_strings(self, temp_db):
        """Test Unicode string handling"""
        for i, unicode_str in enumerate(FuzzData.unicode_strings()):
            try:
                key = f"unicode_{i}"

                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (key, unicode_str)
                )

                # Retrieve and verify
                results = execute("SELECT value FROM kv WHERE key = ?", (key,))

                if results:
                    assert results[0][0] == unicode_str

            except (sqlite3.Error, UnicodeError):
                # Some Unicode might not be supported
                pass

    def test_fuzz_empty_and_null_params(self, temp_db):
        """Test empty and null parameters"""
        test_cases = [
            (None, "value"),  # Null key
            ("key", None),  # Null value
            ("", "value"),  # Empty key
            ("key", ""),  # Empty value
            ("", ""),  # Both empty
        ]

        for key, value in test_cases:
            try:
                # Convert None to empty string
                key_str = str(key) if key is not None else ""
                value_str = str(value) if value is not None else ""

                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (key_str, value_str)
                )

                # Verify
                results = execute("SELECT value FROM kv WHERE key = ?", (key_str,))

                if results:
                    assert results[0][0] == value_str

            except (sqlite3.Error, TypeError):
                # Null/empty values might cause errors
                pass

    def test_fuzz_malformed_queries(self, temp_db):
        """Test malformed SQL queries"""
        malformed_queries = [
            "",  # Empty query
            "SELECT",  # Incomplete
            "SELECT * FROM",  # Incomplete
            "INVALID SQL",  # Invalid syntax
            "SELECT * FROM kv WHERE",  # Incomplete WHERE
            "INSERT INTO",  # Incomplete INSERT
        ]

        for query in malformed_queries:
            try:
                execute(query)
                # Should raise error for malformed queries
                pytest.fail(f"Malformed query should raise error: {query}")
            except sqlite3.Error:
                # Expected - malformed queries should raise errors
                pass

    def test_fuzz_excessive_parameters(self, temp_db):
        """Test queries with excessive parameters"""
        try:
            # Too many parameters
            execute(
                "INSERT INTO kv(key, value) VALUES(?, ?)",
                ("key", "value", "extra", "params")
            )
            # Should either succeed (ignore extra) or raise error
        except sqlite3.Error:
            # Expected behavior
            pass

        try:
            # Too few parameters
            execute(
                "INSERT INTO kv(key, value) VALUES(?, ?)",
                ("only_one",)
            )
            pytest.fail("Should raise error for missing parameters")
        except (sqlite3.Error, TypeError):
            # Expected - should raise error
            pass

    def test_fuzz_concurrent_access(self, temp_db):
        """Test concurrent database access"""
        import threading

        def insert_data(thread_id: int):
            try:
                for i in range(10):
                    execute(
                        "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                        (f"thread_{thread_id}_key_{i}", f"value_{i}")
                    )
            except sqlite3.Error:
                # Concurrent access might cause locking errors
                pass

        # Create multiple threads
        threads = [
            threading.Thread(target=insert_data, args=(i,))
            for i in range(5)
        ]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify database is still functional
        results = execute("SELECT COUNT(*) FROM kv")
        assert len(results) > 0

    def test_fuzz_large_data(self, temp_db):
        """Test handling of large data"""
        sizes = [1000, 10000, 100000]

        for size in sizes[:2]:  # Limit to avoid slowness
            try:
                large_value = "A" * size
                execute(
                    "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                    (f"large_{size}", large_value)
                )

                # Verify storage
                results = execute("SELECT value FROM kv WHERE key = ?", (f"large_{size}",))

                if results:
                    assert len(results[0][0]) == size

                # Cleanup
                execute("DELETE FROM kv WHERE key = ?", (f"large_{size}",))

            except (sqlite3.Error, MemoryError):
                # Large data might exceed limits
                pass

    def test_fuzz_query_result_handling(self, temp_db):
        """Test handling of query results"""
        # Insert test data
        for i in range(10):
            execute(
                "INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)",
                (f"result_test_{i}", f"value_{i}")
            )

        # Test different SELECT scenarios
        test_queries = [
            "SELECT * FROM kv",  # All rows
            "SELECT * FROM kv LIMIT 5",  # Limited rows
            "SELECT * FROM kv WHERE key = 'nonexistent'",  # No results
            "SELECT COUNT(*) FROM kv",  # Aggregate
        ]

        for query in test_queries:
            try:
                results = execute(query)
                # Should return list of tuples
                assert isinstance(results, list)
                for row in results:
                    assert isinstance(row, tuple)
            except sqlite3.Error:
                pass


# ============================================================================
# Error Handling Fuzzing Tests
# ============================================================================

class TestErrorHandlingFuzzing:
    """Test error handling with fuzzed inputs"""

    @pytest.fixture
    def temp_db(self, monkeypatch, tmp_path):
        """Create temporary database for testing"""
        db_file = tmp_path / "test_error.db"

        # Patch the database path
        import storage.database as db_module
        monkeypatch.setattr(db_module, '_DB_PATH', db_file)

        yield db_file

        if db_file.exists():
            db_file.unlink()

    def test_database_not_initialized(self, temp_db):
        """Test operations on uninitialized database"""
        try:
            # Try to query non-existent table
            execute("SELECT * FROM nonexistent_table")
            pytest.fail("Should raise error for non-existent table")
        except sqlite3.Error:
            # Expected
            pass

    def test_invalid_sql_syntax(self, temp_db):
        """Test completely invalid SQL syntax"""
        invalid_queries = [
            "INVALID QUERY",
            "DELETE FROM WHERE",
            "UPDATE SET",
            "CREATE TABLE",
            "DROP",
        ]

        for query in invalid_queries:
            try:
                execute(query)
                pytest.fail(f"Invalid query should raise error: {query}")
            except sqlite3.Error:
                # Expected
                pass

    def test_type_errors_in_params(self, temp_db):
        """Test type errors in parameters"""
        # Create table
        execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")

        invalid_params = [
            ({"dict": "object"}, "value"),  # Dict as key
            ("key", ["list", "value"]),  # List as value
            (lambda x: x, "value"),  # Function as key
        ]

        for params in invalid_params:
            try:
                execute(
                    "INSERT INTO kv(key, value) VALUES(?, ?)",
                    params
                )
                # Might succeed with string conversion
            except (sqlite3.Error, TypeError):
                # Expected for invalid types
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
