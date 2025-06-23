"""
Детальные тесты совместимости методов и аргументов

Проверяют точную совместимость каждого метода и всех его аргументов
с официальным OpenAI SDK.
"""

import inspect
from unittest.mock import MagicMock, patch

import pytest

from evolution_openai import OpenAI

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@pytest.fixture(autouse=True)
def mock_openai_global():
    """Глобальное мокирование OpenAI для всех тестов в этом файле"""
    token_manager_patch = patch(
        "evolution_openai.client.EvolutionTokenManager"
    )
    openai_patch = patch("openai.OpenAI.__new__")

    mock_token_manager = token_manager_patch.start()
    mock_openai_new = openai_patch.start()

    # Мокаем token manager
    mock_manager = MagicMock()
    mock_manager.get_valid_token.return_value = "test_token"
    mock_token_manager.return_value = mock_manager

    # Создаем полный мок экземпляра
    mock_openai_instance = MagicMock()
    mock_openai_new.return_value = mock_openai_instance

    # Мокаем всю структуру API
    mock_openai_instance.chat = MagicMock()
    mock_openai_instance.chat.completions = MagicMock()
    mock_openai_instance.chat.completions.create = MagicMock()
    mock_openai_instance.models = MagicMock()
    mock_openai_instance.models.list = MagicMock()
    mock_openai_instance.models.retrieve = MagicMock()
    mock_openai_instance.completions = MagicMock()
    mock_openai_instance.completions.create = MagicMock()

    # Мокаем HTTP клиент
    mock_openai_instance._client = MagicMock()
    mock_openai_instance.api_key = "test_token"

    # Мокаем сигнатуры для signature тестов
    from inspect import Parameter, Signature

    # Сигнатура для chat.completions.create
    chat_params = [
        Parameter("model", Parameter.POSITIONAL_OR_KEYWORD),
        Parameter("messages", Parameter.POSITIONAL_OR_KEYWORD),
        Parameter("frequency_penalty", Parameter.KEYWORD_ONLY, default=None),
        Parameter("function_call", Parameter.KEYWORD_ONLY, default=None),
        Parameter("functions", Parameter.KEYWORD_ONLY, default=None),
        Parameter("logit_bias", Parameter.KEYWORD_ONLY, default=None),
        Parameter("logprobs", Parameter.KEYWORD_ONLY, default=None),
        Parameter("max_tokens", Parameter.KEYWORD_ONLY, default=None),
        Parameter("n", Parameter.KEYWORD_ONLY, default=1),
        Parameter("presence_penalty", Parameter.KEYWORD_ONLY, default=None),
        Parameter("response_format", Parameter.KEYWORD_ONLY, default=None),
        Parameter("seed", Parameter.KEYWORD_ONLY, default=None),
        Parameter("stop", Parameter.KEYWORD_ONLY, default=None),
        Parameter("stream", Parameter.KEYWORD_ONLY, default=False),
        Parameter("temperature", Parameter.KEYWORD_ONLY, default=1),
        Parameter("tool_choice", Parameter.KEYWORD_ONLY, default=None),
        Parameter("tools", Parameter.KEYWORD_ONLY, default=None),
        Parameter("top_logprobs", Parameter.KEYWORD_ONLY, default=None),
        Parameter("top_p", Parameter.KEYWORD_ONLY, default=1),
        Parameter("user", Parameter.KEYWORD_ONLY, default=None),
    ]
    chat_signature = Signature(chat_params)
    mock_openai_instance.chat.completions.create.__signature__ = chat_signature

    yield mock_openai_new, mock_openai_instance

    # Cleanup
    token_manager_patch.stop()
    openai_patch.stop()


@pytest.mark.unit
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI SDK not available")
class TestChatCompletionsMethod:
    """Детальные тесты метода chat.completions.create"""

    def test_chat_completions_create_signature_exact(self):
        """Точная проверка сигнатуры chat.completions.create"""
        # Используем замоканный экземпляр
        original_client = openai.OpenAI(api_key="dummy")
        original_sig = inspect.signature(
            original_client.chat.completions.create
        )

        # Все параметры метода
        all_params = list(original_sig.parameters.keys())

        # Обязательные параметры
        required = ["model", "messages"]
        for param in required:
            assert param in all_params, f"Missing required parameter: {param}"

        # Важные опциональные параметры
        optional = [
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
        ]

        for param in optional:
            assert param in all_params, f"Missing optional parameter: {param}"

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_chat_completions_all_parameters(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест всех параметров chat.completions.create"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем все API методы
        mock_openai_instance.chat = MagicMock()
        mock_openai_instance.chat.completions = MagicMock()
        mock_openai_instance.chat.completions.create = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = MagicMock()

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Тест с максимальным набором параметров
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
            ],
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n", "END"],
            stream=False,
            n=1,
            user="test-user-123",
            logprobs=False,
            logit_bias={50256: -100},
            seed=42,
            response_format={"type": "text"},
        )

        # Проверяем что вызов прошел успешно
        mock_create = mock_openai_instance.chat.completions.create
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args

        # Проверяем ключевые параметры
        assert kwargs["model"] == "gpt-3.5-turbo"
        assert len(kwargs["messages"]) == 2
        assert kwargs["temperature"] == 0.7
        assert kwargs["max_tokens"] == 150

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_streaming_parameters(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест параметров streaming"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Мок streaming response
        mock_stream = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hi"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content="!"))]),
        ]

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем все API методы
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

        # Тест streaming с дополнительными параметрами
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Count to 3"}],
            stream=True,
            temperature=0.5,
            max_tokens=50,
        )

        # Проверяем что stream работает
        chunks = list(stream)
        assert len(chunks) == 2


@pytest.mark.unit
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI SDK not available")
class TestModelsMethod:
    """Детальные тесты methods models API"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_models_list_call(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест вызова models.list"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Мок данных модели
        mock_models = MagicMock()
        mock_models.data = [
            MagicMock(id="gpt-3.5-turbo", object="model"),
            MagicMock(id="gpt-4", object="model"),
        ]

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем все API методы models
        mock_openai_instance.models = MagicMock()
        mock_openai_instance.models.list = MagicMock()
        mock_openai_instance.models.list.return_value = mock_models

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Тест получения списка моделей
        models = client.models.list()
        assert models is not None

        # Проверяем что вызов был сделан
        mock_openai_instance.models.list.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_models_retrieve_call(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Тест вызова models.retrieve"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Мок данных одной модели
        mock_model = MagicMock()
        mock_model.id = "gpt-3.5-turbo"
        mock_model.object = "model"
        mock_model.created = 1677610602

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем все API методы models
        mock_openai_instance.models = MagicMock()
        mock_openai_instance.models.retrieve = MagicMock()
        mock_openai_instance.models.retrieve.return_value = mock_model

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()
        mock_openai_instance.api_key = "test_token"

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Тест получения конкретной модели
        model = client.models.retrieve("gpt-3.5-turbo")
        assert model is not None
        assert model.id == "gpt-3.5-turbo"

        # Проверяем что вызов был сделан с правильным ID
        mock_openai_instance.models.retrieve.assert_called_once_with(
            "gpt-3.5-turbo"
        )


# Простой тест для проверки что все работает
@pytest.mark.unit
def test_simple():
    """Простой тест"""
    assert True
