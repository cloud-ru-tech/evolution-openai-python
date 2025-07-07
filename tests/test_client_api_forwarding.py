"""
Tests for API method forwarding and edge cases in Evolution OpenAI Client
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from evolution_openai import OpenAI, AsyncOpenAI


@pytest.mark.unit
class TestAPIMethodForwarding:
    """Test that API methods are properly forwarded"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_chat_completions_create_forwarding(
        self, mock_token_manager, mock_credentials
    ):
        """Test that chat.completions.create is properly forwarded"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying chat.completions.create method
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"

        client.chat.completions.create = MagicMock(return_value=mock_response)

        # Call the method
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=100,
        )

        # Verify the method was called correctly
        client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=100,
        )
        assert response.choices[0].message.content == "Test response"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_models_list_forwarding(
        self, mock_token_manager, mock_credentials
    ):
        """Test that models.list is properly forwarded"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying models.list method
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].id = "gpt-3.5-turbo"

        client.models.list = MagicMock(return_value=mock_response)

        # Call the method
        response = client.models.list()

        # Verify the method was called correctly
        client.models.list.assert_called_once()
        assert response.data[0].id == "gpt-3.5-turbo"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_models_retrieve_forwarding(
        self, mock_token_manager, mock_credentials
    ):
        """Test that models.retrieve is properly forwarded"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying models.retrieve method
        mock_response = MagicMock()
        mock_response.id = "gpt-3.5-turbo"
        mock_response.owned_by = "openai"

        client.models.retrieve = MagicMock(return_value=mock_response)

        # Call the method
        response = client.models.retrieve("gpt-3.5-turbo")

        # Verify the method was called correctly
        client.models.retrieve.assert_called_once_with("gpt-3.5-turbo")
        assert response.id == "gpt-3.5-turbo"

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_completions_create_forwarding(
        self, mock_token_manager, mock_credentials
    ):
        """Test that completions.create is properly forwarded"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying completions.create method
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].text = "Test completion"

        client.completions.create = MagicMock(return_value=mock_response)

        # Call the method
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Hello",
            max_tokens=100,
        )

        # Verify the method was called correctly
        client.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo-instruct",
            prompt="Hello",
            max_tokens=100,
        )
        assert response.choices[0].text == "Test completion"

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_chat_completions_create_forwarding(
        self, mock_token_manager, mock_credentials
    ):
        """Test that async chat.completions.create is properly forwarded"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying async chat.completions.create method
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Async test response"

        client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Call the method
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello async"}],
            max_tokens=100,
        )

        # Verify the method was called correctly
        client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello async"}],
            max_tokens=100,
        )
        assert response.choices[0].message.content == "Async test response"

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_models_list_forwarding(
        self, mock_token_manager, mock_credentials
    ):
        """Test that async models.list is properly forwarded"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying async models.list method
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].id = "gpt-3.5-turbo"

        client.models.list = AsyncMock(return_value=mock_response)

        # Call the method
        response = await client.models.list()

        # Verify the method was called correctly
        client.models.list.assert_called_once()
        assert response.data[0].id == "gpt-3.5-turbo"


@pytest.mark.unit
class TestStreamingSupport:
    """Test streaming response support"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_streaming_chat_completions(
        self, mock_token_manager, mock_credentials
    ):
        """Test streaming chat completions"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock streaming response
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Hello"

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " world"

        mock_stream = iter([mock_chunk1, mock_chunk2])

        client.chat.completions.create = MagicMock(return_value=mock_stream)

        # Call the method with streaming
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
        )

        # Verify streaming works
        chunks = list(stream)
        assert len(chunks) == 2
        assert chunks[0].choices[0].delta.content == "Hello"
        assert chunks[1].choices[0].delta.content == " world"

    @patch("evolution_openai.client.EvolutionTokenManager")
    async def test_async_streaming_chat_completions(
        self, mock_token_manager, mock_credentials
    ):
        """Test async streaming chat completions"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock async streaming response
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Async hello"

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " async world"

        async def mock_async_generator():
            yield mock_chunk1
            yield mock_chunk2

        client.chat.completions.create = AsyncMock(
            return_value=mock_async_generator()
        )

        # Call the method with streaming
        stream = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello async"}],
            stream=True,
        )

        # Verify async streaming works
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0].choices[0].delta.content == "Async hello"
        assert chunks[1].choices[0].delta.content == " async world"


@pytest.mark.unit
class TestAdvancedParameterHandling:
    """Test advanced parameter handling scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_extra_headers_handling(
        self, mock_token_manager, mock_credentials
    ):
        """Test handling of extra headers"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying method
        mock_response = MagicMock()
        client.chat.completions.create = MagicMock(return_value=mock_response)

        # Call with extra headers
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            extra_headers={"X-Custom": "value"},
        )

        # Verify extra headers were passed
        client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            extra_headers={"X-Custom": "value"},
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_extra_query_handling(self, mock_token_manager, mock_credentials):
        """Test handling of extra query parameters"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying method
        mock_response = MagicMock()
        client.chat.completions.create = MagicMock(return_value=mock_response)

        # Call with extra query parameters
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            extra_query={"param": "value"},
        )

        # Verify extra query parameters were passed
        client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            extra_query={"param": "value"},
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_extra_body_handling(self, mock_token_manager, mock_credentials):
        """Test handling of extra body parameters"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying method
        mock_response = MagicMock()
        client.chat.completions.create = MagicMock(return_value=mock_response)

        # Call with extra body parameters
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            extra_body={"custom": "data"},
        )

        # Verify extra body parameters were passed
        client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            extra_body={"custom": "data"},
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_timeout_parameter_handling(
        self, mock_token_manager, mock_credentials
    ):
        """Test handling of timeout parameters"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock the underlying method
        mock_response = MagicMock()
        client.chat.completions.create = MagicMock(return_value=mock_response)

        # Call with timeout parameter
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            timeout=30.0,
        )

        # Verify timeout parameter was passed
        client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            timeout=30.0,
        )


@pytest.mark.unit
class TestRawResponseSupport:
    """Test raw response support"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_with_raw_response_support(
        self, mock_token_manager, mock_credentials
    ):
        """Test with_raw_response functionality"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock raw response functionality
        mock_raw_response = MagicMock()
        mock_raw_response.parsed = MagicMock()
        mock_raw_response.parsed.choices = [MagicMock()]
        mock_raw_response.parsed.choices[
            0
        ].message.content = "Raw response test"

        client.chat.completions.with_raw_response = MagicMock()
        client.chat.completions.with_raw_response.create = MagicMock(
            return_value=mock_raw_response
        )

        # Call with raw response
        response = client.chat.completions.with_raw_response.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
        )

        # Verify raw response was used
        client.chat.completions.with_raw_response.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert (
            response.parsed.choices[0].message.content == "Raw response test"
        )

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_with_streaming_response_support(
        self, mock_token_manager, mock_credentials
    ):
        """Test with_streaming_response functionality"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Mock streaming response functionality
        mock_streaming_response = MagicMock()
        mock_streaming_response.parsed = iter([MagicMock()])

        client.chat.completions.with_streaming_response = MagicMock()
        client.chat.completions.with_streaming_response.create = MagicMock(
            return_value=mock_streaming_response
        )

        # Call with streaming response
        response = client.chat.completions.with_streaming_response.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
        )

        # Verify streaming response was used
        client.chat.completions.with_streaming_response.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
        )
        assert response.parsed is not None


@pytest.mark.unit
class TestEdgeCaseScenarios:
    """Test edge case scenarios"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_with_empty_base_url(
        self, mock_token_manager, mock_credentials
    ):
        """Test client creation with empty base_url"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url="",
        )

        assert client.key_id == mock_credentials["key_id"]
        assert client.secret == mock_credentials["secret"]

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_with_none_credentials(self, mock_token_manager):
        """Test client creation with None credentials"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # This should work as the client doesn't validate credentials
        client = OpenAI(
            key_id="",
            secret="",
            base_url="https://api.example.com",
        )

        assert client.key_id == ""
        assert client.secret == ""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_method_attribute_access(
        self, mock_token_manager, mock_credentials
    ):
        """Test that client preserves all method attributes"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Test that common OpenAI client attributes are accessible
        assert hasattr(client, "chat")
        assert hasattr(client, "models")
        assert hasattr(client, "completions")

        # Test nested attributes
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_client_method_attribute_access(
        self, mock_token_manager, mock_credentials
    ):
        """Test that async client preserves all method attributes"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Test that common OpenAI client attributes are accessible
        assert hasattr(client, "chat")
        assert hasattr(client, "models")
        assert hasattr(client, "completions")

        # Test nested attributes
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_with_unusual_parameters(
        self, mock_token_manager, mock_credentials
    ):
        """Test client with unusual but valid parameters"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
            timeout=0.1,  # Very short timeout
            max_retries=0,  # No retries
        )

        assert client.timeout == 0.1
        assert client.max_retries == 0

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_inheritance_chain(
        self, mock_token_manager, mock_credentials
    ):
        """Test that client maintains proper inheritance chain"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Should be instance of both Evolution and OpenAI classes
        assert isinstance(client, OpenAI)
        # Check that it has the expected methods
        assert hasattr(client, "current_token")
        assert hasattr(client, "refresh_token")
        assert hasattr(client, "get_token_info")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_client_inheritance_chain(
        self, mock_token_manager, mock_credentials
    ):
        """Test that async client maintains proper inheritance chain"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Should be instance of both Evolution and AsyncOpenAI classes
        assert isinstance(client, AsyncOpenAI)
        # Check that it has the expected methods
        assert hasattr(client, "current_token")
        assert hasattr(client, "refresh_token")
        assert hasattr(client, "get_token_info")
