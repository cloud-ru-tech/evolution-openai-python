"""
Unit tests for Evolution OpenAI Clients
"""

from unittest.mock import MagicMock, patch

import pytest

from evolution_openai import (
    OpenAI,
    AsyncOpenAI,
    create_client,
    create_async_client,
)
from evolution_openai.exceptions import EvolutionAuthError


@pytest.mark.unit
class TestEvolutionOpenAI:
    """Test Evolution OpenAI client"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_initialization(self, mock_token_manager, mock_credentials):
        """Test client initialization"""
        # Mock token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]
        assert client.token_manager == mock_manager

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_properties(self, mock_token_manager, mock_credentials):
        """Test client properties"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_manager.get_token_info.return_value = {
            "has_token": True,
            "is_valid": True,
        }
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Test current_token property
        assert client.current_token == "test_token"

        # Test get_token_info method
        info = client.get_token_info()
        assert info["has_token"] is True
        assert info["is_valid"] is True

        # Test refresh_token method
        mock_manager.invalidate_token = MagicMock()
        mock_manager.get_valid_token.return_value = "new_token"

        new_token = client.refresh_token()
        assert new_token == "new_token"
        mock_manager.invalidate_token.assert_called_once()


@pytest.mark.unit
class TestEvolutionAsyncOpenAI:
    """Test Evolution Async OpenAI client"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_client_initialization(
        self, mock_token_manager, mock_credentials
    ):
        """Test async client initialization"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]
        assert client.token_manager == mock_manager


@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions"""

    @patch("evolution_openai.client.EvolutionOpenAI")
    def test_create_client(self, mock_openai_class, mock_credentials):
        """Test create_client helper function"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = create_client(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            timeout=30.0,
        )

        mock_openai_class.assert_called_once_with(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            timeout=30.0,
        )
        assert client == mock_client

    @patch("evolution_openai.client.EvolutionAsyncOpenAI")
    def test_create_async_client(self, mock_async_class, mock_credentials):
        """Test create_async_client helper function"""
        mock_client = MagicMock()
        mock_async_class.return_value = mock_client

        client = create_async_client(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            max_retries=5,
        )

        mock_async_class.assert_called_once_with(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            max_retries=5,
        )
        assert client == mock_client


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in clients"""

    def test_missing_openai_dependency(self, mock_credentials):
        """Test behavior when OpenAI SDK is not installed"""
        with patch("evolution_openai.client.OPENAI_AVAILABLE", False):
            with pytest.raises(ImportError) as exc_info:
                OpenAI(
                    key_id=mock_credentials["key_id"],
                    secret=mock_credentials["secret"],
                    base_url=mock_credentials["base_url"],
                )

            assert "OpenAI SDK required" in str(exc_info.value)

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_auth_error_handling(self, mock_token_manager, mock_credentials):
        """Test authentication error handling"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.side_effect = EvolutionAuthError(
            "Authentication failed", status_code=401
        )
        mock_token_manager.return_value = mock_manager

        with pytest.raises(EvolutionAuthError):
            OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )
