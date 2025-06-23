#!/usr/bin/env python3
"""
Примеры асинхронного использования Evolution OpenAI
"""

import os
import asyncio
from typing import Any, Dict

from evolution_openai import AsyncOpenAI

# Конфигурация
BASE_URL = os.getenv("EVOLUTION_BASE_URL", "https://your-endpoint.cloud.ru/v1")
KEY_ID = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
SECRET = os.getenv("EVOLUTION_SECRET", "your_secret")


async def get_available_model_async(client):
    """Получает первую доступную модель из API (асинхронно)"""
    try:
        models = await client.models.list()
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


async def basic_async_example():
    """Базовый пример асинхронного запроса"""
    print("=== Базовый асинхронный запрос ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для работы примеров")
        return

    try:
        async with AsyncOpenAI(
            key_id=KEY_ID, secret=SECRET, base_url=BASE_URL
        ) as client:
            # Получаем доступную модель
            model_name = await get_available_model_async(client)

            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Ты полезный помощник."},
                    {
                        "role": "user",
                        "content": "Что такое асинхронное программирование?",
                    },
                ],
                max_tokens=16,
            )

            print(f"Ответ: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Ошибка: {e}")


async def parallel_requests_example():
    """Пример параллельных запросов"""
    print("\n=== Параллельные запросы ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для параллельных запросов")
        return

    try:
        async with AsyncOpenAI(
            key_id=KEY_ID, secret=SECRET, base_url=BASE_URL
        ) as client:
            # Получаем доступную модель
            model_name = await get_available_model_async(client)

            # Список вопросов для параллельной обработки
            questions = [
                "Что такое Python?",
                "Что такое искусственный интеллект?",
                "Как работает машинное обучение?",
                "Что такое нейронные сети?",
            ]

            # Создаем задачи для параллельного выполнения
            tasks = []
            for _, question in enumerate(questions):
                task = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "Дай короткий ответ в 1-2 предложения.",
                        },
                        {"role": "user", "content": question},
                    ],
                    max_tokens=16,
                )
                tasks.append(task)

            # Выполняем все запросы параллельно
            import time

            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()

            elapsed = end_time - start_time
            print(
                f"Обработано {len(questions)} запросов за {elapsed:.2f} секунд"
            )
            print()

            for i, (question, response) in enumerate(
                zip(questions, responses)
            ):
                print(f"Вопрос {i + 1}: {question}")
                print(f"Ответ: {response.choices[0].message.content}")
                print("-" * 50)

    except Exception as e:
        print(f"Ошибка параллельных запросов: {e}")


async def streaming_async_example():
    """Пример асинхронного streaming"""
    print("\n=== Асинхронный Streaming ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для streaming")
        return

    try:
        client = AsyncOpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        # Получаем доступную модель
        model_name = await get_available_model_async(client)

        print("Streaming ответ:")

        stream = await client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Расскажи интересную историю про программиста",
                }
            ],
            stream=True,
            max_tokens=16,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

        print("\n")
        await client.close()

    except Exception as e:
        print(f"Ошибка streaming: {e}")


async def context_manager_example():
    """Пример использования async context manager"""
    print("\n=== Context Manager ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для context manager")
        return

    try:
        # Используем async with для автоматического закрытия
        async with AsyncOpenAI(
            key_id=KEY_ID, secret=SECRET, base_url=BASE_URL
        ) as client:
            # Получаем доступную модель
            model_name = await get_available_model_async(client)

            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Объясни преимущества использования async/await",
                    }
                ],
                max_tokens=16,
            )

            content = response.choices[0].message.content
            print(f"Ответ через context manager: {content}")

        # Клиент автоматически закрыт после выхода из блока with

    except Exception as e:
        print(f"Ошибка context manager: {e}")


async def error_handling_example():
    """Пример обработки ошибок в асинхронном коде"""
    print("\n=== Обработка ошибок ===")

    try:
        client = AsyncOpenAI(
            key_id=KEY_ID,
            secret=SECRET,
            base_url=BASE_URL,
            timeout=5.0,  # Короткий timeout для демонстрации ошибок
        )

        # Получаем доступную модель
        model_name = await get_available_model_async(client)

        # Попытка запроса с разумным количеством токенов
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Привет!"}],
            max_tokens=16,  # Используем стандартное ограничение
        )

        print(f"Ответ: {response.choices[0].message.content}")
        await client.close()

    except asyncio.TimeoutError:
        print("Ошибка: Превышено время ожидания")
    except Exception as e:
        print(f"Другая ошибка: {e}")


async def batch_processing_example():
    """Пример пакетной обработки с ограничением concurrency"""
    print("\n=== Пакетная обработка ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для пакетной обработки")
        return

    try:
        # Семафор для ограничения количества одновременных запросов
        semaphore = asyncio.Semaphore(3)  # Максимум 3 одновременных запроса

        client = AsyncOpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        # Получаем доступную модель
        model_name = await get_available_model_async(client)

        async def process_single_request(
            text: str, index: int
        ) -> Dict[str, Any]:
            """Обрабатывает один запрос с семафором"""
            async with semaphore:
                print(f"Обрабатываем запрос {index}: {text[:30]}...")

                response = await client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "Определи настроение текста (положительное, отрицательное, нейтральное).",
                        },
                        {"role": "user", "content": f"Текст: {text}"},
                    ],
                    max_tokens=16,
                )

                return {
                    "index": index,
                    "text": text,
                    "sentiment": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens
                    if response.usage
                    else 0,
                }

        # Тестовые тексты для анализа настроений
        texts = [
            "Сегодня прекрасный день!",
            "Мне очень грустно...",
            "Это нормальный рабочий день.",
            "Я очень рад этой новости!",
            "Ситуация меня расстраивает.",
            "Все идет по плану.",
        ]

        # Обрабатываем все тексты параллельно с ограничением
        tasks = [
            process_single_request(text, i) for i, text in enumerate(texts)
        ]
        results = await asyncio.gather(*tasks)

        # Выводим результаты
        print("\nРезультаты анализа настроений:")
        total_tokens = 0
        for result in results:
            print(
                f"{result['index'] + 1}. '{result['text']}' -> {result['sentiment']}"
            )
            total_tokens += result["tokens"]

        print(f"\nВсего использовано токенов: {total_tokens}")

        await client.close()

    except Exception as e:
        print(f"Ошибка пакетной обработки: {e}")


async def main():
    """Основная асинхронная функция"""
    print("🚀 Evolution OpenAI - Асинхронные примеры\n")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("⚠️ Установите переменные окружения:")
        print("export EVOLUTION_KEY_ID='ваш_key_id'")
        print("export EVOLUTION_SECRET='ваш_secret'")
        print("export EVOLUTION_BASE_URL='https://your-endpoint.cloud.ru/v1'")
        return False

    try:
        await basic_async_example()
        await parallel_requests_example()
        await streaming_async_example()
        await context_manager_example()
        await error_handling_example()
        await batch_processing_example()

        print("\n✅ Все асинхронные примеры выполнены!")
        print("\n💡 Подсказки:")
        print("- Используйте async/await для неблокирующих операций")
        print("- Применяйте asyncio.gather() для параллельных запросов")
        print("- Не забывайте закрывать клиенты или используйте async with")
        print("- Ограничивайте concurrency с помощью семафоров")

        return True

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return False


if __name__ == "__main__":
    import sys

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
