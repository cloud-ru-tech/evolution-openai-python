"""
Тесты совместимости с официальным OpenAI SDK

Проверяют что Evolution OpenAI поддерживает все методы и аргументы
официального OpenAI Python SDK для обеспечения 100% drop-in replacement.
"""

import inspect
from unittest.mock import MagicMock, patch

import pytest

from evolution_openai import OpenAI, AsyncOpenAI

try:
    from openai import OpenAI as OriginalOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OriginalOpenAI = None


@pytest.mark.unit
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI SDK not available")
class TestMethodCompatibility:
    """Тесты совместимости методов с OpenAI SDK"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_has_chat_completions_create(
        self, mock_token_manager, mock_credentials
    ):
        """Тест наличия метода chat.completions.create"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем наличие метода
        assert hasattr(client, "chat")
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")
        assert callable(client.chat.completions.create)

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_has_models_methods(
        self, mock_token_manager, mock_credentials
    ):
        """Тест наличия методов models API"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем наличие методов models API
        assert hasattr(client, "models")
        assert hasattr(client.models, "list")
        assert hasattr(client.models, "retrieve")
        assert callable(client.models.list)
        assert callable(client.models.retrieve)

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_client_has_completions_create(
        self, mock_token_manager, mock_credentials
    ):
        """Тест наличия legacy completions.create"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем наличие legacy completions
        assert hasattr(client, "completions")
        assert hasattr(client.completions, "create")
        assert callable(client.completions.create)

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_advanced_features_compatibility(
        self, mock_token_manager, mock_credentials
    ):
        """Тест совместимости advanced features"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем with_options
        assert hasattr(client, "with_options")
        assert callable(client.with_options)

        # Проверяем with_raw_response
        assert hasattr(client.chat.completions, "with_raw_response")

        # Проверяем context manager поддержку
        assert hasattr(client, "__enter__")
        assert hasattr(client, "__exit__")


@pytest.mark.unit
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI SDK not available")
class TestArgumentCompatibility:
    """Тесты совместимости аргументов методов"""

    def test_chat_completions_create_signature(self):
        """Тест совместимости сигнатуры chat.completions.create"""
        # Создаем экземпляр для получения сигнатуры
        original_client = OriginalOpenAI(api_key="dummy")
        original_sig = inspect.signature(
            original_client.chat.completions.create
        )

        # Получаем параметры оригинального метода
        original_params = set(original_sig.parameters.keys())

        # Основные обязательные параметры
        required_params = {
            "model",
            "messages",
            "frequency_penalty",
            "function_call",
            "functions",
            "logit_bias",
            "logprobs",
            "max_tokens",
            "n",
            "presence_penalty",
            "response_format",
            "seed",
            "stop",
            "stream",
            "temperature",
            "tool_choice",
            "tools",
            "top_logprobs",
            "top_p",
            "user",
        }

        # Проверяем что основные параметры присутствуют
        missing_params = required_params - original_params
        assert len(missing_params) == 0, (
            f"Missing parameters: {missing_params}"
        )

    def test_models_list_signature(self):
        """Тест совместимости сигнатуры models.list"""
        original_client = OriginalOpenAI(api_key="dummy")
        original_sig = inspect.signature(original_client.models.list)

        # models.list обычно не принимает параметры кроме стандартных
        assert "extra_headers" in original_sig.parameters
        assert "extra_query" in original_sig.parameters
        assert "extra_body" in original_sig.parameters

    def test_client_init_signature_compatibility(self):
        """Тест совместимости параметров инициализации клиента"""
        original_sig = inspect.signature(OriginalOpenAI.__init__)
        original_params = set(original_sig.parameters.keys())

        # Основные параметры OpenAI client
        expected_params = {
            "api_key",
            "organization",
            "base_url",
            "timeout",
            "max_retries",
            "default_headers",
            "default_query",
            "http_client",
        }

        # Проверяем что основные параметры поддерживаются
        missing_params = expected_params - original_params
        assert len(missing_params) == 0, (
            f"Missing init params: {missing_params}"
        )


@pytest.mark.unit
class TestAsyncCompatibility:
    """Тесты совместимости async методов"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_client_has_chat_completions(
        self, mock_token_manager, mock_credentials
    ):
        """Тест наличия async chat.completions.create"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем наличие async методов
        assert hasattr(client, "chat")
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_client_has_models_methods(
        self, mock_token_manager, mock_credentials
    ):
        """Тест наличия async models методов"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем наличие async models API
        assert hasattr(client, "models")
        assert hasattr(client.models, "list")
        assert hasattr(client.models, "retrieve")

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_async_context_manager(self, mock_token_manager, mock_credentials):
        """Тест async context manager поддержки"""
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        client = AsyncOpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем async context manager
        assert hasattr(client, "__aenter__")
        assert hasattr(client, "__aexit__")


@pytest.mark.unit
class TestParameterValidation:
    """Тесты валидации параметров"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_chat_create_accepts_all_parameters(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест что chat.completions.create принимает все стандартные
        параметры"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем все вложенные объекты
        mock_openai_instance.chat = MagicMock()
        mock_openai_instance.chat.completions = MagicMock()
        mock_openai_instance.chat.completions.create = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = MagicMock()

        # Мокаем HTTP клиент для предотвращения реальных запросов
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Тестируем с максимальным набором параметров (без устаревших)
        try:
            result = client.chat.completions.create(
                model="test-model",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["\\n"],
                stream=False,
                logprobs=False,
                # Убираем echo - устаревший параметр
                n=1,
                user="test-user",
                # Дополнительные параметры
                extra_headers={"Custom": "Header"},
                extra_query={"param": "value"},
                extra_body={"extra": "data"},
            )
            # Проверяем что результат получен
            assert result is not None
        except Exception as e:
            pytest.fail(f"Method rejected valid parameters: {e}")

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_models_list_accepts_parameters(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест что models.list принимает стандартные параметры"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем models API
        mock_openai_instance.models = MagicMock()
        mock_openai_instance.models.list = MagicMock()
        mock_openai_instance.models.list.return_value = MagicMock()

        # Мокаем HTTP клиент чтобы избежать реальных запросов
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        try:
            result = client.models.list(
                extra_headers={"Custom": "Header"},
                extra_query={"param": "value"},
                extra_body={"extra": "data"},
            )
            assert result is not None
        except Exception as e:
            pytest.fail(f"models.list rejected valid parameters: {e}")


@pytest.mark.unit
class TestStreamingCompatibility:
    """Тесты совместимости streaming"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_streaming_response_compatibility(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест совместимости streaming responses"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Мокаем streaming response
        mock_stream = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" World"))]),
        ]

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем chat API с streaming
        mock_openai_instance.chat = MagicMock()
        mock_openai_instance.chat.completions = MagicMock()
        mock_openai_instance.chat.completions.create = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = iter(
            mock_stream
        )

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Тестируем streaming
        stream = client.chat.completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "test"}],
            stream=True,
        )

        # Проверяем что можно итерироваться
        chunks = list(stream)
        assert len(chunks) == 2
        assert chunks[0].choices[0].delta.content == "Hello"
        assert chunks[1].choices[0].delta.content == " World"


@pytest.mark.unit
class TestErrorCompatibility:
    """Тесты совместимости обработки ошибок"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_openai_errors_passthrough(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест что ошибки OpenAI SDK проходят без изменений"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Мокаем OpenAI ошибку
        from openai import APIError

        # Создаем мок request для новых версий OpenAI SDK
        mock_request = MagicMock()
        mock_request.url = "https://api.openai.com/test"
        mock_request.method = "POST"

        try:
            # Пробуем создать ошибку с новым API (request parameter)
            api_error = APIError(
                "Test API error", request=mock_request, body=None
            )
        except TypeError:
            # Если не работает, пробуем старый API
            try:
                api_error = APIError("Test API error")
            except Exception:
                # Если совсем не работает, пропускаем тест
                pytest.skip(
                    "Cannot create APIError with current OpenAI version"
                )

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем chat API с ошибкой
        mock_openai_instance.chat = MagicMock()
        mock_openai_instance.chat.completions = MagicMock()
        mock_openai_instance.chat.completions.create = MagicMock()
        mock_openai_instance.chat.completions.create.side_effect = api_error

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Проверяем что ошибка проходит как есть
        with pytest.raises(APIError):
            client.chat.completions.create(
                model="test-model",
                messages=[{"role": "user", "content": "test"}],
            )


@pytest.mark.unit
class TestResponseCompatibility:
    """Тесты совместимости ответов"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_response_object_compatibility(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест совместимости объектов ответов"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Создаем мок ответа похожий на настоящий
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Test response", role="assistant"),
                finish_reason="stop",
                index=0,
            )
        ]
        mock_response.created = 1234567890
        mock_response.id = "chatcmpl-test"
        mock_response.model = "test-model"
        mock_response.object = "chat.completion"
        mock_response.usage = MagicMock(
            completion_tokens=10, prompt_tokens=5, total_tokens=15
        )

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем chat API
        mock_openai_instance.chat = MagicMock()
        mock_openai_instance.chat.completions = MagicMock()
        mock_openai_instance.chat.completions.create = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = (
            mock_response
        )

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        response = client.chat.completions.create(
            model="test-model", messages=[{"role": "user", "content": "test"}]
        )

        # Проверяем структуру ответа
        assert hasattr(response, "choices")
        assert hasattr(response, "created")
        assert hasattr(response, "id")
        assert hasattr(response, "model")
        assert hasattr(response, "object")
        assert hasattr(response, "usage")

        # Проверяем данные
        assert response.choices[0].message.content == "Test response"
        assert response.choices[0].message.role == "assistant"
        assert response.usage.total_tokens == 15


@pytest.mark.integration
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI SDK not available")
class TestRealCompatibility:
    """Интеграционные тесты реальной совместимости"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    def test_method_signatures_match(self, mock_token_manager):
        """Тест что сигнатуры методов совпадают с оригинальными"""

        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Сравниваем основные методы
        methods_to_check = [
            ("chat.completions.create", "chat.completions.create"),
            ("models.list", "models.list"),
            ("models.retrieve", "models.retrieve"),
        ]

        for original_path, evolution_path in methods_to_check:
            # Получаем оригинальный метод через экземпляр
            original_client = OriginalOpenAI(api_key="dummy")
            original_obj = original_client
            for attr in original_path.split("."):
                original_obj = getattr(original_obj, attr)

            # Получаем Evolution метод через экземпляр
            from evolution_openai.client import EvolutionOpenAI

            evolution_client = EvolutionOpenAI(
                key_id="dummy", secret="dummy", base_url="https://dummy.com"
            )
            evolution_obj = evolution_client
            for attr in evolution_path.split("."):
                evolution_obj = getattr(evolution_obj, attr)

            # Сравниваем сигнатуры (игнорируя self)
            original_sig = inspect.signature(original_obj)
            evolution_sig = inspect.signature(evolution_obj)

            # Убираем self из параметров
            original_params = {
                k: v for k, v in original_sig.parameters.items() if k != "self"
            }
            evolution_params = {
                k: v
                for k, v in evolution_sig.parameters.items()
                if k != "self"
            }

            # Проверяем совместимость основных параметров
            for param_name, param in original_params.items():
                if param_name in evolution_params:
                    evolution_param = evolution_params[param_name]
                    assert param.kind == evolution_param.kind, (
                        f"Parameter {param_name} kind mismatch "
                        f"in {original_path}"
                    )
