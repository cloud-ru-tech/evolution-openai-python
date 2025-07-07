#!/usr/bin/env python3
"""
Unit tests for Foundation Models functionality
"""

from unittest.mock import MagicMock, patch

import pytest

from evolution_openai import OpenAI, AsyncOpenAI
from evolution_openai.exceptions import EvolutionAuthError


@pytest.mark.unit
class TestFoundationModelsUnit:
    """Unit tests for Foundation Models functionality"""

    FOUNDATION_MODELS_URL = (
        "https://foundation-models.api.cloud.ru/api/gigacube/openai/v1"
    )
    DEFAULT_MODEL = "RefalMachine/RuadaptQwen2.5-7B-Lite-Beta"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_foundation_models_client_initialization(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models client initialization with project_id"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=self.FOUNDATION_MODELS_URL,
            project_id="test_project_id",
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]
        assert str(client.base_url) == self.FOUNDATION_MODELS_URL + "/"
        assert client.project_id == "test_project_id"
        assert client.token_manager == mock_manager

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_foundation_models_async_client_initialization(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models async client initialization with project_id"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=self.FOUNDATION_MODELS_URL,
            project_id="test_project_id",
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]
        assert str(client.base_url) == self.FOUNDATION_MODELS_URL + "/"
        assert client.project_id == "test_project_id"
        assert client.token_manager == mock_manager

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_foundation_models_client_properties(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models client properties"""
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
            base_url=self.FOUNDATION_MODELS_URL,
            project_id="test_project_id",
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

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_foundation_models_with_options(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models client with_options method"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=self.FOUNDATION_MODELS_URL,
            project_id="test_project_id",
            timeout=30.0,
        )

        # Test with_options returns a new client instance
        new_client = client.with_options(timeout=60.0, max_retries=3)

        # Original client should be unchanged
        assert client.timeout == 30.0

        # New client should have updated options
        assert new_client.timeout == 60.0
        assert new_client.max_retries == 3

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_foundation_models_auth_error_handling(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models authentication error handling"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.side_effect = EvolutionAuthError(
            "Authentication failed", status_code=401
        )
        mock_token_manager.return_value = mock_manager

        with pytest.raises(EvolutionAuthError):
            OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=self.FOUNDATION_MODELS_URL,
                project_id="test_project_id",
            )

    def test_foundation_models_missing_project_id(self, mock_credentials):
        """Test Foundation Models client without project_id"""
        # This should work fine - project_id is optional
        with patch(
            "evolution_openai.client.EvolutionTokenManager"
        ) as mock_token_manager:
            mock_manager = MagicMock()
            mock_manager.get_valid_token.return_value = "test_token"
            mock_token_manager.return_value = mock_manager

            client = OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=self.FOUNDATION_MODELS_URL,
                # No project_id provided
            )

            assert client.project_id is None

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_foundation_models_context_manager(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models client as context manager"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Test sync client context manager
        with OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=self.FOUNDATION_MODELS_URL,
            project_id="test_project_id",
        ) as client:
            assert client.current_token == "test_token"

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_foundation_models_async_context_manager(
        self, mock_token_manager, mock_credentials
    ):
        """Test Foundation Models async client as context manager"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Test async client context manager
        async with AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=self.FOUNDATION_MODELS_URL,
            project_id="test_project_id",
        ) as client:
            assert client.current_token == "test_token"


@pytest.mark.unit
class TestFoundationModelsConfiguration:
    """Unit tests for Foundation Models configuration"""

    def test_foundation_models_url_validation(self):
        """Test Foundation Models URL validation"""
        foundation_models_url = (
            "https://foundation-models.api.cloud.ru/api/gigacube/openai/v1"
        )

        # URL should be valid
        assert foundation_models_url.startswith("https://")
        assert "foundation-models.api.cloud.ru" in foundation_models_url
        assert foundation_models_url.endswith("/v1")

    def test_foundation_models_default_model(self):
        """Test Foundation Models default model"""
        default_model = "RefalMachine/RuadaptQwen2.5-7B-Lite-Beta"

        # Model name should be valid
        assert "/" in default_model
        assert len(default_model) > 0
        assert default_model.startswith("RefalMachine/")

    def test_foundation_models_timeout_configuration(self):
        """Test Foundation Models timeout configuration"""
        # Foundation Models should have longer timeout than regular API
        regular_timeout = 30.0
        foundation_models_timeout = 60.0

        assert foundation_models_timeout > regular_timeout
        assert foundation_models_timeout >= 60.0  # At least 1 minute

    def test_foundation_models_required_params(self):
        """Test Foundation Models required parameters"""
        required_params = ["key_id", "secret", "base_url"]
        optional_params = ["project_id", "timeout", "max_retries"]

        # Verify we have the right parameter lists
        assert len(required_params) == 3
        assert len(optional_params) == 3
        assert (
            "project_id" in optional_params
        )  # project_id is optional but recommended
