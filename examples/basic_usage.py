#!/usr/bin/env python3
"""
Базовые примеры использования Evolution OpenAI
"""

import os

from evolution_openai import OpenAI, create_client

# Cloud.ru модель endpoint (замените на ваш)
BASE_URL = os.getenv("EVOLUTION_BASE_URL", "https://your-endpoint.cloud.ru/v1")


def check_credentials():
    """Проверяет наличие учетных данных"""
    key_id = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
    secret = os.getenv("EVOLUTION_SECRET", "your_secret")

    if (
        key_id == "your_key_id"
        or secret == "your_secret"
        or not key_id
        or not secret
    ):
        return None, None
    return key_id, secret


def get_available_model(client):
    """Получает первую доступную модель из API"""
    try:
        models = client.models.list()
        if models and models.data and len(models.data) > 0:
            model_name = models.data[0].id
            print(f"🔧 Используем модель: {model_name}")
            return model_name
        else:
            print("⚠️ Нет доступных моделей в /v1/models, используем 'default'")
            return "default"
    except Exception as e:
        print(f"⚠️ Ошибка получения моделей ({e}), используем 'default'")
        return "default"


def basic_chat_example():
    """Базовый пример Chat Completions"""
    print("=== Базовый Chat Completions ===\n")

    key_id, secret = check_credentials()
    if not key_id or not secret:
        print("Установите переменные окружения:")
        print("export EVOLUTION_KEY_ID='ваш_key_id'")
        print("export EVOLUTION_SECRET='ваш_secret'")
        return None  # Пропускаем, это не ошибка

    try:
        # Создаем client с использованием контекстного менеджера
        with OpenAI(key_id=key_id, secret=secret, base_url=BASE_URL) as client:
            # Получаем доступную модель
            model_name = get_available_model(client)

            # Простой запрос
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant.",
                    },
                    {
                        "role": "user",
                        "content": "Что такое искусственный интеллект?",
                    },
                ],
                max_tokens=16,
            )

            print(f"Ответ: {response.choices[0].message.content}")
            print(f"Модель: {response.model}")
            print(f"Токенов использовано: {response.usage.total_tokens}")
            return True

    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def streaming_example():
    """Пример Streaming ответов"""
    print("\n=== Streaming Example ===\n")

    key_id = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
    secret = os.getenv("EVOLUTION_SECRET", "your_secret")

    if key_id == "your_key_id" or secret == "your_secret":
        print("Установите переменные окружения для streaming")
        return None

    try:
        with OpenAI(key_id=key_id, secret=secret, base_url=BASE_URL) as client:
            # Получаем доступную модель
            model_name = get_available_model(client)

            print("Streaming ответ:")
            stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Расскажи короткую историю про робота",
                    }
                ],
                stream=True,
                max_tokens=16,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print("\n")
            return True

    except Exception as e:
        print(f"Streaming ошибка: {e}")
        return False


def helper_function_example():
    """Пример использования helper функций"""
    print("\n=== Helper Functions Example ===\n")

    key_id = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
    secret = os.getenv("EVOLUTION_SECRET", "your_secret")

    if key_id == "your_key_id" or secret == "your_secret":
        print("Установите переменные окружения для helper функций")
        return None

    try:
        # Используем create_client helper с контекстным менеджером
        with create_client(
            key_id=key_id,
            secret=secret,
            base_url=BASE_URL,
            timeout=30.0,
            max_retries=3,
        ) as client:
            # Получаем доступную модель
            model_name = get_available_model(client)

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Привет! Как дела?"}],
                max_tokens=16,
            )

            print(
                f"Helper client ответ: {response.choices[0].message.content}"
            )

            # Информация о токене
            token_info = client.get_token_info()
            print(f"Статус токена: {token_info}")
            return True

    except Exception as e:
        print(f"Helper ошибка: {e}")
        return False


def advanced_features_example():
    """Пример продвинутых возможностей"""
    print("\n=== Advanced Features Example ===\n")

    key_id = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
    secret = os.getenv("EVOLUTION_SECRET", "your_secret")

    if key_id == "your_key_id" or secret == "your_secret":
        print("Установите переменные окружения для advanced примеров")
        return None

    try:
        with OpenAI(key_id=key_id, secret=secret, base_url=BASE_URL) as client:
            # Получаем доступную модель
            model_name = get_available_model(client)

            # Per-request options
            print("1. Per-request options:")
            response = client.with_options(
                timeout=60.0
            ).chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Quick test"}],
                max_tokens=16,
            )
            print(f"   Ответ: {response.choices[0].message.content}")

            # Raw response
            print("\n2. Raw response access:")
            raw_response = client.chat.completions.with_raw_response.create(
                model=model_name,
                messages=[{"role": "user", "content": "Raw test"}],
                max_tokens=16,
            )
            print(f"   Status: {raw_response.status_code}")
            parsed = raw_response.parse()
            print(f"   Content: {parsed.choices[0].message.content}")

            # Token management
            print("\n3. Token management:")
            current_token = client.current_token
            print(f"   Текущий токен: {current_token[:20]}...")

            # Refresh token
            new_token = client.refresh_token()
            print(f"   Обновленный токен: {new_token[:20]}...")
            return True

    except Exception as e:
        print(f"Advanced ошибка: {e}")
        return False


def main():
    """Основная функция с примерами"""
    print("🚀 Evolution OpenAI - Примеры использования\n")

    results = []
    results.append(basic_chat_example())
    results.append(streaming_example())
    results.append(helper_function_example())
    results.append(advanced_features_example())

    # Проверяем результаты
    success_count = sum(1 for r in results if r is True)
    total_count = len([r for r in results if r is not None])

    print("\n✅ Все примеры выполнены!")
    print("\n💡 Подсказки:")
    print("- Установите переменные окружения для тестирования")
    print("- Замените BASE_URL на ваш endpoint")
    print("- Проверьте документацию для дополнительных возможностей")

    # Возвращаем False если были реальные ошибки API
    if total_count > 0 and success_count < total_count:
        return False
    return True


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
