# Evolution OpenAI
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/evolution-openai.svg)](https://badge.fury.io/py/evolution-openai)
[![Coverage](https://cloud-ru-tech.github.io/evolution-openai-python/badges/coverage.svg)](https://github.com/cloud-ru-tech/evolution-openai-python/actions)

**Полностью совместимый** Evolution OpenAI client с автоматическим управлением токенами. Просто замените `OpenAI` на `EvolutionOpenAI` и все будет работать!

## 🎯 Особенности

- ✅ **100% совместимость** с официальным OpenAI Python SDK
- ✅ **Автоматическое управление токенами** Cloud.ru
- ✅ **Drop-in replacement** - минимальные изменения в коде
- ✅ **Async/await поддержка** с `AsyncOpenAI`
- ✅ **Streaming responses** поддержка
- ✅ **Thread-safe** token management
- ✅ **Автоматическое обновление** токенов за 30 секунд до истечения
- ✅ **Retry логика** при ошибках авторизации
- ✅ **Поддержка .env файлов** для управления конфигурацией
- ✅ **Интеграционные тесты** с реальным API
- ✅ **Evolution Foundation Models** поддержка с `project_id`
- ✅ **Готовые примеры** для Foundation Models
- ✅ **Передовые AI модели** включая DeepSeek-R1, Qwen2.5 и другие

## 📦 Установка

```bash
pip install evolution-openai
```

## ⚡ Быстрый старт

### Миграция с OpenAI SDK

```python
# ❌ БЫЛО (OpenAI SDK)
from openai import OpenAI

client = OpenAI(api_key="sk-...")

# ✅ СТАЛО (Evolution OpenAI)
from evolution_openai import OpenAI

# Для обычного использования
client = OpenAI(
    key_id="your_key_id", 
    secret="your_secret", 
    base_url="https://your-model-endpoint.cloud.ru/v1"
)

# Для Evolution Foundation Models
client = OpenAI(
    key_id="your_key_id", 
    secret="your_secret", 
    base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
    project_id="your_project_id"  # Для Evolution Foundation Models
)

# Все остальное работает ТОЧНО ТАК ЖЕ!
response = client.chat.completions.create(
    model="default",  # или "deepseek-ai/DeepSeek-R1-Distill-Llama-70B" для Foundation Models
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Основное использование

#### Обычное использование

```python
from evolution_openai import OpenAI

# Инициализация client для обычного использования
client = OpenAI(
    key_id="your_key_id", 
    secret="your_secret", 
    base_url="https://your-model-endpoint.cloud.ru/v1"
)

# Chat Completions
response = client.chat.completions.create(
    model="default",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is artificial intelligence?"},
    ],
    max_tokens=150,
)

print(response.choices[0].message.content)
```

#### 🚀 Evolution Foundation Models

Библиотека полностью поддерживает **Evolution Foundation Models** - платформу для работы с передовыми AI моделями на Cloud.ru. Ключевые возможности:

- **Автоматическое управление Project ID** - добавляет заголовок `x-project-id` автоматически
- **Передовые модели** - DeepSeek-R1, Qwen2.5, RefalMachine/RuadaptQwen2.5-7B-Lite-Beta
- **Специальный endpoint** - `https://foundation-models.api.cloud.ru/api/gigacube/openai/v1`
- **Полная совместимость** с OpenAI SDK - все методы работают идентично

```python
from evolution_openai import OpenAI

# Инициализация для Evolution Foundation Models
client = OpenAI(
    key_id="your_key_id",
    secret="your_secret", 
    base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
    project_id="your_project_id"  # Автоматически добавляется в заголовки
)

# Использование Foundation Models
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is artificial intelligence?"},
    ],
    max_tokens=150
)

print(response.choices[0].message.content)
```

### Streaming

```python
# Для обычного использования
stream = client.chat.completions.create(
    model="default", 
    messages=[{"role": "user", "content": "Tell me a story"}], 
    stream=True
)

# Для Foundation Models
stream = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B", 
    messages=[{"role": "user", "content": "Tell me a story"}], 
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Async/Await

```python
import asyncio
from evolution_openai import AsyncOpenAI


async def main():
    # Для обычного использования
    client = AsyncOpenAI(
        key_id="your_key_id",
        secret="your_secret",
        base_url="https://your-model-endpoint.cloud.ru/v1",
    )

    # Для Foundation Models
    client = AsyncOpenAI(
        key_id="your_key_id",
        secret="your_secret",
        base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
        project_id="your_project_id",  # Опционально для Foundation Models
    )

    response = await client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",  # или "default" для обычного использования
        messages=[{"role": "user", "content": "Async hello!"}]
    )

    print(response.choices[0].message.content)


asyncio.run(main())
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне вашего проекта:

```bash
# Скопируйте из env.example и заполните
cp env.example .env
```

#### Для обычного использования:

```bash
# .env файл
EVOLUTION_KEY_ID=your_key_id_here
EVOLUTION_SECRET=your_secret_here
EVOLUTION_BASE_URL=https://your-model-endpoint.cloud.ru/v1
EVOLUTION_TOKEN_URL=https://iam.api.cloud.ru/api/v1/auth/token
ENABLE_INTEGRATION_TESTS=false
LOG_LEVEL=INFO
```

#### Для Evolution Foundation Models:

```bash
# .env файл для Foundation Models
EVOLUTION_KEY_ID=your_key_id_here
EVOLUTION_SECRET=your_secret_here
EVOLUTION_BASE_URL=https://foundation-models.api.cloud.ru/api/gigacube/openai/v1
EVOLUTION_PROJECT_ID=your_project_id_here  # Обязательно для Foundation Models
EVOLUTION_TOKEN_URL=https://iam.api.cloud.ru/api/v1/auth/token
ENABLE_INTEGRATION_TESTS=false
LOG_LEVEL=INFO
```

```python
import os
from evolution_openai import OpenAI
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

client = OpenAI(
    key_id=os.getenv("EVOLUTION_KEY_ID"),
    secret=os.getenv("EVOLUTION_SECRET"),
    base_url=os.getenv("EVOLUTION_BASE_URL"),
    project_id=os.getenv("EVOLUTION_PROJECT_ID"),  # Опционально для Foundation Models
)
```

### Удобные функции

```python
from evolution_openai import create_client, create_async_client

# Sync client
client = create_client(key_id="...", secret="...", base_url="...", timeout=30.0)

# Async client
async_client = create_async_client(key_id="...", secret="...", base_url="...", max_retries=5)
```

## 📋 Полная совместимость

Поддерживаются ВСЕ методы OpenAI SDK:

```python
# Chat API
client.chat.completions.create(...)
client.chat.completions.create(..., stream=True)

# Models API
client.models.list()
client.models.retrieve("model_id")

# Legacy Completions
client.completions.create(...)

# Advanced features
client.with_options(timeout=30).chat.completions.create(...)
client.chat.completions.with_raw_response.create(...)

# Context manager
with client:
    response = client.chat.completions.create(...)
```


## 📚 Документация

- [API Documentation](https://cloud-ru-tech.github.io/evolution-openai-python)
- [Evolution Foundation Models Guide](https://cloud-ru-tech.github.io/evolution-openai-python/foundation_models)
- [Migration Guide](https://cloud-ru-tech.github.io/evolution-openai-python/migration)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)
- [Environment Configuration](env.example)


## 🆘 Support

- [GitHub Issues](https://github.com/cloud-ru-tech/evolution-openai-python/issues)
- [Documentation](https://cloud-ru-tech.github.io/evolution-openai-python)
- Email: support@cloud.ru

## 🔗 Links

- [PyPI Package](https://pypi.org/project/evolution-openai/)
- [GitHub Repository](https://github.com/cloud-ru-tech/evolution-openai-python)
- [Cloud.ru Platform](https://cloud.ru/)
- [OpenAI Python SDK](https://github.com/openai/openai-python) 