#!/usr/bin/env python3
"""
Запуск всех примеров Evolution OpenAI
"""

import os
import sys
import subprocess
from pathlib import Path

# Загружаем переменные окружения из файла .env если он существует
try:
    from dotenv import load_dotenv  # type: ignore

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Переменные окружения загружены из {env_file}")
    else:
        print(
            "ℹ️ Файл .env не найден, используются системные переменные окружения"
        )
except ImportError:
    print(
        "⚠️ python-dotenv недоступен, используются только системные переменные окружения"
    )

# Добавляем путь к родительской директории для импорта
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))


def run_example(script_name: str, description: str) -> bool:
    """Запускает пример и отображает результат"""
    print(f"\n{'=' * 60}")
    print(f"🔧 {description}")
    print(f"Файл: {script_name}")
    print("=" * 60)

    script_path = current_dir / script_name
    if not script_path.exists():
        print(f"❌ Файл {script_name} не найден")
        return False

    try:
        # Запуск примера (увеличенный таймаут для Foundation Models)
        timeout_seconds = (
            60 if script_name == "foundation_models_example.py" else 30
        )
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"⚠️ Предупреждения/ошибки:\n{result.stderr}")

        # Проверяем на реальные API ошибки в выводе
        has_api_errors = any(
            error_pattern in result.stdout
            for error_pattern in [
                "Error code: 404",
                "Error code: 401",
                "Error code: 403",
                "Error code: 500",
                "ConnectionError",
                "TimeoutError",
            ]
        )

        # Проверяем на отсутствие переменных окружения (это ожидаемо)
        has_env_issues = any(
            env_pattern in result.stdout
            for env_pattern in [
                "Установите переменные окружения",
                "your_key_id",
                "your_secret",
                "key_id и secret обязательны",
            ]
        )

        if result.returncode == 0:
            if has_api_errors and not has_env_issues:
                print(f"⚠️ {script_name} выполнен с API ошибками")
                return False
            else:
                print(f"✅ {script_name} выполнен успешно")
                return True
        else:
            print(
                f"❌ {script_name} завершился с ошибкой (код: {result.returncode})"
            )
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ {script_name} прерван по таймауту")
        return False
    except Exception as e:
        print(f"💥 Ошибка при запуске {script_name}: {e}")
        return False


def main() -> bool:
    """Главная функция"""
    print("🚀 Evolution OpenAI - Запуск всех примеров")
    print("=" * 60)

    # Проверяем переменные окружения
    required_vars = [
        "EVOLUTION_KEY_ID",
        "EVOLUTION_SECRET",
        "EVOLUTION_BASE_URL",
    ]

    # Проверяем опциональные переменные для Foundation Models
    optional_vars = [
        "EVOLUTION_FOUNDATION_MODELS_URL",
        "EVOLUTION_PROJECT_ID",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("\n⚠️ ВНИМАНИЕ: Отсутствуют переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nПримеры будут запущены в демонстрационном режиме")
        print("Для полного тестирования установите:")
        print("export EVOLUTION_KEY_ID='your_key_id'")
        print("export EVOLUTION_SECRET='your_secret'")
        print("export EVOLUTION_BASE_URL='https://your-endpoint.cloud.ru/v1'")
    else:
        print("\n✅ Все необходимые переменные окружения установлены")
        print("Примеры будут работать с реальным API")

        # Показываем статус опциональных переменных
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            print(
                f"ℹ️ Опциональные переменные не установлены: {', '.join(missing_optional)}"
            )
            print(
                "Foundation Models примеры будут использовать значения по умолчанию"
            )

    # Список примеров для запуска
    examples = [
        ("basic_usage.py", "Базовые примеры использования"),
        ("streaming_examples.py", "Примеры Streaming API"),
        ("token_management.py", "Управление токенами"),
        ("async_examples.py", "Асинхронные примеры"),
        ("foundation_models_example.py", "Примеры Foundation Models"),
    ]

    # Статистика
    successful = 0
    total = len(examples)

    # Запускаем каждый пример
    for script_name, description in examples:
        success = run_example(script_name, description)
        if success:
            successful += 1

    # Итоги
    print(f"\n{'=' * 60}")
    print("📊 ИТОГИ ВЫПОЛНЕНИЯ")
    print(f"✅ Успешно: {successful}/{total}")
    print(f"❌ С ошибками: {total - successful}/{total}")

    if successful == total:
        print("\n🎉 Все примеры выполнены успешно!")
    else:
        print(f"\n⚠️ {total - successful} примеров завершились с ошибками")

    print("\n💡 Дополнительная информация:")
    print("- Файлы примеров находятся в директории examples/")
    print("- Документация: docs/README.md")
    print("- Для реального тестирования установите переменные окружения")

    return successful == total


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
