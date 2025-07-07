#!/usr/bin/env python3
"""
Примеры работы с Evolution Foundation Models
"""

import os
import time
import asyncio

from evolution_openai import OpenAI, AsyncOpenAI

# Конфигурация
BASE_URL = os.getenv("EVOLUTION_BASE_URL", "https://your-endpoint.cloud.ru/v1")
FOUNDATION_MODELS_URL = os.getenv(
    "EVOLUTION_FOUNDATION_MODELS_URL",
    "https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
)
KEY_ID = os.getenv("EVOLUTION_KEY_ID", "your_key_id")
SECRET = os.getenv("EVOLUTION_SECRET", "your_secret")
PROJECT_ID = os.getenv("EVOLUTION_PROJECT_ID")

# Выбираем Foundation Models endpoint если доступен
ENDPOINT_URL = FOUNDATION_MODELS_URL if FOUNDATION_MODELS_URL else BASE_URL
DEFAULT_MODEL = "RefalMachine/RuadaptQwen2.5-7B-Lite-Beta"


def get_foundation_model():
    """Возвращает модель для Foundation Models"""
    print(f"🔧 Используем модель: {DEFAULT_MODEL}")
    return DEFAULT_MODEL


async def get_foundation_model_async():
    """Возвращает модель для Foundation Models (асинхронно)"""
    print(f"🔧 Используем модель: {DEFAULT_MODEL}")
    return DEFAULT_MODEL


def basic_foundation_models_example():
    """Базовый пример Foundation Models"""
    print("=== Базовый Foundation Models ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для работы с Foundation Models")
        return None

    try:
        with OpenAI(
            key_id=KEY_ID,
            secret=SECRET,
            base_url=ENDPOINT_URL,
            project_id=PROJECT_ID,
        ) as client:
            model_name = get_foundation_model()

            response = client.chat.completions.create(
                model=model_name,
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
                max_tokens=50,
                temperature=0.7,
            )

            if (
                response.choices
                and len(response.choices) > 0
                and response.choices[0].message
            ):
                content = (
                    response.choices[0].message.content
                    or "Нет содержимого в ответе"
                )
                print(f"✅ Ответ: {content}")
                print(f"📊 Модель: {response.model}")
                print(f"🔢 Токенов: {response.usage.total_tokens}")
                return True
            else:
                print("❌ Получен пустой ответ")
                return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def streaming_foundation_models_example():
    """Пример streaming с Foundation Models"""
    print("\n=== Streaming Foundation Models ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для streaming")
        return None

    try:
        with OpenAI(
            key_id=KEY_ID,
            secret=SECRET,
            base_url=ENDPOINT_URL,
            project_id=PROJECT_ID,
        ) as client:
            model_name = get_foundation_model()

            print("Генерируем стихотворение...")
            print("-" * 50)

            stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Напиши короткое стихотворение про технологии",
                    }
                ],
                stream=True,
                max_tokens=80,
                temperature=0.8,
            )

            content_parts = []
            for chunk in stream:
                if (
                    chunk.choices
                    and len(chunk.choices) > 0
                    and chunk.choices[0].delta
                    and chunk.choices[0].delta.content
                ):
                    content = chunk.choices[0].delta.content
                    content_parts.append(content)
                    print(content, end="", flush=True)

            print("\n" + "-" * 50)
            print(
                f"✅ Streaming завершен! Получено {len(content_parts)} частей."
            )
            return True

    except Exception as e:
        print(f"❌ Streaming ошибка: {e}")
        return False


async def async_foundation_models_example():
    """Асинхронный пример Foundation Models"""
    print("\n=== Асинхронный Foundation Models ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для async примера")
        return None

    try:
        async with AsyncOpenAI(
            key_id=KEY_ID,
            secret=SECRET,
            base_url=ENDPOINT_URL,
            project_id=PROJECT_ID,
        ) as client:
            model_name = await get_foundation_model_async()

            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Объясни простыми словами, что такое машинное обучение",
                    }
                ],
                max_tokens=60,
                temperature=0.5,
            )

            if (
                response.choices
                and len(response.choices) > 0
                and response.choices[0].message
            ):
                content = (
                    response.choices[0].message.content
                    or "Нет содержимого в ответе"
                )
                print(f"✅ Async ответ: {content}")
                print(f"📊 Модель: {response.model}")
                print(f"🔢 Токенов: {response.usage.total_tokens}")
                return True
            else:
                print("❌ Получен пустой ответ")
                return False

    except Exception as e:
        print(f"❌ Async ошибка: {e}")
        return False


def advanced_foundation_models_example():
    """Пример с дополнительными опциями Foundation Models"""
    print("\n=== Foundation Models с опциями ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для advanced примера")
        return None

    try:
        with OpenAI(
            key_id=KEY_ID,
            secret=SECRET,
            base_url=ENDPOINT_URL,
            project_id=PROJECT_ID,
        ) as client:
            model_name = get_foundation_model()

            # Используем with_options для настройки параметров
            response = client.with_options(
                timeout=60.0, max_retries=3
            ).chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Создай план изучения Python для начинающих",
                    }
                ],
                max_tokens=80,
                temperature=0.3,
            )

            if (
                response.choices
                and len(response.choices) > 0
                and response.choices[0].message
            ):
                content = (
                    response.choices[0].message.content
                    or "Нет содержимого в ответе"
                )
                print(f"✅ Ответ с опциями: {content}")
                print(f"📊 Модель: {response.model}")
                print(f"🔢 Токенов: {response.usage.total_tokens}")

                # Информация о токене
                token_info = client.get_token_info()
                print(f"🔑 Статус токена: {token_info}")
                return True
            else:
                print("❌ Получен пустой ответ")
                return False

    except Exception as e:
        print(f"❌ Ошибка с опциями: {e}")
        return False


async def parallel_foundation_models_example():
    """Пример параллельных запросов к Foundation Models"""
    print("\n=== Параллельные запросы Foundation Models ===")

    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("Установите переменные окружения для параллельных запросов")
        return None

    try:
        async with AsyncOpenAI(
            key_id=KEY_ID,
            secret=SECRET,
            base_url=ENDPOINT_URL,
            project_id=PROJECT_ID,
        ) as client:
            model_name = await get_foundation_model_async()

            # Список вопросов для параллельной обработки
            questions = [
                "Что такое искусственный интеллект?",
                "Как работает машинное обучение?",
                "Что такое нейронные сети?",
            ]

            # Создаем задачи для параллельного выполнения
            tasks = []
            for question in questions:
                task = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "Дай краткий ответ в 1-2 предложения.",
                        },
                        {"role": "user", "content": question},
                    ],
                    max_tokens=50,
                    temperature=0.5,
                )
                tasks.append(task)

            # Выполняем все запросы параллельно
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()

            elapsed = end_time - start_time
            print(
                f"⚡ Обработано {len(questions)} запросов за {elapsed:.2f} секунд"
            )
            print()

            for i, (question, response) in enumerate(
                zip(questions, responses)
            ):
                print(f"❓ Вопрос {i + 1}: {question}")
                if (
                    response.choices
                    and len(response.choices) > 0
                    and response.choices[0].message
                ):
                    content = (
                        response.choices[0].message.content
                        or "Нет содержимого в ответе"
                    )
                    print(f"✅ Ответ: {content}")
                    print(f"🔢 Токенов: {response.usage.total_tokens}")
                else:
                    print("❌ Получен пустой ответ")
                print("-" * 50)

            return True

    except Exception as e:
        print(f"❌ Ошибка параллельных запросов: {e}")
        return False


def main():
    """Основная функция с примерами Foundation Models"""
    print("🚀 Evolution Foundation Models - Примеры использования\n")
    print(f"🌐 Endpoint: {ENDPOINT_URL}")
    print(f"🤖 Модель: {DEFAULT_MODEL}")

    # Показываем, используются ли Foundation Models
    is_foundation_models = (
        "foundation-models" in ENDPOINT_URL or "gigacube" in ENDPOINT_URL
    )
    print(f"🔧 Используется Foundation Models: {is_foundation_models}\n")

    # Проверяем переменные окружения
    if KEY_ID == "your_key_id" or SECRET == "your_secret":
        print("⚠️ ВНИМАНИЕ: Не установлены переменные окружения!")
        print(
            "Установите переменные окружения для работы с Foundation Models:"
        )
        print("export EVOLUTION_KEY_ID='your_key_id'")
        print("export EVOLUTION_SECRET='your_secret'")
        print("export EVOLUTION_PROJECT_ID='your_project_id'")
        print(
            "export EVOLUTION_FOUNDATION_MODELS_URL='https://foundation-models.api.cloud.ru/api/gigacube/openai/v1'"
        )
        print("\n💡 Примеры будут запущены в демонстрационном режиме")
        print()

    # Запускаем примеры
    results = []

    # Синхронные примеры
    results.append(basic_foundation_models_example())
    results.append(streaming_foundation_models_example())
    results.append(advanced_foundation_models_example())

    # Асинхронные примеры
    async def run_async_examples():
        async_results = []
        async_results.append(await async_foundation_models_example())
        async_results.append(await parallel_foundation_models_example())
        return async_results

    # Запускаем асинхронные примеры
    async_results = asyncio.run(run_async_examples())
    results.extend(async_results)

    # Подводим итоги
    successful = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print("\n📊 Результаты выполнения:")
    print(f"✅ Успешно: {successful}")
    print(f"❌ Ошибки: {failed}")
    print(f"⏭️ Пропущено: {skipped}")

    if failed == 0 and successful > 0:
        print("\n🎉 Все примеры Foundation Models выполнены успешно!")
    elif failed > 0:
        print(f"\n⚠️ {failed} примеров завершились с ошибками")

    print("\n💡 Подсказки:")
    print("- Убедитесь, что PROJECT_ID установлен для Foundation Models")
    print("- Проверьте доступность Foundation Models endpoint")
    print(
        "- Используйте EVOLUTION_FOUNDATION_MODELS_URL для специального endpoint"
    )
    print("- Документация: docs/foundation_models.md")

    return failed == 0


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
