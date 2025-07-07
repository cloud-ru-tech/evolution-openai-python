Evolution Foundation Models
============================

Evolution Foundation Models - это специальная платформа для работы с передовыми моделями искусственного интеллекта на основе Cloud.ru. Библиотека **evolution-openai** предоставляет полную поддержку для работы с Evolution Foundation Models через знакомый OpenAI-совместимый API.

Особенности Foundation Models
------------------------------

✅ **Передовые модели AI** - Доступ к последним моделям ИИ включая DeepSeek-R1, Qwen2.5 и другие

✅ **Автоматическое управление Project ID** - Библиотека автоматически добавляет заголовок ``x-project-id``

✅ **Полная совместимость с OpenAI SDK** - Все методы работают идентично

✅ **Поддержка streaming** - Потоковая обработка ответов

✅ **Async/await поддержка** - Асинхронные операции

✅ **Автоматическое управление токенами** - Встроенная авторизация Cloud.ru

Быстрый старт
-------------

Базовая настройка
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import OpenAI

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret", 
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id"  # Обязательно для Foundation Models
   )

   response = client.chat.completions.create(
       model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       messages=[
           {"role": "system", "content": "Ты полезный помощник."},
           {"role": "user", "content": "Расскажи о возможностях ИИ"}
       ],
       max_tokens=100
   )

   print(response.choices[0].message.content)

Переменные окружения
~~~~~~~~~~~~~~~~~~~~

Рекомендуется использовать файл ``.env`` для хранения конфигурации:

.. code-block:: bash

   # .env файл для Foundation Models
   EVOLUTION_KEY_ID=your_key_id_here
   EVOLUTION_SECRET=your_secret_here
   EVOLUTION_BASE_URL=https://foundation-models.api.cloud.ru/api/gigacube/openai/v1
   EVOLUTION_PROJECT_ID=your_project_id_here
   EVOLUTION_FOUNDATION_MODELS_URL=https://foundation-models.api.cloud.ru/api/gigacube/openai/v1

Загрузка из переменных окружения:

.. code-block:: python

   import os
   from evolution_openai import OpenAI
   from dotenv import load_dotenv

   load_dotenv()

   client = OpenAI(
       key_id=os.getenv("EVOLUTION_KEY_ID"),
       secret=os.getenv("EVOLUTION_SECRET"),
       base_url=os.getenv("EVOLUTION_FOUNDATION_MODELS_URL"),
       project_id=os.getenv("EVOLUTION_PROJECT_ID"),
   )

Доступные модели
----------------

Evolution Foundation Models предоставляет доступ к различным моделям:

**RefalMachine/RuadaptQwen2.5-7B-Lite-Beta** (рекомендуется)
   Адаптированная для русского языка модель на основе Qwen2.5-7B

**deepseek-ai/DeepSeek-R1-Distill-Llama-70B**
   Модель на основе DeepSeek-R1 с дистилляцией

**Другие модели**
   Список доступных моделей может обновляться - обратитесь к документации Cloud.ru

Параметры конфигурации
----------------------

Project ID
~~~~~~~~~~

``project_id`` - обязательный параметр для Foundation Models:

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id"  # Автоматически добавляется в заголовки
   )

Timeout и повторы
~~~~~~~~~~~~~~~~~

Foundation Models могут требовать больше времени для обработки:

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id",
       timeout=60.0,  # Увеличенный timeout
       max_retries=3,  # Количество повторов
   )

Примеры использования
---------------------

Базовый пример
~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import OpenAI

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id"
   )

   response = client.chat.completions.create(
       model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       messages=[
           {"role": "system", "content": "Ты полезный помощник."},
           {"role": "user", "content": "Объясни машинное обучение простыми словами"}
       ],
       max_tokens=200,
       temperature=0.7
   )

   print(f"Ответ: {response.choices[0].message.content}")
   print(f"Модель: {response.model}")
   print(f"Токенов использовано: {response.usage.total_tokens}")

Streaming ответы
~~~~~~~~~~~~~~~~

.. code-block:: python

   stream = client.chat.completions.create(
       model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       messages=[
           {"role": "user", "content": "Напиши короткое стихотворение про технологии"}
       ],
       stream=True,
       max_tokens=100,
       temperature=0.8
   )

   print("Генерация стихотворения:")
   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end="", flush=True)

Асинхронное использование
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from evolution_openai import AsyncOpenAI

   async def main():
       async with AsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
           project_id="your_project_id"
       ) as client:
           response = await client.chat.completions.create(
               model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
               messages=[
                   {"role": "user", "content": "Что такое квантовые вычисления?"}
               ],
               max_tokens=150
           )
           
           print(response.choices[0].message.content)

   asyncio.run(main())

Параллельные запросы
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from evolution_openai import AsyncOpenAI

   async def parallel_requests():
       async with AsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
           project_id="your_project_id"
       ) as client:
           
           questions = [
               "Что такое ИИ?",
               "Как работает машинное обучение?",
               "Что такое нейронные сети?"
           ]
           
           # Создаем задачи для параллельного выполнения
           tasks = []
           for question in questions:
               task = client.chat.completions.create(
                   model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
                   messages=[
                       {"role": "system", "content": "Дай краткий ответ."},
                       {"role": "user", "content": question}
                   ],
                   max_tokens=50
               )
               tasks.append(task)
           
           # Выполняем все запросы параллельно
           responses = await asyncio.gather(*tasks)
           
           for question, response in zip(questions, responses):
               print(f"Вопрос: {question}")
               print(f"Ответ: {response.choices[0].message.content}")
               print("-" * 50)

   asyncio.run(parallel_requests())

Использование with_options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Настройка дополнительных опций
   client_with_options = client.with_options(
       timeout=120.0,  # Увеличенный timeout
       max_retries=5,  # Больше попыток
   )

   response = client_with_options.chat.completions.create(
       model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       messages=[
           {"role": "user", "content": "Создай подробный план изучения Python"}
       ],
       max_tokens=300,
       temperature=0.3
   )

   print(response.choices[0].message.content)

Управление токенами
-------------------

Информация о токене
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Получение информации о токене
   token_info = client.get_token_info()
   print(f"Токен активен: {token_info['has_token']}")
   print(f"Токен валиден: {token_info['is_valid']}")

   # Текущий токен
   current_token = client.current_token
   print(f"Текущий токен: {current_token[:20]}...")

Принудительное обновление токена
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Принудительное обновление токена
   new_token = client.refresh_token()
   print(f"Новый токен получен: {new_token[:20]}...")

Обработка ошибок
----------------

Типичные ошибки и их обработка
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import OpenAI
   from evolution_openai.exceptions import EvolutionAuthError

   try:
       client = OpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
           project_id="your_project_id"
       )
       
       response = client.chat.completions.create(
           model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
           messages=[
               {"role": "user", "content": "Привет!"}
           ],
           max_tokens=50
       )
       
   except EvolutionAuthError as e:
       print(f"Ошибка авторизации: {e}")
       # Проверьте key_id, secret и project_id
       
   except Exception as e:
       print(f"Общая ошибка: {e}")

Неправильная модель
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       response = client.chat.completions.create(
           model="non-existent-model",
           messages=[{"role": "user", "content": "Test"}],
           max_tokens=10
       )
   except Exception as e:
       print(f"Модель не найдена: {e}")

Неправильные параметры
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       response = client.chat.completions.create(
           model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
           messages=[],  # Пустой список сообщений
           max_tokens=10
       )
   except Exception as e:
       print(f"Неправильные параметры: {e}")

Тестирование
------------

Запуск примеров
~~~~~~~~~~~~~~~

В проекте есть готовые примеры для Foundation Models:

.. code-block:: bash

   # Запуск примеров Foundation Models
   python examples/foundation_models_example.py

Интеграционные тесты
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Установка переменных окружения
   export EVOLUTION_KEY_ID=your_key_id
   export EVOLUTION_SECRET=your_secret
   export EVOLUTION_PROJECT_ID=your_project_id
   export EVOLUTION_FOUNDATION_MODELS_URL=https://foundation-models.api.cloud.ru/api/gigacube/openai/v1
   export ENABLE_FOUNDATION_MODELS_TESTS=true

   # Запуск тестов
   pytest tests/test_foundation_models_integration.py -v

Модульные тесты
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Запуск модульных тестов
   pytest tests/test_foundation_models_unit.py -v

Лучшие практики
---------------

Настройка timeout
~~~~~~~~~~~~~~~~~

Foundation Models могут работать медленнее обычных API:

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id",
       timeout=90.0  # Увеличенный timeout для Foundation Models
   )

Управление токенами
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Ограничение количества токенов в ответе
   response = client.chat.completions.create(
       model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       messages=[{"role": "user", "content": "Объясни квантовую физику"}],
       max_tokens=200,  # Ограничение для контроля затрат
       temperature=0.5  # Сбалансированная креативность
   )

Кеширование соединений
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Используйте context manager для автоматического управления ресурсами
   with OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id"
   ) as client:
       # Множественные запросы с одним клиентом
       for i in range(5):
           response = client.chat.completions.create(
               model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
               messages=[{"role": "user", "content": f"Вопрос {i+1}"}],
               max_tokens=50
           )
           print(response.choices[0].message.content)

Мониторинг использования
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time

   start_time = time.time()
   
   response = client.chat.completions.create(
       model="RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       messages=[{"role": "user", "content": "Создай план проекта"}],
       max_tokens=300
   )
   
   elapsed_time = time.time() - start_time
   
   print(f"Время ответа: {elapsed_time:.2f} секунд")
   print(f"Токенов использовано: {response.usage.total_tokens}")
   print(f"Скорость: {response.usage.total_tokens / elapsed_time:.1f} токен/сек")

Устранение неполадок
--------------------

Проблемы с авторизацией
~~~~~~~~~~~~~~~~~~~~~~~

**Проблема**: Ошибка авторизации при подключении

**Решение**: Проверьте правильность key_id, secret и project_id:

.. code-block:: python

   # Проверьте переменные окружения
   import os
   print(f"KEY_ID: {os.getenv('EVOLUTION_KEY_ID', 'не установлен')}")
   print(f"SECRET: {os.getenv('EVOLUTION_SECRET', 'не установлен')[:10]}...")
   print(f"PROJECT_ID: {os.getenv('EVOLUTION_PROJECT_ID', 'не установлен')}")

Проблемы с моделью
~~~~~~~~~~~~~~~~~~

**Проблема**: Модель не найдена или недоступна

**Решение**: Используйте проверенные модели:

.. code-block:: python

   # Рекомендуемые модели для Foundation Models
   models = [
       "RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
       "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
   ]

Проблемы с сетью
~~~~~~~~~~~~~~~~

**Проблема**: Тайм-ауты или проблемы с подключением

**Решение**: Увеличьте timeout и количество повторов:

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
       project_id="your_project_id",
       timeout=120.0,  # 2 минуты
       max_retries=5,  # 5 попыток
   )

Ссылки
------

- `Примеры Foundation Models <https://github.com/cloud-ru-tech/evolution-openai-python/blob/main/examples/foundation_models_example.py>`_
- `Интеграционные тесты <https://github.com/cloud-ru-tech/evolution-openai-python/blob/main/tests/test_foundation_models_integration.py>`_
- `Модульные тесты <https://github.com/cloud-ru-tech/evolution-openai-python/blob/main/tests/test_foundation_models_unit.py>`_
- `Документация Cloud.ru <https://cloud.ru/docs/>`_
- `OpenAI API Reference <https://platform.openai.com/docs/api-reference>`_ 