"""
Минимальные тесты совместимости методов
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestChatCompletionsMethodMinimal:
    """Минимальные тесты метода chat.completions.create"""

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_chat_completions_basic(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Базовый тест chat.completions.create"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем структуру API
        mock_create = MagicMock()
        mock_openai_instance.chat.completions.create = mock_create
        mock_create.return_value = MagicMock()

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()

        from evolution_openai import OpenAI

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Простой вызов
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
        )

        # Проверяем что вызов прошел
        assert result is not None
        mock_create.assert_called_once()

    @patch("evolution_openai.client.EvolutionTokenManager")
    @patch("openai.OpenAI.__new__")
    def test_models_list_basic(
        self, mock_openai_new, mock_token_manager, mock_credentials
    ):
        """Базовый тест models.list"""
        # Мокаем token manager
        mock_manager = MagicMock()
        mock_manager.get_valid_token.return_value = "test_token"
        mock_token_manager.return_value = mock_manager

        # Создаем полный мок OpenAI экземпляра
        mock_openai_instance = MagicMock()
        mock_openai_new.return_value = mock_openai_instance

        # Мокаем models API
        mock_list = MagicMock()
        mock_openai_instance.models.list = mock_list
        mock_list.return_value = MagicMock()

        # Мокаем HTTP клиент
        mock_openai_instance._client = MagicMock()

        from evolution_openai import OpenAI

        client = OpenAI(
            key_id=mock_credentials["key_id"],
            secret=mock_credentials["secret"],
            base_url=mock_credentials["base_url"],
        )

        # Простой вызов
        result = client.models.list()

        # Проверяем что вызов прошел
        assert result is not None
        mock_list.assert_called_once()


@pytest.mark.unit
def test_simple_assertion():
    """Простейший тест для проверки что файл работает"""
    assert True
