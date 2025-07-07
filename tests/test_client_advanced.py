"""
Advanced unit tests for Evolution OpenAI Client internal methods
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from evolution_openai import OpenAI, AsyncOpenAI


@pytest.mark.unit
class TestHeaderManagement:
    """Test header management functionality"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_prepare_default_headers_with_project_id(
        self, mock_token_manager, mock_credentials
    ):
        """Test _prepare_default_headers with project_id"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id="test_project_123",
            default_headers={"Custom-Header": "custom_value"},
        )

        assert client.project_id == "test_project_123"
        # Check that headers are properly prepared
        headers = client._prepare_default_headers(
            {"User-Header": "user_value"}
        )
        assert headers["User-Header"] == "user_value"
        assert headers["x-project-id"] == "test_project_123"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_prepare_default_headers_without_project_id(
        self, mock_token_manager, mock_credentials
    ):
        """Test _prepare_default_headers without project_id"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        headers = client._prepare_default_headers(
            {"User-Header": "user_value"}
        )
        assert headers["User-Header"] == "user_value"
        assert "x-project-id" not in headers

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_update_auth_headers_multiple_sources(
        self, mock_token_manager, mock_credentials
    ):
        """Test _update_auth_headers updates all possible header sources"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id="test_project",
        )

        # Mock various header sources
        mock_http_client = MagicMock()
        mock_http_client._auth_headers = {}
        mock_http_client.default_headers = {}
        mock_http_client._default_headers = {}
        client._client = mock_http_client

        # Update headers
        client._update_auth_headers("new_token")

        # Verify HTTP client sources were updated
        assert (
            mock_http_client._auth_headers["Authorization"]
            == "Bearer new_token"
        )
        assert mock_http_client._auth_headers["x-project-id"] == "test_project"
        assert (
            mock_http_client.default_headers["Authorization"]
            == "Bearer new_token"
        )
        assert (
            mock_http_client.default_headers["x-project-id"] == "test_project"
        )
        assert (
            mock_http_client._default_headers["Authorization"]
            == "Bearer new_token"
        )
        assert (
            mock_http_client._default_headers["x-project-id"] == "test_project"
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_update_auth_headers_no_header_sources(
        self, mock_token_manager, mock_credentials
    ):
        """Test _update_auth_headers when no header sources are available"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client with no header attributes
        mock_http_client = MagicMock()
        # Remove any header attributes
        for attr in ["_auth_headers", "default_headers", "_default_headers"]:
            if hasattr(mock_http_client, attr):
                delattr(mock_http_client, attr)
        client._client = mock_http_client

        # Should not raise an error, just log a warning
        client._update_auth_headers("new_token")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_get_request_headers(self, mock_token_manager, mock_credentials):
        """Test get_request_headers method"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client with various header sources
        mock_http_client = MagicMock()
        mock_http_client._auth_headers = {"Authorization": "Bearer test_token"}
        mock_http_client.default_headers = {"User-Agent": "test-agent"}
        mock_http_client._default_headers = {
            "Content-Type": "application/json"
        }
        client._client = mock_http_client

        headers = client.get_request_headers()

        # Should contain headers from all sources
        assert headers["Authorization"] == "Bearer test_token"
        # User-Agent is set by OpenAI client itself, so don't check specific value
        assert "User-Agent" in headers
        assert headers["Content-Type"] == "application/json"


@pytest.mark.unit
class TestAuthErrorDetection:
    """Test authentication error detection"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_is_auth_error_detection(
        self, mock_token_manager, mock_credentials
    ):
        """Test _is_auth_error method with various error types"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Test various auth error scenarios
        auth_errors = [
            Exception("401 Unauthorized"),
            Exception("Authentication failed"),
            Exception("403 Forbidden"),
            Exception("UNAUTHORIZED access"),
            Exception("Authentication error occurred"),
        ]

        for error in auth_errors:
            assert client._is_auth_error(error) is True

        # Test non-auth errors
        non_auth_errors = [
            Exception("500 Internal Server Error"),
            Exception("Rate limit exceeded"),
            Exception("Network timeout"),
            Exception("Bad Request"),
        ]

        for error in non_auth_errors:
            assert client._is_auth_error(error) is False


@pytest.mark.unit
class TestHTTPClientPatching:
    """Test HTTP client patching functionality"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_patch_client_with_request_method(
        self, mock_token_manager, mock_credentials
    ):
        """Test _patch_client when request method exists"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client with request method
        mock_http_client = MagicMock()
        original_request = MagicMock()
        original_request.return_value = "success"
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Verify the request method was patched
        assert hasattr(mock_http_client, "request")
        assert mock_http_client.request != original_request

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_patch_client_without_request_method(
        self, mock_token_manager, mock_credentials
    ):
        """Test _patch_client when request method doesn't exist"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client without request method
        mock_http_client = MagicMock()
        delattr(mock_http_client, "request")
        client._client = mock_http_client

        # Should not raise an error
        client._patch_client()

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_patched_request_success(
        self, mock_token_manager, mock_credentials
    ):
        """Test patched request method successful execution"""
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
        original_request.return_value = "success"
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Call the patched request
        result = mock_http_client.request("arg1", kwarg1="value1")

        # Verify original request was called
        assert result == "success"
        original_request.assert_called_with("arg1", kwarg1="value1")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_patched_request_auth_error_retry(
        self, mock_token_manager, mock_credentials
    ):
        """Test patched request method with auth error and retry"""
        mock_manager = MagicMock()
        # Provide enough tokens for all the calls that happen during the test
        mock_manager.get_valid_token.side_effect = [
            "test_token",
            "test_token",
            "new_token",
            "new_token",
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
        # First call raises auth error, second succeeds
        original_request.side_effect = [
            Exception("401 Unauthorized"),
            "success",
        ]
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Call the patched request
        result = mock_http_client.request("arg1", kwarg1="value1")

        # Verify retry logic
        assert result == "success"
        assert original_request.call_count == 2
        mock_manager.invalidate_token.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_patched_request_non_auth_error(
        self, mock_token_manager, mock_credentials
    ):
        """Test patched request method with non-auth error"""
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
        original_request.side_effect = Exception("500 Internal Server Error")
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_client()

        # Call the patched request - should raise the original error
        with pytest.raises(Exception) as exc_info:
            mock_http_client.request("arg1", kwarg1="value1")

        assert "500 Internal Server Error" in str(exc_info.value)
        assert original_request.call_count == 1
        mock_manager.invalidate_token.assert_not_called()


@pytest.mark.unit
class TestAsyncHTTPClientPatching:
    """Test async HTTP client patching functionality"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_patch_async_client_with_request_method(
        self, mock_token_manager, mock_credentials
    ):
        """Test _patch_async_client when request method exists"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock async HTTP client with request method
        mock_http_client = MagicMock()
        original_request = AsyncMock()
        original_request.return_value = "success"
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_async_client()

        # Verify the request method was patched
        assert hasattr(mock_http_client, "request")
        assert mock_http_client.request != original_request

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_patched_async_request_success(
        self, mock_token_manager, mock_credentials
    ):
        """Test patched async request method successful execution"""
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
        original_request = AsyncMock()
        original_request.return_value = "success"
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_async_client()

        # Call the patched request
        result = await mock_http_client.request("arg1", kwarg1="value1")

        # Verify original request was called
        assert result == "success"
        original_request.assert_called_with("arg1", kwarg1="value1")

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_patched_async_request_auth_error_retry(
        self, mock_token_manager, mock_credentials
    ):
        """Test patched async request method with auth error and retry"""
        mock_manager = MagicMock()
        # Provide enough tokens for all the calls that happen during the test
        mock_manager.get_valid_token.side_effect = [
            "test_token",
            "test_token",
            "new_token",
            "new_token",
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
        # First call raises auth error, second succeeds
        original_request.side_effect = [
            Exception("401 Unauthorized"),
            "success",
        ]
        mock_http_client.request = original_request
        client._client = mock_http_client

        # Patch the client
        client._patch_async_client()

        # Call the patched request
        result = await mock_http_client.request("arg1", kwarg1="value1")

        # Verify retry logic
        assert result == "success"
        assert original_request.call_count == 2
        mock_manager.invalidate_token.assert_called_once()


@pytest.mark.unit
class TestContextManagers:
    """Test context manager functionality"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_sync_context_manager_with_parent(
        self, mock_token_manager, mock_credentials
    ):
        """Test sync context manager when parent has __enter__/__exit__"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        with patch("openai.OpenAI.__enter__") as mock_enter, patch(
            "openai.OpenAI.__exit__"
        ) as mock_exit:
            mock_enter.return_value = MagicMock()
            mock_exit.return_value = None

            client = OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )

            # Test context manager
            with client as ctx_client:
                assert ctx_client is client

            # Verify parent methods were called
            mock_enter.assert_called_once()
            mock_exit.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_sync_context_manager_without_parent(
        self, mock_token_manager, mock_credentials
    ):
        """Test sync context manager when parent doesn't have __enter__/__exit__"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Test context manager works even without parent implementation
        with client as ctx_client:
            assert ctx_client is client

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_sync_context_manager_exit_error(
        self, mock_token_manager, mock_credentials
    ):
        """Test sync context manager when parent __exit__ raises error"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        with patch("openai.OpenAI.__enter__") as mock_enter, patch(
            "openai.OpenAI.__exit__"
        ) as mock_exit:
            mock_enter.return_value = MagicMock()
            mock_exit.side_effect = Exception("Parent exit error")

            client = OpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )

            # Should not raise error, just log warning
            with client as ctx_client:
                assert ctx_client is client

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_context_manager_with_parent(
        self, mock_token_manager, mock_credentials
    ):
        """Test async context manager when parent has __aenter__/__aexit__"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        with patch("openai.AsyncOpenAI.__aenter__") as mock_aenter, patch(
            "openai.AsyncOpenAI.__aexit__"
        ) as mock_aexit:
            mock_aenter.return_value = AsyncMock()
            mock_aexit.return_value = AsyncMock()

            client = AsyncOpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )

            # Test async context manager
            async with client as ctx_client:
                assert ctx_client is client

            # Verify parent methods were called
            mock_aenter.assert_called_once()
            mock_aexit.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_context_manager_exit_error(
        self, mock_token_manager, mock_credentials
    ):
        """Test async context manager when parent __aexit__ raises error"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        with patch("openai.AsyncOpenAI.__aenter__") as mock_aenter, patch(
            "openai.AsyncOpenAI.__aexit__"
        ) as mock_aexit:
            mock_aenter.return_value = AsyncMock()
            mock_aexit.side_effect = Exception("Parent async exit error")

            client = AsyncOpenAI(
                key_id=mock_credentials["key_id"],
                secret=mock_credentials["secret"],
                base_url=mock_credentials["base_url"],
            )

            # Should not raise error, just log warning
            async with client as ctx_client:
                assert ctx_client is client


@pytest.mark.unit
class TestWithOptionsMethod:
    """Test with_options method functionality"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_with_options_creates_new_client(
        self, mock_token_manager, mock_credentials
    ):
        """Test with_options creates a new client instance"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            timeout=30.0,
            max_retries=2,
        )

        # Create new client with different options
        new_client = client.with_options(timeout=60.0, max_retries=5)

        # Verify new client has updated options
        assert new_client.timeout == 60.0
        assert new_client.max_retries == 5
        assert new_client.key_id == mock_credentials["key_id"]
        assert new_client.secret == mock_credentials["secret"]

        # Verify original client is unchanged
        assert client.timeout == 30.0
        assert client.max_retries == 2

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_with_options_preserves_credentials(
        self, mock_token_manager, mock_credentials
    ):
        """Test with_options preserves Evolution credentials"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id="test_project",
        )

        # Create new client with different options
        new_client = client.with_options(timeout=60.0)

        # Verify credentials are preserved
        assert new_client.key_id == mock_credentials["key_id"]
        assert new_client.secret == mock_credentials["secret"]
        assert new_client.project_id == "test_project"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_with_options_creates_new_client(
        self, mock_token_manager, mock_credentials
    ):
        """Test async with_options creates a new client instance"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            timeout=30.0,
            max_retries=2,
        )

        # Create new client with different options
        new_client = client.with_options(timeout=60.0, max_retries=5)

        # Verify new client has updated options
        assert new_client.timeout == 60.0
        assert new_client.max_retries == 5
        assert new_client.key_id == mock_credentials["key_id"]
        assert new_client.secret == mock_credentials["secret"]

        # Verify original client is unchanged
        assert client.timeout == 30.0
        assert client.max_retries == 2


@pytest.mark.unit
class TestInitializationMethods:
    """Test initialization helper methods"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_initialize_headers_with_valid_token(
        self, mock_token_manager, mock_credentials
    ):
        """Test _initialize_headers with valid token"""
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
        mock_http_client._auth_headers = {}
        client._client = mock_http_client

        # Initialize headers
        client._initialize_headers()

        # Verify headers were updated
        assert (
            mock_http_client._auth_headers["Authorization"]
            == "Bearer test_token"
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_initialize_headers_with_no_token(
        self, mock_token_manager, mock_credentials
    ):
        """Test _initialize_headers with no token"""
        mock_manager = MagicMock()
        # First call returns valid token for client creation, then None twice
        mock_manager.get_valid_token.side_effect = ["test_token", None, None]
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Should not raise error when called directly
        client._initialize_headers()


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_with_none_values(
        self, mock_token_manager, mock_credentials
    ):
        """Test client creation with None values"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            project_id=None,
            default_headers=None,
            timeout=None,
        )

        assert client.project_id is None
        assert client.timeout is None

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_token_manager_get_valid_token_returns_none(
        self, mock_token_manager, mock_credentials
    ):
        """Test behavior when token manager returns None"""
        mock_manager = MagicMock()
        # First call returns valid token for client creation, then None twice
        mock_manager.get_valid_token.side_effect = ["test_token", None, None]
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        assert client.current_token is None

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_refresh_token_returns_none(
        self, mock_token_manager, mock_credentials
    ):
        """Test refresh_token when it returns None"""
        mock_manager = MagicMock()
        # First call returns valid token for client creation, then None for refresh
        mock_manager.get_valid_token.side_effect = ["test_token", None, None]
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        new_token = client.refresh_token()
        assert new_token is None
        mock_manager.invalidate_token.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_properties_with_empty_strings(
        self, mock_token_manager, mock_credentials
    ):
        """Test client properties with empty strings"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = ""
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        assert client.current_token == ""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_get_request_headers_with_none_values(
        self, mock_token_manager, mock_credentials
    ):
        """Test get_request_headers with None values"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock HTTP client with None values
        mock_http_client = MagicMock()
        mock_http_client._auth_headers = None
        mock_http_client.default_headers = None
        mock_http_client._default_headers = None
        client._client = mock_http_client
        # Should not raise error and return empty dict for attributes not found
        headers = client.get_request_headers()
        assert isinstance(headers, dict)
