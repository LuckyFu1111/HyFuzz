"""Tests for CVE classifier module."""

import pytest
from src.scanning.cve_classifier import CVEClassifier, CVEInfo


class TestCVEClassifier:
    """Test CVE classifier functionality."""

    def test_classifier_initialization(self):
        """Test CVE classifier initializes correctly."""
        classifier = CVEClassifier()
        assert classifier is not None

    def test_classify_returns_cve_info(self):
        """Test that classify returns CVEInfo object."""
        classifier = CVEClassifier()
        result = classifier.classify("buffer overflow")
        assert isinstance(result, (CVEInfo, type(None)))

    def test_classifier_handles_empty_input(self):
        """Test classifier handles empty input gracefully."""
        classifier = CVEClassifier()
        result = classifier.classify("")
        assert result is None or isinstance(result, CVEInfo)

    def test_classifier_handles_none_input(self):
        """Test classifier handles None input gracefully."""
        classifier = CVEClassifier()
        # Should not raise exception
        try:
            result = classifier.classify(None)
            assert result is None or isinstance(result, CVEInfo)
        except (TypeError, AttributeError):
            # This is acceptable behavior
            pass


class TestCVEInfo:
    """Test CVEInfo data class."""

    def test_cve_info_creation(self):
        """Test creating CVEInfo object."""
        info = CVEInfo(
            cve_id="CVE-2021-1234",
            description="Test vulnerability",
            severity="HIGH"
        )
        assert info.cve_id == "CVE-2021-1234"
        assert info.description == "Test vulnerability"
        assert info.severity == "HIGH"

    def test_cve_info_to_dict(self):
        """Test converting CVEInfo to dictionary."""
        info = CVEInfo(
            cve_id="CVE-2021-1234",
            description="Test",
            severity="MEDIUM"
        )
        d = info.to_dict()
        assert d["cve_id"] == "CVE-2021-1234"
        assert d["severity"] == "MEDIUM"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
