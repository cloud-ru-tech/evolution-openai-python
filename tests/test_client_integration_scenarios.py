"""
Integration scenario tests for Evolution OpenAI Client
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from evolution_openai import OpenAI, AsyncOpenAI
from evolution_openai.exceptions import EvolutionAuthError


@pytest.mark.unit
class TestOpenAIVersionCompatibility:
    """Test compatibility with different OpenAI SDK versions"""

    def test_openai_version_check_success(self, mock_credentials):
        """Test successful OpenAI version check"""
        with patch("evolution_openai.client.openai") as mock_openai:
            mock_openai.__version__ = "1.30.0"

            with patch(
                "evolution_openai.client.EvolutionTokenManager"
            ) as mock_token_manager:
                mock_manager = MagicMock()
                mock_manager.get_valid_token.return_value = "test_token"
                mock_token_manager.return_value = mock_manager

                # Should not raise an error
                client = OpenAI(
                    key_id=mock_credentials["key_id"],
                    secret=mock_credentials["secret"],
                    base_url=mock_credentials["base_url"],
                )
                assert client is not None

    def test_openai_version_check_malformed_version(self, mock_credentials):
        """Test OpenAI version check with malformed version string"""
        with patch("evolution_openai.client.openai") as mock_openai:
            mock_openai.__version__ = "1.30"  # Missing patch version

            with patch(
                "evolution_openai.client.EvolutionTokenManager"
            ) as mock_token_manager:
                mock_manager = MagicMock()
                mock_manager.get_valid_token.return_value = "test_token"
                mock_token_manager.return_value = mock_manager

                # Should still work as we check if len(version_parts) > 1
                client = OpenAI(
                    key_id=mock_credentials["key_id"],
                    secret=mock_credentials["secret"],
                    base_url=mock_credentials["base_url"],
                )
                assert client is not None

    def test_openai_not_available_fallback(self, mock_credentials):
        """Test behavior when OpenAI is not available"""
        with patch("evolution_openai.client.OPENAI_AVAILABLE", False):
            with pytest.raises(ImportError) as exc_info:
                OpenAI(
                    key_id=mock_credentials["key_id"],
                    secret=mock_credentials["secret"],
                    base_url=mock_credentials["base_url"],
                )

            assert "OpenAI SDK required" in str(exc_info.value)

    def test_supports_project_flag(self, mock_credentials):
        """Test SUPPORTS_PROJECT flag behavior"""
        with patch("evolution_openai.client.SUPPORTS_PROJECT", True):
            with patch(
                "evolution_openai.client.EvolutionTokenManager"
            ) as mock_token_manager:
                mock_manager = MagicMock()
                mock_manager.get_valid_token.return_value = "test_token"
                mock_token_manager.return_value = mock_manager

                client = OpenAI(
                    key_id=mock_credentials["key_id"],
                    secret=mock_credentials["secret"],
                    base_url=mock_credentials["base_url"],
                    project_id="test_project",
                )

                assert client.project_id == "test_project"


@pytest.mark.unit
class TestClientParameterHandling:
    """Test client parameter handling scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_ignores_api_key_parameter(
        self, mock_token_manager, mock_credentials
    ):
        """Test that client ignores the api_key parameter"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            api_key="should_be_ignored",
        )

        # Should use token from token manager, not the provided api_key
        assert client.current_token == "test_token"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_with_all_openai_parameters(
        self, mock_token_manager, mock_credentials
    ):
        """Test client with all possible OpenAI parameters"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            api_key="ignored",
            organization="test_org",
            project_id="test_project",
            timeout=45.0,
            max_retries=3,
            default_headers={"X-Custom": "test"},
            default_query={"param": "value"},
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]
        assert client.project_id == "test_project"
        assert client.timeout == 45.0
        assert client.max_retries == 3

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_client_with_all_parameters(
        self, mock_token_manager, mock_credentials
    ):
        """Test async client with all possible parameters"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            api_key="ignored",
            organization="test_org",
            project_id="test_project",
            timeout=45.0,
            max_retries=3,
            default_headers={"X-Custom": "test"},
            default_query={"param": "value"},
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]
        assert client.project_id == "test_project"
        assert client.timeout == 45.0
        assert client.max_retries == 3


@pytest.mark.unit
class TestTokenRefreshScenarios:
    """Test various token refresh scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_token_refresh_on_client_creation(
        self, mock_token_manager, mock_credentials
    ):
        """Test token refresh behavior during client creation"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "initial_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Should call get_valid_token during initialization
        assert mock_manager.get_valid_token.called
        assert client.current_token == "initial_token"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_multiple_token_refresh_calls(
        self, mock_token_manager, mock_credentials
    ):
        """Test multiple token refresh calls"""
        mock_manager = MagicMock()
        # Provide tokens: initial creation, then 2 refresh calls + token access checks
        mock_manager.get_valid_token.side_effect = [
            "token1",
            "token2",
            "token3",
            "token4",
            "token5",
        ]
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # First refresh
        token1 = client.refresh_token()
        assert token1 == "token3"  # Updated based on side_effect sequence

        # Second refresh
        token2 = client.refresh_token()
        assert token2 == "token4"  # Updated based on side_effect sequence

        # Should have called invalidate_token twice
        assert mock_manager.invalidate_token.call_count == 2

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_token_info_retrieval(self, mock_token_manager, mock_credentials):
        """Test token info retrieval"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_manager.get_token_info.return_value = {
            "token": "test_token",
            "expires_at": 1234567890,
            "is_valid": True,
        }
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        info = client.get_token_info()
        assert info["token"] == "test_token"
        assert info["expires_at"] == 1234567890
        assert info["is_valid"] is True

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_token_manager_exception_handling(
        self, mock_token_manager, mock_credentials
    ):
        """Test token manager exception handling"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.side_effect = EvolutionAuthError(
            "Token error"
        )
        mock_token_manager.return_value = mock_manager

        with pytest.raises(EvolutionAuthError):
            OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )


@pytest.mark.unit
class TestHeaderInjectionScenarios:
    """Test header injection scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_project_id_header_injection_sync(
        self, mock_token_manager, mock_credentials
    ):
        """Test project_id header injection in sync client"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id="test_project_123",
        )

        # Mock HTTP client to test header injection
        mock_http_client = MagicMock()
        mock_http_client._auth_headers = {}
        mock_http_client.default_headers = {}
        mock_http_client._default_headers = {}
        client._client = mock_http_client

        # Update headers
        client._update_auth_headers("new_token")

        # Check that project_id header was added to all sources
        assert (
            mock_http_client._auth_headers.get("x-project-id")
            == "test_project_123"
        )
        assert (
            mock_http_client.default_headers.get("x-project-id")
            == "test_project_123"
        )
        assert (
            mock_http_client._default_headers.get("x-project-id")
            == "test_project_123"
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_project_id_header_injection_async(
        self, mock_token_manager, mock_credentials
    ):
        """Test project_id header injection in async client"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id="test_project_async",
        )

        # Mock HTTP client to test header injection
        mock_http_client = MagicMock()
        mock_http_client._auth_headers = {}
        mock_http_client.default_headers = {}
        mock_http_client._default_headers = {}
        client._client = mock_http_client

        # Update headers
        client._update_auth_headers("new_token")

        # Check that project_id header was added to all sources
        assert (
            mock_http_client._auth_headers.get("x-project-id")
            == "test_project_async"
        )
        assert (
            mock_http_client.default_headers.get("x-project-id")
            == "test_project_async"
        )
        assert (
            mock_http_client._default_headers.get("x-project-id")
            == "test_project_async"
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_custom_headers_preservation(
        self, mock_token_manager, mock_credentials
    ):
        """Test that custom headers are preserved"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        custom_headers = {
            "X-Custom-Header": "custom_value",
            "User-Agent": "custom-agent",
        }

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            default_headers=custom_headers,
        )

        # Headers should be preserved
        assert client.default_headers["X-Custom-Header"] == "custom_value"
        assert client.default_headers["User-Agent"] == "custom-agent"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_headers_with_none_project_id(
        self, mock_token_manager, mock_credentials
    ):
        """Test header handling when project_id is None"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id=None,
        )

        # Mock HTTP client
        mock_http_client = MagicMock()
        mock_http_client._auth_headers = {}
        client._client = mock_http_client

        # Update headers
        client._update_auth_headers("new_token")

        # Should not add project_id header when it's None
        assert "x-project-id" not in mock_http_client._auth_headers


@pytest.mark.unit
class TestRequestInterceptionScenarios:
    """Test request interception and modification scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_request_interception_token_update(
        self, mock_token_manager, mock_credentials
    ):
        """Test that requests are intercepted and tokens are updated"""
        mock_manager = MagicMock()
        # Provide tokens: initial creation, initialization, patching, request
        mock_manager.get_valid_token.side_effect = [
            "token1",
            "token2",
            "token3",
            "token4",
        ]
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client
        mock_http_client = MagicMock()
        original_request = MagicMock()
        original_request.return_value = "success"
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Make a request
        result = mock_http_client.request("test_arg")

        # Verify token was updated before request
        assert (
            client.api_key == "token3"
        )  # Updated based on side_effect sequence
        assert result == "success"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_request_interception_auth_error_recovery(
        self, mock_token_manager, mock_credentials
    ):
        """Test authentication error recovery during request"""
        mock_manager = MagicMock()
        # Provide tokens: initial creation, initialization, first request, invalidate/retry
        mock_manager.get_valid_token.side_effect = [
            "token1",
            "token2",
            "token3",
            "token4",
            "token5",
        ]
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client
        mock_http_client = MagicMock()
        original_request = MagicMock()
        # First call fails with auth error, second succeeds
        original_request.side_effect = [
            Exception("401 Unauthorized"),
            "success",
        ]
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Make a request
        result = mock_http_client.request("test_arg")

        # Verify recovery logic
        assert result == "success"
        assert original_request.call_count == 2
        mock_manager.invalidate_token.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_request_interception_token_update(
        self, mock_token_manager, mock_credentials
    ):
        """Test that async requests are intercepted and tokens are updated"""
        mock_manager = MagicMock()
        # Provide tokens: initial creation, initialization, patching, request
        mock_manager.get_valid_token.side_effect = [
            "token1",
            "token2",
            "token3",
            "token4",
        ]
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock async HTTP client
        mock_http_client = MagicMock()
        original_request = AsyncMock()
        original_request.return_value = "async_success"
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_async_client()

        # Make an async request
        result = await mock_http_client.request("async_test_arg")

        # Verify token was updated before request
        assert (
            client.api_key == "token3"
        )  # Updated based on side_effect sequence
        assert result == "async_success"


@pytest.mark.unit
class TestClientStateManagement:
    """Test client state management scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_credentials_immutability(
        self, mock_token_manager, mock_credentials
    ):
        """Test that client credentials remain immutable"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Credentials should remain unchanged
        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]

        # Even after token refresh
        client.refresh_token()
        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]


@pytest.mark.unit
class TestErrorPropagation:
    """Test error propagation scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_non_auth_error_propagation(
        self, mock_token_manager, mock_credentials
    ):
        """Test that non-auth errors are propagated correctly"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client
        mock_http_client = MagicMock()
        original_request = MagicMock()
        original_request.side_effect = ValueError("Test error")
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Should propagate the ValueError
        with pytest.raises(ValueError) as exc_info:
            mock_http_client.request("test_arg")

        assert "Test error" in str(exc_info.value)

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_token_manager_error_propagation(
        self, mock_token_manager, mock_credentials
    ):
        """Test that token manager errors are propagated correctly"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.side_effect = Exception(
            "Token manager error"
        )
        mock_token_manager.return_value = mock_manager

        with pytest.raises(Exception) as exc_info:
            OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )

        assert "Token manager error" in str(exc_info.value)

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_error_propagation(
        self, mock_token_manager, mock_credentials
    ):
        """Test that async errors are propagated correctly"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock async HTTP client
        mock_http_client = MagicMock()
        original_request = MagicMock()
        original_request.side_effect = RuntimeError("Async error")
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_async_client()

        # Should propagate the RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            await mock_http_client.request("async_test_arg")

        assert "Async error" in str(exc_info.value)
