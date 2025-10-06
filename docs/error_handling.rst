Обработка ошибок
================

Evolution OpenAI предоставляет комплексную систему обработки ошибок для различных сценариев использования.

Типы ошибок
-----------

Иерархия исключений
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   EvolutionOpenAIError (базовый класс)
   ├── APIError (ошибки API)
   │   ├── APIStatusError (HTTP ошибки)
   │   │   ├── BadRequestError (400)
   │   │   ├── AuthenticationError (401)
   │   │   ├── PermissionDeniedError (403)
   │   │   ├── NotFoundError (404)
   │   │   ├── ConflictError (409)
   │   │   ├── UnprocessableEntityError (422)
   │   │   ├── RateLimitError (429)
   │   │   └── InternalServerError (500+)
   │   ├── APIConnectionError (сетевые ошибки)
   │   └── APITimeoutError (таймауты)
   └── InvalidRequestError (некорректные параметры)

Базовая обработка ошибок
------------------------

Простой try-except
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import EvolutionOpenAI
   from evolution_openai.exceptions import EvolutionOpenAIError

   client = EvolutionOpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

   try:
       response = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Привет!"}],
           max_tokens=100
       )
       print(response.choices[0].message.content)
       
   except EvolutionOpenAIError as e:
       print(f"Ошибка OpenAI: {e}")
   except Exception as e:
       print(f"Неожиданная ошибка: {e}")

Детальная обработка ошибок
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai.exceptions import (
       AuthenticationError,
       RateLimitError,
       APIConnectionError,
       APITimeoutError,
       InternalServerError
   )

   try:
       response = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Тест"}],
           max_tokens=100
       )
       
   except AuthenticationError as e:
       print(f"Ошибка аутентификации: {e}")
       print("Проверьте Key ID и Secret")
       
   except RateLimitError as e:
       print(f"Превышен лимит запросов: {e}")
       print("Подождите перед следующим запросом")
       
   except APIConnectionError as e:
       print(f"Ошибка подключения: {e}")
       print("Проверьте интернет соединение")
       
   except APITimeoutError as e:
       print(f"Таймаут запроса: {e}")
       print("Попробуйте увеличить timeout")
       
   except InternalServerError as e:
       print(f"Ошибка сервера: {e}")
       print("Попробуйте позже")
       
   except EvolutionOpenAIError as e:
       print(f"Другая ошибка API: {e}")

Анализ ошибок
-------------

Получение подробной информации
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       response = client.chat.completions.create(
           model="invalid-model",
           messages=[{"role": "user", "content": "Тест"}]
       )
       
   except EvolutionOpenAIError as e:
       print(f"Ошибка: {e}")
       print(f"Тип: {type(e).__name__}")
       
       # Дополнительная информация об ошибке
       if hasattr(e, 'status_code'):
           print(f"HTTP статус: {e.status_code}")
       
       if hasattr(e, 'request_id'):
           print(f"Request ID: {e.request_id}")
       
       if hasattr(e, 'body'):
           print(f"Тело ответа: {e.body}")

Логирование ошибок
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   # Настройка логирования
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)

   def safe_api_call(client, messages, **kwargs):
       try:
           response = client.chat.completions.create(
               messages=messages,
               **kwargs
           )
           logger.info(f"Успешный запрос, токенов: {response.usage.total_tokens}")
           return response
           
       except AuthenticationError as e:
           logger.error(f"Ошибка аутентификации: {e}")
           raise
           
       except RateLimitError as e:
           logger.warning(f"Rate limit: {e}")
           raise
           
       except APIConnectionError as e:
           logger.error(f"Сетевая ошибка: {e}")
           raise
           
       except EvolutionOpenAIError as e:
           logger.error(f"API ошибка: {e}")
           raise

Retry логика
------------

Простой retry
~~~~~~~~~~~~~

.. code-block:: python

   import time
   import random

   def simple_retry(func, max_retries=3, delay=1):
       for attempt in range(max_retries):
           try:
               return func()
           except (APIConnectionError, APITimeoutError, InternalServerError) as e:
               if attempt == max_retries - 1:
                   raise
               
               wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
               print(f"Попытка {attempt + 1} неудачна, ждем {wait_time:.1f}с")
               time.sleep(wait_time)

   # Использование
   def make_request():
       return client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Тест"}],
           max_tokens=50
       )

   try:
       response = simple_retry(make_request, max_retries=3)
       print(response.choices[0].message.content)
   except EvolutionOpenAIError as e:
       print(f"Все попытки неудачны: {e}")

Продвинутый retry с backoff
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import random
   from functools import wraps

   def retry_with_backoff(
       max_retries=3,
       initial_delay=1,
       max_delay=60,
       exponential_base=2,
       jitter=True,
       retry_on=None
   ):
       if retry_on is None:
           retry_on = (APIConnectionError, APITimeoutError, InternalServerError)
       
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               for attempt in range(max_retries):
                   try:
                       return func(*args, **kwargs)
                   except retry_on as e:
                       if attempt == max_retries - 1:
                           raise
                       
                       delay = min(
                           initial_delay * (exponential_base ** attempt),
                           max_delay
                       )
                       
                       if jitter:
                           delay += random.uniform(0, delay * 0.1)
                       
                       print(f"Попытка {attempt + 1} неудачна: {e}")
                       print(f"Повтор через {delay:.1f} секунд")
                       time.sleep(delay)
               
               return None  # Не должно дойти сюда
           
           return wrapper
       return decorator

   # Использование
   @retry_with_backoff(max_retries=5, initial_delay=2)
   def reliable_request(messages):
       return client.chat.completions.create(
           model="default",
           messages=messages,
           max_tokens=100
       )

   try:
       response = reliable_request([{"role": "user", "content": "Тест"}])
       print(response.choices[0].message.content)
   except EvolutionOpenAIError as e:
       print(f"Финальная ошибка: {e}")

Обработка Rate Limits
---------------------

Автоматическое ожидание
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def handle_rate_limit(client, messages, **kwargs):
       while True:
           try:
               return client.chat.completions.create(
                   messages=messages,
                   **kwargs
               )
           except RateLimitError as e:
               # Извлекаем время ожидания из заголовков
               retry_after = getattr(e, 'retry_after', None)
               if retry_after:
                   wait_time = int(retry_after)
               else:
                   wait_time = 60  # По умолчанию 60 секунд
               
               print(f"Rate limit достигнут, ждем {wait_time} секунд")
               time.sleep(wait_time)

Очередь с rate limiting
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from asyncio import Queue
   import time

   class RateLimitedQueue:
       def __init__(self, rate_per_minute=60):
           self.rate_per_minute = rate_per_minute
           self.requests = []
           self.lock = asyncio.Lock()
       
       async def wait_if_needed(self):
           async with self.lock:
               now = time.time()
               
               # Удаляем старые запросы (старше минуты)
               self.requests = [req_time for req_time in self.requests 
                              if now - req_time < 60]
               
               # Если достигли лимита, ждем
               if len(self.requests) >= self.rate_per_minute:
                   oldest_request = min(self.requests)
                   wait_time = 60 - (now - oldest_request)
                   if wait_time > 0:
                       await asyncio.sleep(wait_time)
               
               # Добавляем текущий запрос
               self.requests.append(now)

   # Использование
   rate_limiter = RateLimitedQueue(rate_per_minute=50)

   async def rate_limited_request(client, messages):
       await rate_limiter.wait_if_needed()
       return await client.chat.completions.create(
           model="default",
           messages=messages,
           max_tokens=100
       )

Валидация запросов
------------------

Предварительная проверка
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_request(messages, max_tokens=None, model=None):
       """Валидация параметров запроса"""
       errors = []
       
       # Проверка сообщений
       if not messages:
           errors.append("Сообщения не могут быть пустыми")
       
       if not isinstance(messages, list):
           errors.append("Сообщения должны быть списком")
       
       for i, message in enumerate(messages):
           if not isinstance(message, dict):
               errors.append(f"Сообщение {i} должно быть словарем")
               continue
           
           if 'role' not in message:
               errors.append(f"Сообщение {i} должно содержать 'role'")
           
           if 'content' not in message:
               errors.append(f"Сообщение {i} должно содержать 'content'")
           
           if message.get('role') not in ['system', 'user', 'assistant']:
               errors.append(f"Неверная роль в сообщении {i}")
       
       # Проверка max_tokens
       if max_tokens is not None:
           if not isinstance(max_tokens, int) or max_tokens <= 0:
               errors.append("max_tokens должно быть положительным числом")
           
           if max_tokens > 4096:  # Примерный лимит
               errors.append("max_tokens слишком большой")
       
       # Проверка модели
       if model and not isinstance(model, str):
           errors.append("model должно быть строкой")
       
       return errors

   def safe_completion(client, messages, **kwargs):
       # Валидация
       errors = validate_request(messages, kwargs.get('max_tokens'))
       if errors:
           raise ValueError(f"Ошибки валидации: {'; '.join(errors)}")
       
       # Запрос
       try:
           return client.chat.completions.create(
               messages=messages,
               **kwargs
           )
       except EvolutionOpenAIError as e:
           print(f"API ошибка: {e}")
           raise

Circuit Breaker Pattern
-----------------------

.. code-block:: python

   import time
   from enum import Enum

   class CircuitState(Enum):
       CLOSED = "closed"        # Нормальная работа
       OPEN = "open"           # Ошибки, запросы блокируются
       HALF_OPEN = "half_open" # Тестирование восстановления

   class CircuitBreaker:
       def __init__(self, failure_threshold=5, timeout=60):
           self.failure_threshold = failure_threshold
           self.timeout = timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED
       
       def call(self, func, *args, **kwargs):
           if self.state == CircuitState.OPEN:
               if self._should_attempt_reset():
                   self.state = CircuitState.HALF_OPEN
               else:
                   raise Exception("Circuit breaker is OPEN")
           
           try:
               result = func(*args, **kwargs)
               self._on_success()
               return result
           except Exception as e:
               self._on_failure()
               raise
       
       def _should_attempt_reset(self):
           return (time.time() - self.last_failure_time) >= self.timeout
       
       def _on_success(self):
           self.failure_count = 0
           self.state = CircuitState.CLOSED
       
       def _on_failure(self):
           self.failure_count += 1
           self.last_failure_time = time.time()
           
           if self.failure_count >= self.failure_threshold:
               self.state = CircuitState.OPEN

   # Использование
   circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

   def protected_request(messages):
       def make_request():
           return client.chat.completions.create(
               model="default",
               messages=messages,
               max_tokens=100
           )
       
       return circuit_breaker.call(make_request)

   # Тестирование
   for i in range(10):
       try:
           response = protected_request([{"role": "user", "content": f"Тест {i}"}])
           print(f"Запрос {i}: Успех")
       except Exception as e:
           print(f"Запрос {i}: Ошибка - {e}")

Мониторинг и метрики
--------------------

Сбор метрик ошибок
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from collections import defaultdict, deque
   import time

   class ErrorMetrics:
       def __init__(self, window_size=100):
           self.errors = defaultdict(int)
           self.error_history = deque(maxlen=window_size)
           self.total_requests = 0
           self.start_time = time.time()
       
       def record_request(self, success=True, error_type=None):
           self.total_requests += 1
           
           if not success and error_type:
               self.errors[error_type] += 1
               self.error_history.append({
                   'timestamp': time.time(),
                   'error_type': error_type
               })
       
       def get_error_rate(self):
           if self.total_requests == 0:
               return 0.0
           return sum(self.errors.values()) / self.total_requests
       
       def get_recent_error_rate(self, minutes=5):
           cutoff = time.time() - (minutes * 60)
           recent_errors = [err for err in self.error_history 
                          if err['timestamp'] > cutoff]
           
           if not recent_errors:
               return 0.0
           
           return len(recent_errors) / max(1, self.total_requests)
       
       def get_stats(self):
           return {
               'total_requests': self.total_requests,
               'total_errors': sum(self.errors.values()),
               'error_rate': self.get_error_rate(),
               'recent_error_rate': self.get_recent_error_rate(),
               'errors_by_type': dict(self.errors),
               'uptime': time.time() - self.start_time
           }

   # Использование
   metrics = ErrorMetrics()

   def monitored_request(messages):
       try:
           response = client.chat.completions.create(
               model="default",
               messages=messages,
               max_tokens=100
           )
           metrics.record_request(success=True)
           return response
       except EvolutionOpenAIError as e:
           error_type = type(e).__name__
           metrics.record_request(success=False, error_type=error_type)
           raise

   # Периодический отчет
   def print_metrics():
       stats = metrics.get_stats()
       print(f"Статистика:")
       print(f"  Всего запросов: {stats['total_requests']}")
       print(f"  Ошибок: {stats['total_errors']}")
       print(f"  Процент ошибок: {stats['error_rate']:.2%}")
       print(f"  Ошибки по типам: {stats['errors_by_type']}")

Лучшие практики
---------------

1. **Всегда обрабатывайте исключения** специфично к типу ошибки
2. **Используйте retry логику** для временных ошибок
3. **Логируйте ошибки** с достаточным контекстом
4. **Валидируйте входные данные** до отправки запроса
5. **Мониторьте метрики ошибок** в продакшене
6. **Реализуйте circuit breaker** для критичных сервисов
7. **Предоставляйте fallback** механизмы
8. **Настройте алерты** на критичные ошибки
9. **Документируйте** возможные ошибки для пользователей
10. **Тестируйте** сценарии ошибок в тестах 