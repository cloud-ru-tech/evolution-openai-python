Использование
=============

Этот раздел покрывает основные способы использования Evolution OpenAI.

Основы работы с SDK
-------------------

Инициализация клиента
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import OpenAI

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

Chat Completions API
--------------------

Базовый запрос
~~~~~~~~~~~~~~

.. code-block:: python

   response = client.chat.completions.create(
       model="default",
       messages=[
           {"role": "system", "content": "Ты полезный помощник."},
           {"role": "user", "content": "Объясни квантовую физику простыми словами"}
       ],
       max_tokens=200
   )

   print(response.choices[0].message.content)

С дополнительными параметрами
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   response = client.chat.completions.create(
       model="default",
       messages=[
           {"role": "system", "content": "Ты креативный писатель."},
           {"role": "user", "content": "Напиши короткую историю про робота"}
       ],
       max_tokens=300,
       temperature=0.8,          # Креативность (0.0-2.0)
       top_p=0.9,               # Nucleus sampling
       frequency_penalty=0.5,    # Штраф за повторения
       presence_penalty=0.3,     # Штраф за присутствие токенов
       stop=["КОНЕЦ", "END"]     # Остановочные последовательности
   )

Диалоговый режим
~~~~~~~~~~~~~~~~

.. code-block:: python

   # История диалога
   conversation = [
       {"role": "system", "content": "Ты дружелюбный помощник."}
   ]

   # Функция для продолжения диалога
   def chat(message):
       conversation.append({"role": "user", "content": message})
       
       response = client.chat.completions.create(
           model="default",
           messages=conversation,
           max_tokens=150
       )
       
       assistant_message = response.choices[0].message.content
       conversation.append({"role": "assistant", "content": assistant_message})
       
       return assistant_message

   # Пример диалога
   print(chat("Привет! Как дела?"))
   print(chat("Расскажи анекдот"))
   print(chat("Объясни предыдущий анекдот"))

Models API
----------

Получение списка моделей
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   models = client.models.list()
   for model in models.data:
       print(f"ID: {model.id}, Created: {model.created}")

Информация о конкретной модели
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   model = client.models.retrieve("default")
   print(f"Model: {model.id}")
   print(f"Owner: {model.owned_by}")

Legacy Completions API
----------------------

.. note::
   Рекомендуется использовать Chat Completions API для новых проектов.

.. code-block:: python

   response = client.completions.create(
       model="default",
       prompt="Расскажи о преимуществах искусственного интеллекта:",
       max_tokens=150,
       temperature=0.7
   )

   print(response.choices[0].text)

Продвинутые возможности
-----------------------

Per-request конфигурация
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Временное изменение таймаута для одного запроса
   response = client.with_options(timeout=60.0).chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Долгий запрос..."}],
       max_tokens=500
   )

Raw response доступ
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Получение полного HTTP ответа
   raw_response = client.chat.completions.with_raw_response.create(
       model="default",
       messages=[{"role": "user", "content": "Тестовое сообщение"}],
       max_tokens=50
   )

   print(f"Status Code: {raw_response.status_code}")
   print(f"Headers: {raw_response.headers}")
   
   # Парсинг ответа
   parsed = raw_response.parse()
   print(parsed.choices[0].message.content)

Context Manager
~~~~~~~~~~~~~~~

.. code-block:: python

   with OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   ) as client:
       response = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Привет!"}]
       )
       print(response.choices[0].message.content)
   # Клиент автоматически закрывается

Helper функции
--------------

create_client()
~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import create_client

   client = create_client(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1",
       timeout=30.0,
       max_retries=3
   )

Конфигурация клиента
--------------------

Таймауты
~~~~~~~~

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1",
       timeout=30.0  # 30 секунд
   )

Повторные попытки
~~~~~~~~~~~~~~~~~

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1",
       max_retries=5  # До 5 повторных попыток
   )

Кастомные заголовки
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1",
       default_headers={
           "User-Agent": "MyApp/1.0",
           "X-Custom-Header": "custom-value"
       }
   )

Обработка ответов
-----------------

Структура ответа
~~~~~~~~~~~~~~~~

.. code-block:: python

   response = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Привет!"}]
   )

   # Основные поля ответа
   print(f"ID: {response.id}")
   print(f"Model: {response.model}")
   print(f"Created: {response.created}")
   
   # Выбор ответа
   choice = response.choices[0]
   print(f"Message: {choice.message.content}")
   print(f"Role: {choice.message.role}")
   print(f"Finish Reason: {choice.finish_reason}")
   
   # Статистика использования
   if response.usage:
       print(f"Prompt Tokens: {response.usage.prompt_tokens}")
       print(f"Completion Tokens: {response.usage.completion_tokens}")
       print(f"Total Tokens: {response.usage.total_tokens}")

Несколько вариантов ответа
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   response = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Назови три цвета"}],
       n=3  # Получить 3 варианта ответа
   )

   for i, choice in enumerate(response.choices):
       print(f"Вариант {i+1}: {choice.message.content}")

Лучшие практики
---------------

Управление контекстом
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def manage_conversation_length(messages, max_tokens=2000):
       """Обрезает историю диалога, если она слишком длинная"""
       total_tokens = estimate_tokens(messages)
       
       while total_tokens > max_tokens and len(messages) > 1:
           # Удаляем самые старые сообщения (кроме системного)
           if messages[1]["role"] != "system":
               messages.pop(1)
           else:
               messages.pop(2)
           total_tokens = estimate_tokens(messages)
       
       return messages

   def estimate_tokens(messages):
       """Примерная оценка количества токенов"""
       return sum(len(msg["content"].split()) * 1.3 for msg in messages)

Кеширование ответов
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import hashlib
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def cached_completion(prompt_hash, max_tokens=100):
       """Кеширует ответы для одинаковых запросов"""
       response = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": prompt_hash}],
           max_tokens=max_tokens
       )
       return response.choices[0].message.content

   def get_completion(prompt):
       prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
       return cached_completion(prompt_hash)

Обработка больших текстов
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def process_large_text(text, chunk_size=2000):
       """Обрабатывает большой текст по частям"""
       chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
       results = []
       
       for i, chunk in enumerate(chunks):
           print(f"Обрабатываю часть {i+1}/{len(chunks)}")
           
           response = client.chat.completions.create(
               model="default",
               messages=[
                   {"role": "system", "content": "Суммируй следующий текст:"},
                   {"role": "user", "content": chunk}
               ],
               max_tokens=200
           )
           
           results.append(response.choices[0].message.content)
       
       return results

Мониторинг использования
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from collections import defaultdict

   class UsageTracker:
       def __init__(self):
           self.stats = defaultdict(int)
           self.start_time = time.time()
       
       def track_request(self, response):
           if response.usage:
               self.stats["total_tokens"] += response.usage.total_tokens
               self.stats["requests"] += 1
       
       def get_stats(self):
           elapsed = time.time() - self.start_time
           return {
               "total_requests": self.stats["requests"],
               "total_tokens": self.stats["total_tokens"],
               "avg_tokens_per_request": self.stats["total_tokens"] / max(1, self.stats["requests"]),
               "requests_per_minute": self.stats["requests"] / (elapsed / 60),
               "tokens_per_minute": self.stats["total_tokens"] / (elapsed / 60)
           }

   # Использование
   tracker = UsageTracker()

   response = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Тест"}]
   )

   tracker.track_request(response)
   print(tracker.get_stats()) 