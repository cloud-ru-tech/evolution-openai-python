Асинхронное использование
=========================

Evolution OpenAI полностью поддерживает асинхронные операции с использованием async/await.

Основы асинхронной работы
-------------------------

Инициализация асинхронного клиента
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from evolution_openai import EvolutionAsyncOpenAI

   async def main():
       client = EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       )

       # Ваш код здесь
       
       await client.close()  # Важно закрывать клиент

   asyncio.run(main())

Базовый асинхронный запрос
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def simple_request():
       client = EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret", 
           base_url="https://your-endpoint.cloud.ru/v1"
       )
       
       response = await client.chat.completions.create(
           model="default",
           messages=[
               {"role": "system", "content": "Ты полезный помощник."},
               {"role": "user", "content": "Что такое асинхронное программирование?"}
           ],
           max_tokens=200
       )
       
       print(response.choices[0].message.content)
       await client.close()

Context Manager
---------------

Рекомендуемый способ использования async клиента:

.. code-block:: python

   async def with_context_manager():
       async with EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           response = await client.chat.completions.create(
               model="default",
               messages=[{"role": "user", "content": "Привет!"}],
               max_tokens=50
           )
           
           print(response.choices[0].message.content)
       # Клиент автоматически закрывается

Параллельные запросы
--------------------

Одновременная обработка нескольких запросов
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def parallel_requests():
       async with EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           # Создаем задачи для параллельного выполнения
           tasks = [
               client.chat.completions.create(
                   model="default",
                   messages=[{"role": "user", "content": f"Вопрос {i}"}],
                   max_tokens=50
               )
               for i in range(5)
           ]
           
           # Выполняем все запросы параллельно
           responses = await asyncio.gather(*tasks)
           
           for i, response in enumerate(responses):
               print(f"Ответ {i}: {response.choices[0].message.content}")

Обработка с семафором
~~~~~~~~~~~~~~~~~~~~~

Ограничение количества одновременных запросов:

.. code-block:: python

   async def limited_parallel_requests():
       # Ограничиваем до 3 одновременных запросов
       semaphore = asyncio.Semaphore(3)
       
       async def single_request(client, prompt, index):
           async with semaphore:
               print(f"Запрос {index} начался")
               response = await client.chat.completions.create(
                   model="default",
                   messages=[{"role": "user", "content": prompt}],
                   max_tokens=50
               )
               print(f"Запрос {index} завершен")
               return response.choices[0].message.content
       
       async with EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           prompts = [f"Расскажи про тему {i}" for i in range(10)]
           
           tasks = [
               single_request(client, prompt, i) 
               for i, prompt in enumerate(prompts)
           ]
           
           results = await asyncio.gather(*tasks)
           
           for i, result in enumerate(results):
               print(f"Результат {i}: {result}")

Асинхронный Streaming
---------------------

Потоковая передача с async/await
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def async_streaming():
       async with EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           stream = await client.chat.completions.create(
               model="default",
               messages=[{
                   "role": "user", 
                   "content": "Расскажи длинную историю"
               }],
               stream=True,
               max_tokens=300
           )
           
           async for chunk in stream:
               if chunk.choices[0].delta.content:
                   print(chunk.choices[0].delta.content, end="", flush=True)
           
           print()  # Новая строка в конце

Обработка ошибок в асинхронном коде
-----------------------------------

Try-except с async
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def error_handling_example():
       try:
           async with EvolutionAsyncOpenAI(
               key_id="your_key_id",
               secret="your_secret",
               base_url="https://your-endpoint.cloud.ru/v1"
           ) as client:
               
               response = await client.chat.completions.create(
                   model="default",
                   messages=[{"role": "user", "content": "Тест"}],
                   max_tokens=50
               )
               
               print(response.choices[0].message.content)
               
       except asyncio.TimeoutError:
           print("Превышено время ожидания")
       except Exception as e:
           print(f"Ошибка: {e}")

Graceful shutdown
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import signal

   class AsyncChatBot:
       def __init__(self):
           self.client = None
           self.running = True
       
       async def start(self):
           self.client = EvolutionAsyncOpenAI(
               key_id="your_key_id",
               secret="your_secret",
               base_url="https://your-endpoint.cloud.ru/v1"
           )
           
           # Обработчик сигналов
           signal.signal(signal.SIGINT, self.signal_handler)
           signal.signal(signal.SIGTERM, self.signal_handler)
           
           try:
               while self.running:
                   # Основной цикл работы
                   await self.process_requests()
                   await asyncio.sleep(1)
           finally:
               await self.cleanup()
       
       def signal_handler(self, signum, frame):
           print(f"Получен сигнал {signum}, останавливаюсь...")
           self.running = False
       
       async def process_requests(self):
           # Логика обработки запросов
           pass
       
       async def cleanup(self):
           if self.client:
               await self.client.close()
               print("Клиент закрыт")

Продвинутые паттерны
--------------------

Пул асинхронных клиентов
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AsyncClientPool:
       def __init__(self, pool_size=5):
           self.pool_size = pool_size
           self.clients = []
           self.semaphore = asyncio.Semaphore(pool_size)
       
       async def __aenter__(self):
           for i in range(self.pool_size):
               client = EvolutionAsyncOpenAI(
                   key_id="your_key_id",
                   secret="your_secret",
                   base_url="https://your-endpoint.cloud.ru/v1"
               )
               self.clients.append(client)
           return self
       
       async def __aexit__(self, exc_type, exc_val, exc_tb):
           for client in self.clients:
               await client.close()
       
       async def request(self, messages, **kwargs):
           async with self.semaphore:
               # Простое round-robin
               client = self.clients[len(self.clients) % self.pool_size]
               return await client.chat.completions.create(
                   messages=messages, **kwargs
               )

   # Использование
   async def use_pool():
       async with AsyncClientPool(pool_size=3) as pool:
           tasks = [
               pool.request([{"role": "user", "content": f"Запрос {i}"}])
               for i in range(10)
           ]
           responses = await asyncio.gather(*tasks)

Асинхронная очередь задач
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def worker(queue, client, worker_id):
       """Воркер для обработки задач из очереди"""
       while True:
           try:
               # Получаем задачу из очереди
               task = await queue.get()
               
               if task is None:  # Сигнал завершения
                   break
               
               print(f"Воркер {worker_id} обрабатывает: {task['prompt']}")
               
               response = await client.chat.completions.create(
                   model="default",
                   messages=[{"role": "user", "content": task['prompt']}],
                   max_tokens=100
               )
               
               # Сохраняем результат
               task['result'] = response.choices[0].message.content
               task['done'].set()  # Сигнализируем о завершении
               
               queue.task_done()
               
           except Exception as e:
               print(f"Ошибка в воркере {worker_id}: {e}")
               queue.task_done()

   async def queue_example():
       # Создаем очередь и клиент
       queue = asyncio.Queue(maxsize=20)
       
       async with EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           # Запускаем воркеров
           workers = [
               asyncio.create_task(worker(queue, client, i))
               for i in range(3)
           ]
           
           # Добавляем задачи
           tasks = []
           for i in range(10):
               task = {
                   'prompt': f"Вопрос номер {i}",
                   'done': asyncio.Event(),
                   'result': None
               }
               tasks.append(task)
               await queue.put(task)
           
           # Ждем завершения всех задач
           for task in tasks:
               await task['done'].wait()
               print(f"Результат: {task['result']}")
           
           # Останавливаем воркеров
           for _ in workers:
               await queue.put(None)
           
           await asyncio.gather(*workers)

Интеграция с веб-фреймворками
-----------------------------

FastAPI пример
~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI
   from pydantic import BaseModel
   from evolution_openai import EvolutionAsyncOpenAI

   app = FastAPI()

   class ChatRequest(BaseModel):
       message: str
       max_tokens: int = 100

   class ChatResponse(BaseModel):
       response: str

   # Глобальный клиент (инициализируется при старте)
   client = None

   @app.on_event("startup")
   async def startup_event():
       global client
       client = EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       )

   @app.on_event("shutdown")
   async def shutdown_event():
       global client
       if client:
           await client.close()

   @app.post("/chat", response_model=ChatResponse)
   async def chat_endpoint(request: ChatRequest):
       response = await client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": request.message}],
           max_tokens=request.max_tokens
       )
       
       return ChatResponse(
           response=response.choices[0].message.content
       )

aiohttp пример
~~~~~~~~~~~~~~

.. code-block:: python

   from aiohttp import web
   from evolution_openai import EvolutionAsyncOpenAI

   async def chat_handler(request):
       data = await request.json()
       message = data.get('message', '')
       
       client = request.app['openai_client']
       
       response = await client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": message}],
           max_tokens=100
       )
       
       return web.json_response({
           'response': response.choices[0].message.content
       })

   async def init_app():
       app = web.Application()
       
       # Инициализация клиента
       app['openai_client'] = EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       )
       
       app.router.add_post('/chat', chat_handler)
       
       return app

   async def cleanup(app):
       await app['openai_client'].close()

   if __name__ == '__main__':
       app = init_app()
       app.on_cleanup.append(cleanup)
       web.run_app(app, host='127.0.0.1', port=8080)

Лучшие практики
---------------

1. **Всегда используйте context manager** или вручную закрывайте клиенты
2. **Ограничивайте concurrency** семафорами во избежание перегрузки
3. **Обрабатывайте исключения** специфичные для async кода
4. **Используйте пулы клиентов** для высоконагруженных приложений
5. **Реализуйте graceful shutdown** в долгоработающих сервисах
6. **Мониторьте производительность** и bottlenecks в async коде 