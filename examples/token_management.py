#!/usr/bin/env python3
"""
Примеры управления токенами Evolution OpenAI
"""

import os
import time

from evolution_openai import OpenAI

# Конфигурация
BASE_URL = os.getenv("EVOLUTION_BASE_URL", "https://your-endpoint.cloud.ru/v1")
KEY_ID = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
SECRET = os.getenv("EVOLUTION_SECRET", "your_secret")


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


def token_info_example():
    """Пример получения информации о токене"""
    print("=== Информация о токене ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        with OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL) as client:
            # Получаем информацию о текущем токене
            token_info = client.get_token_info()
            print(f"Информация о токене: {token_info}")

            # Получаем сам токен (первые 20 символов)
            current_token = client.current_token
            print(f"Текущий токен: {current_token[:20]}...")

            # Получаем доступную модель
            model_name = get_available_model(client)

            # Делаем простой запрос
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Привет!"}],
                max_tokens=16,
            )

            print(f"Ответ: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Ошибка: {e}")


def token_refresh_example():
    """Пример принудительного обновления токена"""
    print("\n=== Принудительное обновление токена ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        client = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        # Получаем текущий токен
        old_token = client.current_token
        print(f"Старый токен: {old_token[:20]}...")

        # Принудительно обновляем токен
        print("Обновляем токен...")
        new_token = client.refresh_token()
        print(f"Новый токен: {new_token[:20]}...")

        # Проверяем что токен действительно изменился
        if old_token != new_token:
            print("✅ Токен успешно обновлен")
        else:
            print("⚠️ Токен остался тем же")

        # Получаем доступную модель
        model_name = get_available_model(client)

        # Делаем запрос с новым токеном
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Тест нового токена"}],
            max_tokens=16,
        )

        print(f"Ответ с новым токеном: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Ошибка: {e}")


def automatic_token_management():
    """Демонстрация автоматического управления токенами"""
    print("\n=== Автоматическое управление токенами ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        client = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        print("Делаем серию запросов...")

        # Получаем доступную модель
        model_name = get_available_model(client)

        for i in range(3):
            print(f"\nЗапрос {i + 1}:")

            # Проверяем токен перед запросом
            token_before = client.current_token[:20]
            print(f"  Токен перед запросом: {token_before}...")

            # Делаем запрос (токен может автоматически обновиться)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": f"Это запрос номер {i + 1}"}
                ],
                max_tokens=16,
            )

            # Проверяем токен после запроса
            token_after = client.current_token[:20]
            print(f"  Токен после запроса: {token_after}...")

            if token_before != token_after:
                print("  🔄 Токен был автоматически обновлен")
            else:
                print("  ✅ Токен остался прежним")

            print(f"  Ответ: {response.choices[0].message.content}")

            # Небольшая пауза между запросами
            time.sleep(1)

    except Exception as e:
        print(f"Ошибка: {e}")


def token_expiration_simulation():
    """Симуляция истечения токена"""
    print("\n=== Симуляция истечения токена ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        client = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        print("Получаем информацию о токене...")
        token_info = client.get_token_info()
        print(f"Текущая информация: {token_info}")

        # Искусственно инвалидируем токен
        print("\nИскусственно инвалидируем текущий токен...")
        client.token_manager.invalidate_token()

        # При следующем запросе токен должен обновиться автоматически
        print("Делаем запрос (токен должен обновиться автоматически)...")

        # Получаем доступную модель
        model_name = get_available_model(client)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Тест после инвалидации токена"}
            ],
            max_tokens=16,
        )

        print(f"✅ Запрос успешен: {response.choices[0].message.content}")
        print("🔄 Токен был автоматически восстановлен")

        # Проверяем новую информацию о токене
        new_token_info = client.get_token_info()
        print(f"Новая информация о токене: {new_token_info}")

    except Exception as e:
        print(f"Ошибка: {e}")


def multiple_clients_example():
    """Пример работы с несколькими клиентами"""
    print("\n=== Несколько клиентов ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        # Создаем два клиента с одинаковыми credentials
        client1 = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        client2 = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        print("Создали два клиента...")

        # Получаем токены от обоих клиентов
        token1 = client1.current_token
        token2 = client2.current_token

        print(f"Токен клиента 1: {token1[:20]}...")
        print(f"Токен клиента 2: {token2[:20]}...")

        # Получаем доступную модель
        model_name = get_available_model(client1)

        # Делаем запросы от обоих клиентов
        response1 = client1.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Сообщение от клиента 1"}],
            max_tokens=16,
        )

        response2 = client2.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Сообщение от клиента 2"}],
            max_tokens=16,
        )

        print(f"Ответ клиенту 1: {response1.choices[0].message.content}")
        print(f"Ответ клиенту 2: {response2.choices[0].message.content}")

        # Обновляем токен у первого клиента
        print("\nОбновляем токен у первого клиента...")
        new_token1 = client1.refresh_token()
        token2_after = client2.current_token

        print(f"Новый токен клиента 1: {new_token1[:20]}...")
        print(f"Токен клиента 2: {token2_after[:20]}...")

        print("✅ Каждый клиент управляет своими токенами независимо")

    except Exception as e:
        print(f"Ошибка: {e}")


def main():
    """Основная функция"""
    print("🚀 Evolution OpenAI - Управление токенами\n")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("⚠️ Установите переменные окружения:")
        print("export EVOLUTION_KEY_ID='ваш_key_id'")
        print("export EVOLUTION_SECRET='ваш_secret'")
        print("export EVOLUTION_BASE_URL='https://your-endpoint.cloud.ru/v1'")
        return False

    try:
        token_info_example()
        token_refresh_example()
        automatic_token_management()
        token_expiration_simulation()
        multiple_clients_example()

        print("\n✅ Все примеры управления токенами выполнены!")
        print("\n💡 Ключевые особенности управления токенами:")
        print("- Токены обновляются автоматически при необходимости")
        print("- Можно принудительно обновить токен через refresh_token()")
        print("- Каждый клиент управляет своими токенами независимо")
        print("- Информацию о токенах можно получить через get_token_info()")
        print("- При ошибках авторизации токен обновляется автоматически")

        return True

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return False


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
