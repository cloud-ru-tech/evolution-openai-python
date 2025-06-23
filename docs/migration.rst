Миграция с OpenAI SDK
=====================

Этот раздел поможет вам мигрировать с официального OpenAI Python SDK на Evolution OpenAI.

Почему миграция проста
----------------------

Evolution OpenAI **полностью совместим** с официальным OpenAI SDK:

✅ **Идентичный API** - все методы и параметры работают одинаково
✅ **Те же типы данных** - структуры ответов не изменились  
✅ **Совместимые исключения** - обработка ошибок аналогична
✅ **Async/await поддержка** - все асинхронные возможности сохранены
✅ **Streaming API** - потоковая передача работает идентично

Основные изменения
------------------

Единственное отличие - **способ аутентификации**:

.. list-table:: Сравнение аутентификации
   :header-rows: 1
   :widths: 50 50

   * - OpenAI SDK
     - Evolution OpenAI
   * - ``api_key="sk-..."``
     - ``key_id="your_key_id", secret="your_secret"``
   * - ``base_url`` (опционально)
     - ``base_url`` (обязательно)
   * - ``organization`` (опционально)
     - ``organization`` (совместимость)

Пошаговая миграция
------------------

Шаг 1: Установка
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Удалите старый SDK (опционально)
   pip uninstall openai
   
   # Установите Evolution SDK
   pip install evolution-openai

Шаг 2: Изменение импортов
~~~~~~~~~~~~~~~~~~~~~~~~~

**До:**

.. code-block:: python

   from openai import OpenAI, AsyncOpenAI

**После:**

.. code-block:: python

   from evolution_openai import OpenAI, AsyncOpenAI

Шаг 3: Обновление аутентификации
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**До:**

.. code-block:: python

   client = OpenAI(
       api_key="sk-your-openai-key"
   )

**После:**

.. code-block:: python

   client = OpenAI(
       key_id="your_EVOLUTION_key_id",
       secret="your_EVOLUTION_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

Шаг 4: Переменные окружения
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**До:**

.. code-block:: bash

   export OPENAI_API_KEY="sk-your-key"
   export OPENAI_BASE_URL="https://api.openai.com/v1"  # опционально

**После:**

.. code-block:: bash

   export EVOLUTION_KEY_ID="your_key_id"
   export EVOLUTION_SECRET="your_secret"
   export EVOLUTION_BASE_URL="https://your-endpoint.cloud.ru/v1"

Примеры миграции
----------------

Базовый чат
~~~~~~~~~~~

**До (OpenAI):**

.. code-block:: python

   from openai import OpenAI
   import os

   client = OpenAI(
       api_key=os.getenv("OPENAI_API_KEY")
   )

   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "Hello!"}
       ],
       max_tokens=100
   )

   print(response.choices[0].message.content)

**После (Evolution):**

.. code-block:: python

   from evolution_openai import OpenAI
   import os

   client = OpenAI(
       key_id=os.getenv("EVOLUTION_KEY_ID"),
       secret=os.getenv("EVOLUTION_SECRET"),
       base_url=os.getenv("EVOLUTION_BASE_URL")
   )

   response = client.chat.completions.create(
       model="default",  # Или название вашей модели
       messages=[
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "Hello!"}
       ],
       max_tokens=100
   )

   print(response.choices[0].message.content)

Асинхронный код
~~~~~~~~~~~~~~~

**До (OpenAI):**

.. code-block:: python

   import asyncio
   from openai import AsyncOpenAI

   async def main():
       client = AsyncOpenAI(
           api_key="sk-your-key"
       )
       
       response = await client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Hello async!"}]
       )
       
       print(response.choices[0].message.content)

   asyncio.run(main())

**После (Evolution):**

.. code-block:: python

   import asyncio
   from evolution_openai import AsyncOpenAI

   async def main():
       async with AsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           response = await client.chat.completions.create(
               model="default",
               messages=[{"role": "user", "content": "Hello async!"}]
           )
           
           print(response.choices[0].message.content)

   asyncio.run(main())

Streaming
~~~~~~~~~

**До (OpenAI):**

.. code-block:: python

   from openai import OpenAI

   client = OpenAI(api_key="sk-your-key")

   stream = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Tell me a story"}],
       stream=True
   )

   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end="")

**После (Evolution):**

.. code-block:: python

   from evolution_openai import OpenAI

   client = OpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

   stream = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Tell me a story"}],
       stream=True
   )

   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end="")

Обработка ошибок
~~~~~~~~~~~~~~~~

**До (OpenAI):**

.. code-block:: python

   from openai import OpenAI
   from openai.error import OpenAIError, RateLimitError

   try:
       response = client.chat.completions.create(...)
   except RateLimitError as e:
       print(f"Rate limit exceeded: {e}")
   except OpenAIError as e:
       print(f"OpenAI error: {e}")

**После (Evolution):**

.. code-block:: python

   from evolution_openai import OpenAI
   from evolution_openai.exceptions import EvolutionOpenAIError, RateLimitError

   try:
       response = client.chat.completions.create(...)
   except RateLimitError as e:
       print(f"Rate limit exceeded: {e}")
   except EvolutionOpenAIError as e:
       print(f"Evolution error: {e}")

Автоматическая миграция
-----------------------

Скрипт миграции
~~~~~~~~~~~~~~~

Создайте файл ``migrate.py`` для автоматической замены:

.. code-block:: python

   #!/usr/bin/env python3
   """
   Скрипт для автоматической миграции с OpenAI SDK на Evolution OpenAI
   """

   import os
   import re
   import argparse
   from pathlib import Path

   def migrate_file(file_path):
       """Мигрирует один Python файл"""
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       original_content = content
       
       # Замена импортов
       content = re.sub(
           r'from openai import',
           r'from evolution_openai import',
           content
       )
       
       content = re.sub(
           r'import openai',
           r'import evolution_openai as openai',
           content
       )
       
       # Замена создания клиента
       content = re.sub(
           r'OpenAI\(\s*api_key\s*=\s*["\']([^"\']+)["\']\s*\)',
           r'OpenAI(\n    key_id="your_key_id",\n    secret="your_secret",\n    base_url="https://your-endpoint.cloud.ru/v1"\n)',
           content
       )
       
       # Замена переменных окружения
       content = re.sub(
           r'os\.getenv\(["\']OPENAI_API_KEY["\']\)',
           r'os.getenv("EVOLUTION_KEY_ID")',
           content
       )
       
       # Замена исключений
       content = re.sub(
           r'from openai\.error import',
           r'from evolution_openai.exceptions import',
           content
       )
       
       content = re.sub(
           r'OpenAIError',
           r'EvolutionOpenAIError',
           content
       )
       
       if content != original_content:
           # Создаем резервную копию
           backup_path = f"{file_path}.backup"
           with open(backup_path, 'w', encoding='utf-8') as f:
               f.write(original_content)
           
           # Записываем измененный файл
           with open(file_path, 'w', encoding='utf-8') as f:
               f.write(content)
           
           print(f"✅ Мигрирован: {file_path} (резервная копия: {backup_path})")
           return True
       else:
           print(f"⏭️ Без изменений: {file_path}")
           return False

   def migrate_directory(directory):
       """Мигрирует все Python файлы в директории"""
       directory = Path(directory)
       migrated_count = 0
       
       for py_file in directory.rglob("*.py"):
           if migrate_file(py_file):
               migrated_count += 1
       
       print(f"\n📊 Мигрировано файлов: {migrated_count}")

   def create_env_template():
       """Создает шаблон .env файла"""
       env_content = """# Evolution OpenAI Configuration
   EVOLUTION_KEY_ID=your_key_id_here
   EVOLUTION_SECRET=your_secret_here  
   EVOLUTION_BASE_URL=https://your-endpoint.cloud.ru/v1

   # Legacy OpenAI (удалите после миграции)
   # OPENAI_API_KEY=sk-...
   """
       
       with open('.env.Evolution', 'w') as f:
           f.write(env_content)
       
       print("📄 Создан шаблон .env.Evolution")

   def main():
       parser = argparse.ArgumentParser(
           description="Миграция с OpenAI SDK на Evolution OpenAI"
       )
       parser.add_argument(
           'path',
           help="Путь к файлу или директории для миграции"
       )
       parser.add_argument(
           '--env',
           action='store_true',
           help="Создать шаблон .env файла"
       )
       
       args = parser.parse_args()
       
       if args.env:
           create_env_template()
       
       path = Path(args.path)
       
       if path.is_file() and path.suffix == '.py':
           migrate_file(path)
       elif path.is_dir():
           migrate_directory(path)
       else:
           print(f"❌ Некорректный путь: {path}")

   if __name__ == "__main__":
       main()

Использование скрипта:

.. code-block:: bash

   # Мигрировать один файл
   python migrate.py my_app.py
   
   # Мигрировать всю директорию
   python migrate.py ./src
   
   # Создать шаблон .env
   python migrate.py --env .

Конфигурационные файлы
----------------------

Docker Compose
~~~~~~~~~~~~~~

**До:**

.. code-block:: yaml

   version: '3.8'
   services:
     app:
       build: .
       environment:
         - OPENAI_API_KEY=sk-your-key
         - OPENAI_BASE_URL=https://api.openai.com/v1

**После:**

.. code-block:: yaml

   version: '3.8'
   services:
     app:
       build: .
       environment:
         - EVOLUTION_KEY_ID=your_key_id
         - EVOLUTION_SECRET=your_secret
         - EVOLUTION_BASE_URL=https://your-endpoint.cloud.ru/v1

Kubernetes
~~~~~~~~~~

**До:**

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: openai-config
   data:
     OPENAI_API_KEY: "sk-your-key"

**После:**

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: Evolution-config
   data:
     EVOLUTION_KEY_ID: "your_key_id"
     EVOLUTION_SECRET: "your_secret"
     EVOLUTION_BASE_URL: "https://your-endpoint.cloud.ru/v1"

Тестирование миграции
---------------------

Проверочный скрипт
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   #!/usr/bin/env python3
   """
   Тестирование миграции Evolution OpenAI
   """

   import os
   from evolution_openai import OpenAI

   def test_connection():
       """Тестирует подключение к Evolution API"""
       try:
           client = OpenAI(
               key_id=os.getenv("EVOLUTION_KEY_ID"),
               secret=os.getenv("EVOLUTION_SECRET"),
               base_url=os.getenv("EVOLUTION_BASE_URL")
           )
           
           response = client.chat.completions.create(
               model="default",
               messages=[{"role": "user", "content": "Test connection"}],
               max_tokens=10
           )
           
           print("✅ Подключение успешно!")
           print(f"Ответ: {response.choices[0].message.content}")
           return True
           
       except Exception as e:
           print(f"❌ Ошибка подключения: {e}")
           return False

   def test_models():
       """Тестирует получение списка моделей"""
       try:
           client = OpenAI(
               key_id=os.getenv("EVOLUTION_KEY_ID"),
               secret=os.getenv("EVOLUTION_SECRET"),
               base_url=os.getenv("EVOLUTION_BASE_URL")
           )
           
           models = client.models.list()
           print(f"✅ Доступные модели: {len(models.data)}")
           
           for model in models.data:
               print(f"  - {model.id}")
           
           return True
           
       except Exception as e:
           print(f"❌ Ошибка получения моделей: {e}")
           return False

   def main():
       print("🧪 Тестирование Evolution OpenAI")
       print("=" * 40)
       
       # Проверка переменных окружения
       required_vars = ["EVOLUTION_KEY_ID", "EVOLUTION_SECRET", "EVOLUTION_BASE_URL"]
       missing_vars = [var for var in required_vars if not os.getenv(var)]
       
       if missing_vars:
           print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
           return False
       
       print("✅ Переменные окружения настроены")
       
       # Тестирование
       success = True
       success &= test_connection()
       success &= test_models()
       
       if success:
           print("\n🎉 Миграция завершена успешно!")
       else:
           print("\n❌ Обнаружены проблемы в миграции")
       
       return success

   if __name__ == "__main__":
       exit(0 if main() else 1)

Частые проблемы и решения
-------------------------

Проблема: "Module not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Ошибка:**

.. code-block::

   ModuleNotFoundError: No module named 'openai'

**Решение:**

.. code-block:: python

   # Замените все импорты
   # from openai import OpenAI
   from evolution_openai import OpenAI

Проблема: "Invalid credentials"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Ошибка:**

.. code-block::

   AuthenticationError: Invalid credentials

**Решение:**

1. Проверьте правильность ``key_id`` и ``secret``
2. Убедитесь, что ``base_url`` корректен
3. Проверьте права доступа ключа

Проблема: "Model not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Ошибка:**

.. code-block::

   NotFoundError: Model 'gpt-3.5-turbo' not found

**Решение:**

.. code-block:: python

   # Замените название модели на доступное
   response = client.chat.completions.create(
       model="default",  # Или другое доступное название
       messages=[...]
   )

Проблема: Старые исключения
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Ошибка:**

.. code-block::

   NameError: name 'OpenAIError' is not defined

**Решение:**

.. code-block:: python

   # Замените импорты исключений
   # from openai.error import OpenAIError
   from evolution_openai.exceptions import EvolutionOpenAIError

Rollback план
-------------

Если миграция вызвала проблемы, можно быстро откатиться:

.. code-block:: bash

   # 1. Восстановите из резервных копий
   find . -name "*.py.backup" -exec bash -c 'mv "$1" "${1%.backup}"' _ {} \;
   
   # 2. Переустановите оригинальный SDK
   pip uninstall evolution-openai
   pip install openai
   
   # 3. Восстановите переменные окружения
   export OPENAI_API_KEY="sk-your-original-key"

Чек-лист миграции
-----------------

.. list-table:: Чек-лист для миграции
   :header-rows: 1
   :widths: 70 30

   * - Задача
     - Статус
   * - ☐ Установлен ``evolution-openai``
     - 
   * - ☐ Обновлены импорты во всех файлах
     - 
   * - ☐ Изменена аутентификация
     - 
   * - ☐ Обновлены переменные окружения
     - 
   * - ☐ Исправлены названия моделей
     - 
   * - ☐ Обновлены исключения
     - 
   * - ☐ Обновлены конфигурационные файлы
     - 
   * - ☐ Протестировано подключение
     - 
   * - ☐ Протестированы основные функции
     - 
   * - ☐ Обновлена документация проекта
     - 

Заключение
----------

Миграция с OpenAI SDK на Evolution OpenAI - это простой процесс, который требует минимальных изменений в коде. Основное отличие - в способе аутентификации, все остальное остается неизменным.

**Преимущества после миграции:**

✅ Доступ к моделям на платформе Cloud.ru
✅ Автоматическое управление токенами
✅ Тот же удобный API
✅ Полная совместимость с существующим кодом
✅ Поддержка всех современных возможностей 