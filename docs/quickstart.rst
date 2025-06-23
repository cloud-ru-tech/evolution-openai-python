Быстрый старт
=============

Этот раздел поможет вам быстро начать работу с Evolution OpenAI.

Установка
---------

Установите SDK через pip:

.. code-block:: bash

   pip install evolution-openai

Или, если вы используете Poetry:

.. code-block:: bash

   poetry add evolution-openai

Получение учетных данных
------------------------

Для работы с Evolution OpenAI вам понадобятся:

1. **Key ID** - идентификатор ключа доступа
2. **Secret** - секретный ключ
3. **Base URL** - URL эндпоинта вашей модели

Эти данные можно получить в личном кабинете Cloud.ru.

Первый запрос
-------------

Создайте файл ``example.py`` и добавьте следующий код:

.. code-block:: python

   from evolution_openai import OpenAI

   # Инициализация клиента
   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

   # Выполнение запроса
   response = client.chat.completions.create(
       model="default",
       messages=[
           {"role": "system", "content": "Ты полезный помощник."},
           {"role": "user", "content": "Привет! Расскажи анекдот."}
       ],
       max_tokens=150
   )

   print(response.choices[0].message.content)

Запустите скрипт:

.. code-block:: bash

   python example.py

Использование переменных окружения
----------------------------------

Для безопасности рекомендуется использовать переменные окружения:

.. code-block:: bash

   export EVOLUTION_KEY_ID="your_key_id"
   export EVOLUTION_SECRET="your_secret"
   export EVOLUTION_BASE_URL="https://your-endpoint.cloud.ru/v1"

Затем в коде:

.. code-block:: python

   import os
   from evolution_openai import OpenAI

   client = OpenAI(
       key_id=os.getenv("EVOLUTION_KEY_ID"),
       secret=os.getenv("EVOLUTION_SECRET"),
       base_url=os.getenv("EVOLUTION_BASE_URL")
   )

Или используйте файл ``.env``:

.. code-block:: bash

   # .env
   EVOLUTION_KEY_ID=your_key_id
   EVOLUTION_SECRET=your_secret
   EVOLUTION_BASE_URL=https://your-endpoint.cloud.ru/v1

.. code-block:: python

   from dotenv import load_dotenv
   import os
   from evolution_openai import OpenAI

   load_dotenv()

   client = OpenAI(
       key_id=os.getenv("EVOLUTION_KEY_ID"),
       secret=os.getenv("EVOLUTION_SECRET"),
       base_url=os.getenv("EVOLUTION_BASE_URL")
   )

Основные возможности
--------------------

Streaming
~~~~~~~~~

.. code-block:: python

   stream = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Расскажи историю"}],
       stream=True
   )

   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end='')

Асинхронные запросы
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from evolution_openai import AsyncOpenAI

   async def main():
       client = AsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       )

       response = await client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Привет!"}]
       )

       print(response.choices[0].message.content)

   asyncio.run(main())

Обработка ошибок
~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import OpenAI
   from evolution_openai.exceptions import EvolutionOpenAIError

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

   try:
       response = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Привет!"}]
       )
       print(response.choices[0].message.content)
   except EvolutionOpenAIError as e:
       print(f"Ошибка API: {e}")
   except Exception as e:
       print(f"Неожиданная ошибка: {e}")

Что дальше?
-----------

- Изучите :doc:`usage` для подробного руководства
.. - Посмотрите :doc:`examples/basic_usage` для больших примеров
.. - Прочитайте :doc:`api/client` для справки по API 

