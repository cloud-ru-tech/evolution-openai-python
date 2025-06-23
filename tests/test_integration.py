"""
Integration tests for Evolution OpenAI

These tests require real Evolution credentials and are only run when
ENABLE_INTEGRATION_TESTS=true is set in environment or .env file.
"""

import pytest


@pytest.mark.integration
class TestEvolutionIntegration:
    """Integration tests with real Evolution API"""

    def get_available_model(self, client):
        """Helper to get the first available model from the API"""
        try:
            models = client.models.list()
            if models and models.data and len(models.data) > 0:
                return models.data[0].id
            else:
                pytest.skip("No models available from /v1/models endpoint")
        except Exception as e:
            pytest.skip(f"Cannot get available models: {e}")

    async def get_available_model_async(self, client):
        """Helper to get the first available model from the API (async)"""
        try:
            models = await client.models.list()
            if models and models.data and len(models.data) > 0:
                return models.data[0].id
            else:
                pytest.skip("No models available from /v1/models endpoint")
        except Exception as e:
            pytest.skip(f"Cannot get available models: {e}")

    def test_real_token_acquisition(self, client):
        """Test acquiring real token from Evolution API using session client fixture"""
        # Test token acquisition
        token = client.current_token
        assert token is not None
        assert len(token) > 0

        # Test token info
        token_info = client.get_token_info()
        assert token_info["has_token"] is True
        assert token_info["is_valid"] is True

        print(f"✅ Token acquired successfully: {token[:20]}...")

    def test_real_chat_completion(self, client):
        """Test real chat completion with Evolution API using session client fixture"""
        # Get an available model from the API
        model_name = self.get_available_model(client)
        print(f"🔧 Using model: {model_name}")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Say 'Hello, Evolution SDK!'"}
            ],
            max_tokens=50,
        )

        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

        print(f"✅ Chat completion: {response.choices[0].message.content}")

    def test_real_models_endpoint(self, client):
        """Test getting model names from /v1/models endpoint using session client fixture"""
        # Get list of available models
        models = client.models.list()

        assert models is not None
        assert hasattr(models, "data")
        assert len(models.data) > 0

        print(f"✅ Available models ({len(models.data)} total):")
        for model in models.data:
            assert hasattr(model, "id")
            assert model.id is not None
            assert len(model.id) > 0
            print(f"  - {model.id}")

            # Additional model properties that might be available
            if hasattr(model, "created"):
                print(f"    Created: {model.created}")
            if hasattr(model, "owned_by"):
                print(f"    Owned by: {model.owned_by}")

    def test_real_streaming(self, client):
        """Test real streaming with Evolution API using session client fixture"""
        # Get an available model from the API
        model_name = self.get_available_model(client)
        print(f"🔧 Using model for streaming: {model_name}")

        stream = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Count from 1 to 3"}],
            stream=True,
            max_tokens=30,
        )

        content_chunks = []
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content_chunks.append(chunk.choices[0].delta.content)

        full_content = "".join(content_chunks)
        assert len(full_content) > 0

        print(f"✅ Streaming response: {full_content}")

    async def test_real_async_completion(self, async_client):
        """Test real async completion with Evolution API using session async client fixture"""
        # Get an available model from the API
        model_name = await self.get_available_model_async(async_client)
        print(f"🔧 Using model for async completion: {model_name}")

        response = await async_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Async hello from Evolution!"}
            ],
            max_tokens=50,
        )

        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

        print(f"✅ Async completion: {response.choices[0].message.content}")

    async def test_real_async_models_endpoint(self, async_client):
        """Test getting model names from /v1/models endpoint asynchronously using session async client fixture"""
        # Get list of available models asynchronously
        models = await async_client.models.list()

        assert models is not None
        assert hasattr(models, "data")
        assert len(models.data) > 0

        print(f"✅ Async - Available models ({len(models.data)} total):")
        for model in models.data:
            assert hasattr(model, "id")
            assert model.id is not None
            assert len(model.id) > 0
            print(f"  - {model.id}")

            # Additional model properties that might be available
            if hasattr(model, "created"):
                print(f"    Created: {model.created}")
            if hasattr(model, "owned_by"):
                print(f"    Owned by: {model.owned_by}")

    def test_helper_function_integration(self, client):
        """Test helper functions with real API using session client fixture"""
        # Get an available model from the API
        model_name = self.get_available_model(client)
        print(f"🔧 Using model for helper function test: {model_name}")

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Helper function test"}],
            max_tokens=30,
        )

        assert response.choices[0].message.content is not None
        print(f"✅ Helper function: {response.choices[0].message.content}")

    def test_token_refresh_integration(self, client):
        """Test token refresh with real API using session client fixture"""
        # Get initial token
        token1 = client.current_token

        # Force refresh
        token2 = client.refresh_token()

        # Tokens should be different (new token)
        assert token1 != token2
        assert len(token2) > 0

        print(f"✅ Token refresh: {token1[:15]}... -> {token2[:15]}...")


@pytest.mark.integration
@pytest.mark.slow
class TestEvolutionPerformance:
    """Performance and load tests for Evolution API"""

    def get_available_model(self, client):
        """Helper to get the first available model from the API"""
        try:
            models = client.models.list()
            if models and models.data and len(models.data) > 0:
                return models.data[0].id
            else:
                pytest.skip("No models available from /v1/models endpoint")
        except Exception as e:
            pytest.skip(f"Cannot get available models: {e}")

    def test_multiple_requests(self, client):
        """Test multiple sequential requests using session client fixture"""
        # Get an available model from the API
        model_name = self.get_available_model(client)
        print(f"🔧 Using model for multiple requests: {model_name}")

        for i in range(3):
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": f"Request {i + 1}"}],
                max_tokens=20,
            )
            assert response.choices[0].message.content is not None
            print(f"✅ Request {i + 1}: OK")
