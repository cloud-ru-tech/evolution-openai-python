Evolution OpenAI Documentation
================================

.. image:: https://img.shields.io/pypi/v/evolution-openai.svg
   :target: https://pypi.org/project/evolution-openai/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/evolution-openai.svg
   :target: https://pypi.org/project/evolution-openai/
   :alt: Python versions

**Evolution OpenAI** - это 100% совместимый с официальным OpenAI Python SDK клиент для работы с моделями искусственного интеллекта на платформе Cloud.ru.

Особенности
-----------

✅ **Полная совместимость** с официальным OpenAI SDK

✅ **Автоматическое управление токенами** Cloud.ru

✅ **Поддержка всех API методов** (chat, completions, embeddings, и др.)

✅ **Async/await поддержка**

✅ **Streaming responses**

✅ **Type hints** и автодополнение

✅ **Подробная документация** и примеры

Быстрый старт
-------------

Установка
~~~~~~~~~

.. code-block:: bash

   pip install evolution-openai

Основное использование
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import OpenAI

   client = OpenAI(
       key_id="your_EVOLUTION_key_id",
       secret="your_EVOLUTION_secret", 
       base_url="https://your-model-endpoint.cloud.ru/v1"
   )

   response = client.chat.completions.create(
       model="default",
       messages=[
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "Привет! Как дела?"}
       ]
   )

   print(response.choices[0].message.content)

Содержание
----------

.. toctree::
   :maxdepth: 2
   :caption: Руководство пользователя:

   quickstart
   installation
   authentication
   usage
   async_usage
   streaming
   error_handling
   migration

.. toctree::
   :maxdepth: 2
   :caption: Дополнительно:

   README_DOCS
   workflow
   coverage-setup

Индексы и таблицы
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 