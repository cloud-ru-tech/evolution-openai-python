Установка
=========

Evolution OpenAI можно установить несколькими способами.

Требования к системе
--------------------

- Python 3.8.1 или выше
- pip или Poetry для управления пакетами

Установка через pip
-------------------

Самый простой способ установки:

.. code-block:: bash

   pip install evolution-openai

Установка через Poetry
----------------------

Если вы используете Poetry для управления зависимостями:

.. code-block:: bash

   poetry add evolution-openai

Установка из исходного кода
---------------------------

Для разработчиков или для получения последней версии:

.. code-block:: bash

   git clone https://github.com/cloud-ru-tech/evolution-openai-python.git
   cd evolution-openai
   pip install -e .

Установка для разработки
------------------------

Если вы планируете вносить изменения в код:

.. code-block:: bash

   git clone https://github.com/cloud-ru-tech/evolution-openai-python.git
   cd evolution-openai
   
   # С Poetry
   poetry install --with=dev,docs
   
   # Или с pip
   pip install -e ".[dev,test,docs]"

Проверка установки
------------------

Проверьте, что установка прошла успешно:

.. code-block:: python

   import evolution_openai
   print(evolution_openai.__version__)

Или через командную строку:

.. code-block:: bash

   python -c "import evolution_openai; print(evolution_openai.__version__)"

Обновление
----------

Для обновления до последней версии:

.. code-block:: bash

   # С pip
   pip install --upgrade evolution-openai
   
   # С Poetry
   poetry update evolution-openai

Удаление
--------

Если нужно удалить пакет:

.. code-block:: bash

   # С pip
   pip uninstall evolution-openai
   
   # С Poetry (удалить из проекта)
   poetry remove evolution-openai

Возможные проблемы
------------------

Конфликт версий Python
~~~~~~~~~~~~~~~~~~~~~~

Если вы получаете ошибку о несовместимости версий Python:

.. code-block:: bash

   ERROR: evolution-openai requires Python '>=3.8.1' but the running Python is 3.8.0

Обновите Python до версии 3.8.1 или выше.

Проблемы с зависимостями
~~~~~~~~~~~~~~~~~~~~~~~~

При конфликтах зависимостей попробуйте:

.. code-block:: bash

   # Очистить кеш pip
   pip cache purge
   
   # Переустановить пакет
   pip uninstall evolution-openai
   pip install evolution-openai

Проблемы с установкой в виртуальном окружении
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Убедитесь, что виртуальное окружение активировано:

.. code-block:: bash

   # Создание виртуального окружения
   python -m venv venv
   
   # Активация (Linux/Mac)
   source venv/bin/activate
   
   # Активация (Windows)
   venv\Scripts\activate
   
   # Установка
   pip install evolution-openai 