# Evolution OpenAI
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/evolution-openai.svg)](https://badge.fury.io/py/evolution-openai)
[![Coverage](https://cloud-ru-tech.github.io/evolution-openai-python/badges/coverage.svg)](https://github.com/cloud-ru-tech/evolution-openai-python/actions)

**Полностью совместимый** Evolution OpenAI client с автоматическим управлением токенами. Просто замените `OpenAI` на `EvolutionOpenAI` и все будет работать!

## 🎯 Особенности

- ✅ **100% совместимость** с официальным OpenAI Python SDK
- ✅ **Автоматическое управление токенами** Cloud.ru
- ✅ **Drop-in replacement** - минимальные изменения в коде
- ✅ **Async/await поддержка** с `EvolutionAsyncOpenAI`
- ✅ **Streaming responses** поддержка
- ✅ **Thread-safe** token management
- ✅ **Автоматическое обновление** токенов за 30 секунд до истечения
- ✅ **Retry логика** при ошибках авторизации
- ✅ **Поддержка .env файлов** для управления конфигурацией
- ✅ **Интеграционные тесты** с реальным API
 

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
from evolution_openai import EvolutionOpenAI

# Для обычного использования
client = EvolutionOpenAI(
    key_id="your_key_id", secret="your_secret", base_url="https://your-model-endpoint.cloud.ru/v1"
)

response = client.chat.completions.create(
    model="default", messages=[{"role": "user", "content": "Hello!"}]
)
```

### Основное использование

#### Обычное использование

```python
from evolution_openai import EvolutionOpenAI

# Инициализация client для обычного использования
client = EvolutionOpenAI(
    key_id="your_key_id", secret="your_secret", base_url="https://your-model-endpoint.cloud.ru/v1"
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

 

### Streaming

```python
# Для обычного использования
stream = client.chat.completions.create(
    model="default", messages=[{"role": "user", "content": "Tell me a story"}], stream=True
)


for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Async/Await

```python
import asyncio
from evolution_openai import EvolutionAsyncOpenAI


async def main():
    client = EvolutionAsyncOpenAI(
        key_id="your_key_id",
        secret="your_secret",
        base_url="https://your-model-endpoint.cloud.ru/v1",
    )
    response = await client.chat.completions.create(
        model="default", messages=[{"role": "user", "content": "Async hello!"}]
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

 

```python
import os
from evolution_openai import EvolutionOpenAI
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

client = EvolutionOpenAI(
    key_id=os.getenv("EVOLUTION_KEY_ID"),
    secret=os.getenv("EVOLUTION_SECRET"),
    base_url=os.getenv("EVOLUTION_BASE_URL"),
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