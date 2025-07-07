"""
Integration tests for Evolution Foundation Models

These tests require real Evolution Foundation Models credentials and are only run when
ENABLE_FOUNDATION_MODELS_TESTS=true or ENABLE_INTEGRATION_TESTS=true is set in environment or .env file.

Based on examples/foundation_models_example.py
"""

import time
import asyncio

import pytest


@pytest.mark.integration
@pytest.mark.foundation_models
class TestFoundationModelsIntegration:
    """Integration tests with real Evolution Foundation Models API"""

    def test_foundation_models_token_acquisition(
        self, foundation_models_client, foundation_models_credentials
    ):
        """Test acquiring real token from Foundation Models API"""
        # Test token acquisition
        token = foundation_models_client.current_token
        assert token is not None
        assert len(token) > 0

        # Test token info
        token_info = foundation_models_client.get_token_info()
        assert token_info["has_token"] is True
        assert token_info["is_valid"] is True

        # Verify project_id is configured
        assert (
            foundation_models_client.project_id
            == foundation_models_credentials["project_id"]
        )

        print(
            f"✅ Foundation Models token acquired successfully: {token[:20]}..."
        )
        print(f"🏷️ Project ID: {foundation_models_client.project_id}")

    def test_foundation_models_basic_chat_completion(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test basic chat completion with Foundation Models API"""
        print(f"🔧 Using model: {foundation_models_default_model}")

        response = foundation_models_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "system",
                    "content": "Ты полезный помощник, использующий Evolution Foundation Models.",
                },
                {
                    "role": "user",
                    "content": "Расскажи кратко о возможностях искусственного интеллекта",
                },
            ],
            max_tokens=10,
            temperature=0.7,
        )

        # Verify response structure
        assert response.choices is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

        # Verify response metadata
        assert response.model is not None
        assert response.usage is not None
        assert response.usage.total_tokens > 0

        print(f"✅ Response: {response.choices[0].message.content}")
        print(f"📊 Model: {response.model}")
        print(f"🔢 Total tokens: {response.usage.total_tokens}")

    def test_foundation_models_streaming(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test streaming with Foundation Models API"""
        print(
            f"🔧 Using model for streaming: {foundation_models_default_model}"
        )

        stream = foundation_models_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Напиши короткое стихотворение про технологии",
                }
            ],
            stream=True,
            max_tokens=15,
            temperature=0.8,
        )

        content_parts = []
        chunk_count = 0
        for chunk in stream:
            chunk_count += 1
            if (
                chunk.choices
                and len(chunk.choices) > 0
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                content = chunk.choices[0].delta.content
                content_parts.append(content)

        full_content = "".join(content_parts)
        assert len(full_content) > 0
        assert len(content_parts) > 0
        assert chunk_count > 0

        print(f"✅ Streaming response: {full_content}")
        print(
            f"📊 Received {len(content_parts)} content chunks in {chunk_count} total chunks"
        )

    def test_foundation_models_with_options(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test Foundation Models with additional options"""
        print(
            f"🔧 Using model with options: {foundation_models_default_model}"
        )

        # Test with_options for configuration
        client_with_options = foundation_models_client.with_options(
            timeout=60.0, max_retries=3
        )

        response = client_with_options.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Создай план изучения Python для начинающих",
                }
            ],
            max_tokens=15,
            temperature=0.3,
        )

        assert response.choices is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

        # Test token info
        token_info = client_with_options.get_token_info()
        assert token_info["has_token"] is True
        assert token_info["is_valid"] is True

        print(
            f"✅ Response with options: {response.choices[0].message.content}"
        )
        print(f"📊 Model: {response.model}")
        print(f"🔢 Total tokens: {response.usage.total_tokens}")
        print(f"🔑 Token status: {token_info}")

    def test_foundation_models_token_refresh(self, foundation_models_client):
        """Test token refresh with Foundation Models API"""
        # Get initial token
        token1 = foundation_models_client.current_token
        assert token1 is not None
        assert len(token1) > 0

        # Force refresh
        token2 = foundation_models_client.refresh_token()
        assert token2 is not None
        assert len(token2) > 0

        # Tokens should be different (new token)
        assert token1 != token2

        print(f"✅ Token refresh: {token1[:15]}... -> {token2[:15]}...")

    async def test_foundation_models_async_basic(
        self, foundation_models_async_client, foundation_models_default_model
    ):
        """Test basic async Foundation Models functionality"""
        print(f"🔧 Using model for async: {foundation_models_default_model}")

        response = await foundation_models_async_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Объясни простыми словами, что такое машинное обучение",
                }
            ],
            max_tokens=12,
            temperature=0.5,
        )

        assert response.choices is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

        print(f"✅ Async response: {response.choices[0].message.content}")
        print(f"📊 Model: {response.model}")
        print(f"🔢 Total tokens: {response.usage.total_tokens}")

    async def test_foundation_models_async_streaming(
        self, foundation_models_async_client, foundation_models_default_model
    ):
        """Test async streaming with Foundation Models"""
        print(
            f"🔧 Using model for async streaming: {foundation_models_default_model}"
        )

        stream = await foundation_models_async_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Напиши короткое стихотворение про космос",
                }
            ],
            stream=True,
            max_tokens=12,
            temperature=0.8,
        )

        content_parts = []
        chunk_count = 0
        async for chunk in stream:
            chunk_count += 1
            if (
                chunk.choices
                and len(chunk.choices) > 0
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                content = chunk.choices[0].delta.content
                content_parts.append(content)

        full_content = "".join(content_parts)
        assert len(full_content) > 0
        assert len(content_parts) > 0
        assert chunk_count > 0

        print(f"✅ Async streaming response: {full_content}")
        print(
            f"📊 Received {len(content_parts)} content chunks in {chunk_count} total chunks"
        )

    async def test_foundation_models_parallel_requests(
        self, foundation_models_async_client, foundation_models_default_model
    ):
        """Test parallel requests to Foundation Models"""
        print(
            f"🔧 Using model for parallel requests: {foundation_models_default_model}"
        )

        # List of questions for parallel processing
        questions = [
            "Что такое искусственный интеллект?",
            "Как работает машинное обучение?",
            "Что такое нейронные сети?",
        ]

        # Create tasks for parallel execution
        tasks = []
        for question in questions:
            task = foundation_models_async_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Дай краткий ответ в 1-2 предложения.",
                    },
                    {"role": "user", "content": question},
                ],
                max_tokens=10,
                temperature=0.5,
            )
            tasks.append(task)

        # Execute all requests in parallel
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        elapsed = end_time - start_time
        print(
            f"⚡ Processed {len(questions)} requests in {elapsed:.2f} seconds"
        )

        # Verify all responses
        for i, (question, response) in enumerate(zip(questions, responses)):
            assert response.choices is not None
            assert len(response.choices) > 0
            assert response.choices[0].message is not None
            assert response.choices[0].message.content is not None
            assert len(response.choices[0].message.content) > 0

            print(f"❓ Question {i + 1}: {question}")
            print(f"✅ Answer: {response.choices[0].message.content}")
            print(f"🔢 Tokens: {response.usage.total_tokens}")
            print("-" * 50)

        assert len(responses) == len(questions)


@pytest.mark.integration
@pytest.mark.foundation_models
@pytest.mark.slow
class TestFoundationModelsPerformance:
    """Performance and load tests for Foundation Models API"""

    def test_foundation_models_multiple_sequential_requests(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test multiple sequential requests to Foundation Models"""
        print(
            f"🔧 Testing sequential requests with model: {foundation_models_default_model}"
        )

        request_count = 3
        responses = []
        start_time = time.time()

        for i in range(request_count):
            response = foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Вопрос {i + 1}: Что такое программирование?",
                    }
                ],
                max_tokens=8,
                temperature=0.3,
            )
            responses.append(response)

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify all responses
        for i, response in enumerate(responses):
            assert response.choices is not None
            assert len(response.choices) > 0
            assert response.choices[0].message is not None
            assert response.choices[0].message.content is not None
            print(f"✅ Request {i + 1}: {response.choices[0].message.content}")

        print(
            f"⏱️ {request_count} sequential requests completed in {elapsed:.2f} seconds"
        )
        print(
            f"📊 Average time per request: {elapsed / request_count:.2f} seconds"
        )

    def test_foundation_models_streaming_performance(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test streaming performance with Foundation Models"""
        print(
            f"🔧 Testing streaming performance with model: {foundation_models_default_model}"
        )

        start_time = time.time()
        stream = foundation_models_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Напиши подробный рассказ о технологиях будущего",
                }
            ],
            stream=True,
            max_tokens=20,
            temperature=0.7,
        )

        content_parts = []
        chunk_timestamps = []

        for chunk in stream:
            chunk_timestamps.append(time.time())
            if (
                chunk.choices
                and len(chunk.choices) > 0
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                content_parts.append(chunk.choices[0].delta.content)

        end_time = time.time()
        total_elapsed = end_time - start_time

        full_content = "".join(content_parts)
        assert len(full_content) > 0

        # Calculate streaming statistics
        first_chunk_time = (
            chunk_timestamps[0] - start_time if chunk_timestamps else 0
        )
        avg_chunk_interval = 0
        if len(chunk_timestamps) > 1:
            intervals = [
                chunk_timestamps[i] - chunk_timestamps[i - 1]
                for i in range(1, len(chunk_timestamps))
            ]
            avg_chunk_interval = sum(intervals) / len(intervals)

        print("✅ Streaming completed")
        print(f"📊 Total content length: {len(full_content)} characters")
        print(f"⏱️ Total time: {total_elapsed:.2f} seconds")
        print(f"🚀 Time to first chunk: {first_chunk_time:.2f} seconds")
        print(f"📈 Average chunk interval: {avg_chunk_interval:.3f} seconds")
        print(f"🔢 Total chunks: {len(chunk_timestamps)}")
        print(f"📝 Content chunks: {len(content_parts)}")

    async def test_foundation_models_concurrent_load(
        self, foundation_models_async_client, foundation_models_default_model
    ):
        """Test concurrent load on Foundation Models API"""
        print(
            f"🔧 Testing concurrent load with model: {foundation_models_default_model}"
        )

        # Test with multiple concurrent requests
        concurrent_count = 5
        tasks = []

        for i in range(concurrent_count):
            task = foundation_models_async_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Concurrent request {i + 1}: Explain artificial intelligence briefly",
                    }
                ],
                max_tokens=8,
                temperature=0.4,
            )
            tasks.append(task)

        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        elapsed = end_time - start_time

        # Verify responses
        successful_responses = 0
        failed_responses = 0

        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"❌ Request {i + 1} failed: {response}")
                failed_responses += 1
            else:
                assert response.choices is not None
                assert len(response.choices) > 0
                assert response.choices[0].message is not None
                assert response.choices[0].message.content is not None
                print(
                    f"✅ Request {i + 1}: {response.choices[0].message.content}"
                )
                successful_responses += 1

        print(
            f"⚡ {concurrent_count} concurrent requests completed in {elapsed:.2f} seconds"
        )
        print(
            f"📊 Success rate: {successful_responses}/{concurrent_count} ({successful_responses / concurrent_count * 100:.1f}%)"
        )
        print(
            f"📈 Average time per request: {elapsed / concurrent_count:.2f} seconds"
        )

        # At least 80% should succeed
        assert successful_responses / concurrent_count >= 0.8


@pytest.mark.integration
@pytest.mark.foundation_models
class TestFoundationModelsErrorHandling:
    """Error handling tests for Foundation Models API"""

    def test_foundation_models_invalid_model(self, foundation_models_client):
        """Test error handling with invalid model name"""
        with pytest.raises(Exception) as exc_info:
            foundation_models_client.chat.completions.create(
                model="invalid-model-name-12345",
                messages=[
                    {
                        "role": "user",
                        "content": "This should fail",
                    }
                ],
                max_tokens=10,
            )

        print(f"✅ Expected error for invalid model: {exc_info.value}")

    def test_foundation_models_invalid_parameters(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test error handling with invalid parameters"""
        # Test with extremely high max_tokens (might be clamped instead of raising error)
        try:
            response = foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Test with very high max_tokens",
                    }
                ],
                max_tokens=999999,  # Extremely high value
            )
            # If it succeeds, the API might clamp the value rather than error
            print(
                f"✅ API handled high max_tokens gracefully: {response.usage.total_tokens} tokens"
            )
        except Exception as e:
            print(f"✅ Expected error for invalid max_tokens: {e}")

        # Test with invalid temperature (outside normal range)
        try:
            response = foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Test with invalid temperature",
                    }
                ],
                max_tokens=8,
                temperature=10.0,  # Invalid temperature value
            )
            # If it succeeds, the API might clamp the value rather than error
            print("✅ API handled high temperature gracefully")
        except Exception as e:
            print(f"✅ Expected error for invalid temperature: {e}")

        # Test with completely invalid parameter type (this should fail)
        with pytest.raises(Exception) as exc_info:
            foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages="invalid_messages_type",  # Should be list, not string
                max_tokens=8,
            )

        print(f"✅ Expected error for invalid message type: {exc_info.value}")

    def test_foundation_models_empty_messages(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test error handling with empty messages"""
        with pytest.raises(Exception) as exc_info:
            foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[],
                max_tokens=10,
            )

        print(f"✅ Expected error for empty messages: {exc_info.value}")

    async def test_foundation_models_async_error_handling(
        self, foundation_models_async_client, foundation_models_default_model
    ):
        """Test async error handling"""
        with pytest.raises(Exception) as exc_info:
            await foundation_models_async_client.chat.completions.create(
                model="invalid-async-model",
                messages=[
                    {
                        "role": "user",
                        "content": "This should fail async",
                    }
                ],
                max_tokens=10,
            )

        print(f"✅ Expected async error: {exc_info.value}")


@pytest.mark.integration
@pytest.mark.foundation_models
class TestFoundationModelsCompatibility:
    """Compatibility tests for Foundation Models API"""

    def test_foundation_models_different_temperatures(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test Foundation Models with different temperature settings"""
        temperatures = [0.1, 0.5, 0.9]

        for temp in temperatures:
            response = foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate text with temperature {temp}",
                    }
                ],
                max_tokens=8,
                temperature=temp,
            )

            assert response.choices is not None
            assert len(response.choices) > 0
            assert response.choices[0].message is not None
            assert response.choices[0].message.content is not None

            print(
                f"✅ Temperature {temp}: {response.choices[0].message.content}"
            )

    def test_foundation_models_different_max_tokens(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test Foundation Models with different max_tokens settings"""
        max_tokens_values = [5, 10, 15]

        for max_tokens in max_tokens_values:
            response = foundation_models_client.chat.completions.create(
                model=foundation_models_default_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Tell me about programming",
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.5,
            )

            assert response.choices is not None
            assert len(response.choices) > 0
            assert response.choices[0].message is not None
            assert response.choices[0].message.content is not None
            assert response.usage.total_tokens > 0

            print(
                f"✅ Max tokens {max_tokens}: {len(response.choices[0].message.content)} chars, {response.usage.total_tokens} tokens"
            )

    def test_foundation_models_system_messages(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test Foundation Models with system messages"""
        response = foundation_models_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "system",
                    "content": "Ты эксперт по программированию. Отвечай кратко и точно.",
                },
                {
                    "role": "user",
                    "content": "Что такое Python?",
                },
            ],
            max_tokens=10,
            temperature=0.3,
        )

        assert response.choices is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None

        print(
            f"✅ System message response: {response.choices[0].message.content}"
        )

    def test_foundation_models_conversation_history(
        self, foundation_models_client, foundation_models_default_model
    ):
        """Test Foundation Models with conversation history"""
        response = foundation_models_client.chat.completions.create(
            model=foundation_models_default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Привет! Как дела?",
                },
                {
                    "role": "assistant",
                    "content": "Привет! Дела хорошо, спасибо за вопрос!",
                },
                {
                    "role": "user",
                    "content": "Можешь рассказать о машинном обучении?",
                },
            ],
            max_tokens=12,
            temperature=0.4,
        )

        assert response.choices is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None

        print(
            f"✅ Conversation history response: {response.choices[0].message.content}"
        )
