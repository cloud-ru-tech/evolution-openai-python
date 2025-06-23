"""
Unit tests for EvolutionTokenManager
"""

from datetime import datetime, timedelta

import pytest
import responses

from evolution_openai.exceptions import (
    EvolutionAuthError,
    EvolutionTokenError,
    EvolutionNetworkError,
)
from evolution_openai.token_manager import EvolutionTokenManager


@pytest.mark.unit
class TestEvolutionTokenManager:
    """Test EvolutionTokenManager functionality"""

    def test_init_valid_credentials(self, mock_credentials):
        """Test initialization with valid credentials"""
        manager = EvolutionTokenManager(
            mock_credentials["key_id"], mock_credentials["secret"]
        )
        assert manager.key_id == mock_credentials["key_id"]
        assert manager.secret == mock_credentials["secret"]
        assert manager.access_token is None
        assert manager.token_expires_at is None

    def test_init_empty_credentials(self):
        """Test initialization with empty credentials raises error"""
        with pytest.raises(EvolutionTokenError):
            EvolutionTokenManager("", "test_secret")

        with pytest.raises(EvolutionTokenError):
            EvolutionTokenManager("test_key", "")

    @responses.activate
    def test_successful_token_request(self, mock_credentials):
        """Test successful token request"""
        # Mock successful response
        responses.add(
            responses.POST,
            mock_credentials["token_url"],
            json={"access_token": "test_token_123", "expires_in": 3600},
            status=200,
        )

        manager = EvolutionTokenManager(
            mock_credentials["key_id"],
            mock_credentials["secret"],
            token_url=mock_credentials["token_url"],
        )
        token = manager.get_valid_token()

        assert token == "test_token_123"
        assert manager.access_token == "test_token_123"
        assert manager.token_expires_at is not None

    @responses.activate
    def test_token_request_401_error(self, mock_credentials):
        """Test 401 authentication error"""
        responses.add(
            responses.POST,
            mock_credentials["token_url"],
            json={"error": "Unauthorized"},
            status=401,
        )

        manager = EvolutionTokenManager(
            "wrong_key",
            "wrong_secret",
            token_url=mock_credentials["token_url"],
        )

        with pytest.raises(EvolutionAuthError) as exc_info:
            manager.get_valid_token()

        assert exc_info.value.status_code == 401

    @responses.activate
    def test_token_request_network_error(self, mock_credentials):
        """Test network error handling"""
        responses.add(
            responses.POST,
            mock_credentials["token_url"],
            json={"error": "Network error"},
            status=500,
        )

        manager = EvolutionTokenManager(
            mock_credentials["key_id"],
            mock_credentials["secret"],
            token_url=mock_credentials["token_url"],
        )

        with pytest.raises(EvolutionNetworkError):
            manager.get_valid_token()

    @responses.activate
    def test_token_refresh_logic(self, mock_credentials):
        """Test token refresh logic"""
        # First request
        responses.add(
            responses.POST,
            mock_credentials["token_url"],
            json={"access_token": "token_1", "expires_in": 3600},
            status=200,
        )

        # Second request
        responses.add(
            responses.POST,
            mock_credentials["token_url"],
            json={"access_token": "token_2", "expires_in": 3600},
            status=200,
        )

        manager = EvolutionTokenManager(
            mock_credentials["key_id"],
            mock_credentials["secret"],
            token_url=mock_credentials["token_url"],
            buffer_seconds=0,
        )

        # Get first token
        token1 = manager.get_valid_token()
        assert token1 == "token_1"

        # Simulate token expiration
        manager.token_expires_at = datetime.now() - timedelta(seconds=1)

        # Get refreshed token
        token2 = manager.get_valid_token()
        assert token2 == "token_2"

    def test_is_token_valid(self, mock_credentials):
        """Test token validity check"""
        manager = EvolutionTokenManager(
            mock_credentials["key_id"], mock_credentials["secret"]
        )

        # No token
        assert not manager.is_token_valid()

        # Valid token
        manager.access_token = "test_token"
        manager.token_expires_at = datetime.now() + timedelta(hours=1)
        assert manager.is_token_valid()

        # Expired token
        manager.token_expires_at = datetime.now() - timedelta(seconds=1)
        assert not manager.is_token_valid()

    def test_invalidate_token(self, mock_credentials):
        """Test token invalidation"""
        manager = EvolutionTokenManager(
            mock_credentials["key_id"], mock_credentials["secret"]
        )
        manager.access_token = "test_token"
        manager.token_expires_at = datetime.now() + timedelta(hours=1)

        manager.invalidate_token()

        assert manager.access_token is None
        assert manager.token_expires_at is None

    def test_get_token_info(self, mock_credentials):
        """Test token info retrieval"""
        manager = EvolutionTokenManager(
            mock_credentials["key_id"], mock_credentials["secret"]
        )

        # No token
        info = manager.get_token_info()
        assert info["has_token"] is False
        assert info["expires_at"] is None
        assert info["is_valid"] is False

        # With token
        expires_at = datetime.now() + timedelta(hours=1)
        manager.access_token = "test_token"
        manager.token_expires_at = expires_at

        info = manager.get_token_info()
        assert info["has_token"] is True
        assert info["expires_at"] == expires_at.isoformat()
        assert info["is_valid"] is True


@pytest.mark.unit
class TestEvolutionTokenManagerWithEnv:
    """Test TokenManager with environment variables"""

    def test_custom_token_url(self, test_credentials):
        """Test using custom token URL from environment"""
        if test_credentials["token_url"]:
            manager = EvolutionTokenManager(
                "test_key",
                "test_secret",
                token_url=test_credentials["token_url"],
            )
            assert manager.token_url == test_credentials["token_url"]

    def test_buffer_seconds_configuration(self):
        """Test buffer seconds configuration"""
        manager = EvolutionTokenManager(
            "test_key", "test_secret", buffer_seconds=60
        )
        assert manager.buffer_seconds == 60

        info = manager.get_token_info()
        assert info["buffer_seconds"] == 60
