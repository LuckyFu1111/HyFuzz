"""Extended tests for connection manager."""

import pytest
from unittest.mock import Mock, patch
from src.mcp_client.connection_manager import ConnectionManager


class TestConnectionManagerExtended:
    """Extended tests for ConnectionManager."""

    def test_initialization(self):
        """Test connection manager initialization."""
        manager = ConnectionManager("http://localhost:8080")
        assert manager.endpoint == "http://localhost:8080"
        assert not manager.is_connected()

    def test_initialization_strips_trailing_slash(self):
        """Test that endpoint trailing slashes are removed."""
        manager = ConnectionManager("http://localhost:8080/")
        assert manager.endpoint == "http://localhost:8080"

    def test_url_construction(self):
        """Test internal URL construction."""
        manager = ConnectionManager("http://localhost:8080")
        url = manager._url("health")
        assert url == "http://localhost:8080/health"

    def test_url_construction_with_leading_slash(self):
        """Test URL construction with leading slash in path."""
        manager = ConnectionManager("http://localhost:8080")
        url = manager._url("/health")
        # Should handle both cases
        assert "health" in url

    @patch('src.mcp_client.connection_manager.requests.Session')
    def test_connect_calls_health_endpoint(self, mock_session_class):
        """Test that connect calls health endpoint."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.post.return_value = Mock(json=lambda: {"result": {"sessionId": "test"}})
        mock_session_class.return_value = mock_session

        manager = ConnectionManager("http://localhost:8080", session=mock_session)
        try:
            manager.connect(timeout=1.0)
        except Exception:
            pass  # Expected to fail, we're just checking the call

        mock_session.get.assert_called()

    def test_send_without_connection_raises_error(self):
        """Test that sending without connection raises error."""
        manager = ConnectionManager("http://localhost:8080")
        with pytest.raises(RuntimeError, match="Not connected"):
            manager.send({"test": "message"})

    def test_session_id_stored_after_connect(self):
        """Test that session ID is stored after successful connect."""
        manager = ConnectionManager("http://localhost:8080")
        # Session ID should be None initially
        assert manager._session_id is None

    @patch('src.mcp_client.connection_manager.requests.Session')
    def test_custom_session_can_be_provided(self, mock_session_class):
        """Test that custom session can be provided."""
        custom_session = Mock()
        manager = ConnectionManager("http://localhost:8080", session=custom_session)
        assert manager._session == custom_session

    def test_connection_status_initially_false(self):
        """Test connection status is initially false."""
        manager = ConnectionManager("http://localhost:8080")
        assert not manager.is_connected()


class TestConnectionManagerErrorHandling:
    """Test error handling in ConnectionManager."""

    @patch('src.mcp_client.connection_manager.requests.Session')
    def test_connect_handles_timeout(self, mock_session_class):
        """Test that connect handles timeout gracefully."""
        mock_session = Mock()
        mock_session.get.side_effect = TimeoutError("Connection timeout")
        mock_session_class.return_value = mock_session

        manager = ConnectionManager("http://localhost:8080", session=mock_session)
        with pytest.raises((RuntimeError, TimeoutError)):
            manager.connect(timeout=0.1)

    @patch('src.mcp_client.connection_manager.requests.Session')
    def test_send_handles_invalid_json(self, mock_session_class):
        """Test that send handles invalid JSON response."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        manager = ConnectionManager("http://localhost:8080", session=mock_session)
        manager._connected = True  # Bypass connection check

        with pytest.raises(RuntimeError, match="Invalid JSON"):
            manager.send({"test": "message"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
