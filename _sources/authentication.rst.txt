Аутентификация
==============

Evolution OpenAI использует систему аутентификации Cloud.ru для доступа к API моделей искусственного интеллекта.

Получение учетных данных
------------------------

Для работы с SDK вам понадобятся:

1. **Key ID** - идентификатор ключа доступа
2. **Secret** - секретный ключ
3. **Base URL** - URL эндпоинта вашей модели

Эти данные можно получить в личном кабинете Cloud.ru:

1. Войдите в личный кабинет Cloud.ru
2. Перейдите в раздел "AI/ML сервисы"
3. Выберите вашу модель
4. В разделе "API доступ" найдите учетные данные

Способы аутентификации
----------------------

Прямое указание в коде
~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   Не рекомендуется для продакшена! Используйте только для тестирования.

.. code-block:: python

   from evolution_openai import OpenAI

   client = OpenAI(
       key_id="your_key_id_here",
       secret="your_secret_here",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

Переменные окружения
~~~~~~~~~~~~~~~~~~~~

**Рекомендуемый способ** для продакшена:

.. code-block:: bash

   export EVOLUTION_KEY_ID="your_key_id"
   export EVOLUTION_SECRET="your_secret"
   export EVOLUTION_BASE_URL="https://your-endpoint.cloud.ru/v1"

.. code-block:: python

   import os
   from evolution_openai import OpenAI

   client = OpenAI(
       key_id=os.getenv("EVOLUTION_KEY_ID"),
       secret=os.getenv("EVOLUTION_SECRET"),
       base_url=os.getenv("EVOLUTION_BASE_URL")
   )

Файл .env
~~~~~~~~~

Создайте файл ``.env`` в корне проекта:

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

Управление токенами
-------------------

SDK автоматически управляет токенами доступа:

Автоматическое обновление
~~~~~~~~~~~~~~~~~~~~~~~~~

- Токены автоматически обновляются за 30 секунд до истечения
- При ошибках авторизации токен обновляется принудительно
- Каждый клиент управляет своими токенами независимо

Ручное управление
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Получить информацию о текущем токене
   token_info = client.get_token_info()
   print(token_info)
   # {
   #     "has_token": true,
   #     "expires_at": "2024-01-01T12:00:00Z",
   #     "is_valid": true,
   #     "buffer_seconds": 30
   # }

   # Принудительно обновить токен
   new_token = client.refresh_token()

   # Получить текущий токен
   current_token = client.current_token

Безопасность
------------

Лучшие практики
~~~~~~~~~~~~~~~

.. important::
   Никогда не храните учетные данные в коде или публичных репозиториях!

1. **Используйте переменные окружения** или файлы конфигурации
2. **Добавьте .env в .gitignore**
3. **Используйте разные учетные данные** для разработки и продакшена
4. **Регулярно обновляйте ключи** доступа
5. **Ограничивайте области доступа** ключей

Файл .gitignore
~~~~~~~~~~~~~~~

Убедитесь, что ваш ``.gitignore`` содержит:

.. code-block:: bash

   # Environment variables
   .env
   .env.*
   !.env.example

   # Credentials
   *.token
   credentials.json

Ротация ключей
~~~~~~~~~~~~~~

При компрометации ключей:

1. Сгенерируйте новые ключи в личном кабинете Cloud.ru
2. Обновите переменные окружения
3. Перезапустите приложение
4. Удалите старые ключи из системы

Отладка аутентификации
----------------------

Включение логирования
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   # Включить отладочные логи
   logging.basicConfig(level=logging.DEBUG)
   
   from evolution_openai import OpenAI
   
   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

Проверка подключения
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       # Простой тестовый запрос
       response = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Тест подключения"}],
           max_tokens=10
       )
       print("✅ Аутентификация успешна")
   except Exception as e:
       print(f"❌ Ошибка аутентификации: {e}")

Частые ошибки
-------------

401 Unauthorized
~~~~~~~~~~~~~~~~

.. code-block:: bash

   401 Client Error: Unauthorized

**Причины:**
- Неверный Key ID или Secret
- Истекший токен (автоматически исправляется SDK)
- Доступ к эндпоинту запрещен

**Решение:**
- Проверьте правильность учетных данных
- Убедитесь в доступности эндпоинта
- Проверьте права доступа ключа

403 Forbidden
~~~~~~~~~~~~~

.. code-block:: bash

   403 Client Error: Forbidden

**Причины:**
- Недостаточно прав у ключа доступа
- Эндпоинт недоступен для вашего аккаунта

**Решение:**
- Проверьте права доступа в личном кабинете
- Обратитесь в поддержку Cloud.ru

Таймауты
~~~~~~~~

.. code-block:: bash

   TimeoutError: Request timed out

**Решение:**

.. code-block:: python

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1",
       timeout=60.0  # Увеличить таймаут
   ) 