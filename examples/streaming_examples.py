#!/usr/bin/env python3
"""
Примеры работы со Streaming API Evolution OpenAI
"""

import os
import time
import asyncio

from evolution_openai import OpenAI, AsyncOpenAI

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


def basic_streaming_example():
    """Базовый пример streaming"""
    print("=== Базовый Streaming ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        with OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL) as client:
            # Получаем доступную модель
            model_name = get_available_model(client)

            print("Вопрос: Расскажи историю про космонавта")
            print("Ответ: ", end="", flush=True)

            stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Расскажи короткую историю про космонавта",
                    }
                ],
                stream=True,
                max_tokens=16,
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content

            print("\n")
            response_length = len(full_response)
            preview = full_response[:100]
            print(f"Полный ответ ({response_length} символов): {preview}...")

    except Exception as e:
        print(f"Ошибка: {e}")


def streaming_with_metadata():
    """Streaming с отображением метаданных"""
    print("\n=== Streaming с метаданными ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        with OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL) as client:
            # Получаем доступную модель
            model_name = get_available_model(client)

            print("Генерируем стихотворение...")
            print("-" * 50)

            stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты поэт. Пиши красивые стихи.",
                    },
                    {
                        "role": "user",
                        "content": "Напиши короткое стихотворение про весну",
                    },
                ],
                stream=True,
                max_tokens=16,
                temperature=0.8,
            )

            chunk_count = 0
            total_content = ""
            start_time = time.time()

            for chunk in stream:
                chunk_count += 1

                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    total_content += content
                    print(content, end="", flush=True)

            end_time = time.time()
            generation_time = end_time - start_time

            print("\n" + "-" * 50)
            print("Статистика:")
            print(f"• Получено чанков: {chunk_count}")
            print(f"• Время генерации: {generation_time:.2f} сек")
            print(f"• Длина ответа: {len(total_content)} символов")
            chars_per_sec = len(total_content) / generation_time
            print(f"• Скорость: {chars_per_sec:.1f} симв/сек")

    except Exception as e:
        print(f"Ошибка: {e}")


async def async_streaming_example():
    """Асинхронный streaming"""
    print("\n=== Асинхронный Streaming ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        async with AsyncOpenAI(
            key_id=KEY_ID, secret=SECRET, base_url=BASE_URL
        ) as client:
            # Получаем доступную модель
            model_name = await get_available_model_async(client)

            print("Асинхронная генерация рассказа...")
            print("=" * 60)

            stream = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты писатель фантастических рассказов.",
                    },
                    {
                        "role": "user",
                        "content": "Напиши начало рассказа про время",
                    },
                ],
                stream=True,
                max_tokens=16,
            )

            words_count = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    words_count += len(content.split())

                    # Добавляем небольшую задержку для эффекта печатной машинки
                    await asyncio.sleep(0.05)

            print("\n" + "=" * 60)
            print(f"Приблизительно слов: {words_count}")

    except Exception as e:
        print(f"Ошибка: {e}")


def streaming_with_stop_sequence():
    """Streaming с использованием stop sequences"""
    print("\n=== Streaming с остановочными последовательностями ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    try:
        client = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        # Получаем доступную модель
        model_name = get_available_model(client)

        print("Генерируем список до ключевого слова 'КОНЕЦ'...")
        print()

        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Создавай нумерованный список советов. "
                        "Заканчивай словом 'КОНЕЦ'."
                    ),
                },
                {
                    "role": "user",
                    "content": "Дай 5 советов для изучения программирования",
                },
            ],
            stream=True,
            max_tokens=16,
            stop=["КОНЕЦ", "конец"],
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

            # Проверяем причину остановки
            if chunk.choices[0].finish_reason:
                reason = chunk.choices[0].finish_reason
                print(f"\n[Причина остановки: {reason}]")

        print()

    except Exception as e:
        print(f"Ошибка: {e}")


def multiple_streaming_conversations():
    """Множественные streaming диалоги"""
    print("\n=== Множественные Streaming диалоги ===\n")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения")
        return

    conversations = [
        {
            "name": "Математик",
            "system": "Ты математик. Объясняй сложные концепции простыми словами.",
            "question": "Объясни теорему Пифагора простыми словами",
        },
        {
            "name": "Историк",
            "system": "Ты историк. Рассказывай о важных исторических событиях.",
            "question": "Расскажи кратко о падении Берлинской стены",
        },
    ]

    try:
        client = OpenAI(key_id=KEY_ID, secret=SECRET, base_url=BASE_URL)

        # Получаем доступную модель
        model_name = get_available_model(client)

        for i, conv in enumerate(conversations, 1):
            print(f"{i}. Беседа с {conv['name']}:")
            print(f"Вопрос: {conv['question']}")
            print("Ответ: ", end="", flush=True)

            try:
                stream = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": conv["system"]},
                        {"role": "user", "content": conv["question"]},
                    ],
                    stream=True,
                    max_tokens=16,
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        print(
                            chunk.choices[0].delta.content, end="", flush=True
                        )

                print("\n")

            except Exception as e:
                print(f"Ошибка: {e}")

            print("-" * 60)

    except Exception as e:
        print(f"Общая ошибка: {e}")


def main():
    """Главная функция"""
    print("🚀 Evolution OpenAI - Примеры Streaming\n")

    basic_streaming_example()
    streaming_with_metadata()

    # Асинхронный пример
    print("\nЗапускаем асинхронный пример...")
    asyncio.run(async_streaming_example())

    streaming_with_stop_sequence()
    multiple_streaming_conversations()

    print("\n✅ Все примеры streaming выполнены!")
    print("\n💡 Советы по Streaming:")
    print("- Используйте stream=True в параметрах запроса")
    print("- Обрабатывайте каждый chunk по мере поступления")
    print("- Проверяйте finish_reason для контроля остановки")
    print("- Применяйте stop sequences для точного контроля")
    print("- В async коде используйте 'async for chunk in stream'")


if __name__ == "__main__":
    main()
