Streaming API
=============

Evolution OpenAI поддерживает потоковую передачу ответов (streaming), позволяя получать части ответа по мере их генерации.

Что такое Streaming
-------------------

Streaming позволяет:

- **Получать ответы по частям** вместо ожидания полного ответа
- **Улучшить UX** - пользователь видит прогресс генерации
- **Снизить воспринимаемую задержку** - первые слова появляются быстрее
- **Обрабатывать длинные ответы** эффективно

Базовое использование
---------------------

Синхронный streaming
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from evolution_openai import EvolutionOpenAI

   client = EvolutionOpenAI(
       key_id="your_key_id",
       secret="your_secret",
       base_url="https://your-endpoint.cloud.ru/v1"
   )

   stream = client.chat.completions.create(
       model="default",
       messages=[{
           "role": "user",
           "content": "Расскажи длинную историю про космос"
       }],
       stream=True,  # Включаем streaming
       max_tokens=300
   )

   # Обрабатываем каждый chunk
   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end="", flush=True)

   print()  # Новая строка в конце

Асинхронный streaming
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from evolution_openai import EvolutionAsyncOpenAI

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
                   "content": "Объясни квантовую физику подробно"
               }],
               stream=True,
               max_tokens=400
           )
           
           async for chunk in stream:
               if chunk.choices[0].delta.content:
                   print(chunk.choices[0].delta.content, end="", flush=True)
           
           print()

   asyncio.run(async_streaming())

Структура streaming chunk
-------------------------

Каждый chunk содержит следующие поля:

.. code-block:: python

   chunk = {
       "id": "chatcmpl-123",
       "object": "chat.completion.chunk",
       "created": 1677652288,
       "model": "default",
       "choices": [
           {
               "index": 0,
               "delta": {
                   "role": "assistant",  # Только в первом chunk
                   "content": "Привет"   # Часть ответа
               },
               "finish_reason": None  # null пока не закончено
           }
       ]
   }

Обработка различных типов chunk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   stream = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Привет!"}],
       stream=True
   )

   full_response = ""
   
   for chunk in stream:
       choice = chunk.choices[0]
       delta = choice.delta
       
       # Первый chunk с ролью
       if delta.role:
           print(f"Роль: {delta.role}")
       
       # Контент
       if delta.content:
           content = delta.content
           print(content, end="", flush=True)
           full_response += content
       
       # Проверяем причину завершения
       if choice.finish_reason:
           print(f"\nЗавершено: {choice.finish_reason}")
           break

   print(f"\nПолный ответ: {full_response}")

Продвинутые возможности
-----------------------

Streaming с метаданными
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time

   def streaming_with_stats():
       start_time = time.time()
       chunk_count = 0
       total_content = ""
       
       stream = client.chat.completions.create(
           model="default",
           messages=[{
               "role": "user",
               "content": "Напиши подробный рассказ про будущее"
           }],
           stream=True,
           max_tokens=500
       )
       
       for chunk in stream:
           chunk_count += 1
           
           if chunk.choices[0].delta.content:
               content = chunk.choices[0].delta.content
               total_content += content
               print(content, end="", flush=True)
       
       end_time = time.time()
       
       print(f"\n\nСтатистика:")
       print(f"Время: {end_time - start_time:.2f} сек")
       print(f"Chunks: {chunk_count}")
       print(f"Символов: {len(total_content)}")
       print(f"Скорость: {len(total_content)/(end_time-start_time):.1f} симв/сек")

Stop sequences в streaming
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   stream = client.chat.completions.create(
       model="default",
       messages=[{
           "role": "system",
           "content": "Создавай список и заканчивай словом КОНЕЦ"
       }, {
           "role": "user",
           "content": "Дай советы по изучению Python"
       }],
       stream=True,
       stop=["КОНЕЦ", "END"],  # Остановочные последовательности
       max_tokens=300
   )

   for chunk in stream:
       choice = chunk.choices[0]
       
       if choice.delta.content:
           print(choice.delta.content, end="", flush=True)
       
       # Проверяем причину остановки
       if choice.finish_reason == "stop":
           print("\n[Остановлено по stop sequence]")
       elif choice.finish_reason == "length":
           print("\n[Достигнут лимит токенов]")

Обработка ошибок в streaming
----------------------------

Базовая обработка ошибок
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       stream = client.chat.completions.create(
           model="default",
           messages=[{"role": "user", "content": "Тест"}],
           stream=True
       )
       
       for chunk in stream:
           if chunk.choices[0].delta.content:
               print(chunk.choices[0].delta.content, end="")
               
   except Exception as e:
       print(f"\nОшибка streaming: {e}")

Продвинутая обработка ошибок
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from evolution_openai.exceptions import EvolutionOpenAIError

   def robust_streaming(messages, max_retries=3):
       for attempt in range(max_retries):
           try:
               stream = client.chat.completions.create(
                   model="default",
                   messages=messages,
                   stream=True,
                   timeout=30
               )
               
               content_buffer = ""
               
               for chunk in stream:
                   if chunk.choices[0].delta.content:
                       content = chunk.choices[0].delta.content
                       print(content, end="", flush=True)
                       content_buffer += content
               
               return content_buffer  # Успешно завершено
               
           except EvolutionOpenAIError as e:
               print(f"\nОшибка API (попытка {attempt + 1}): {e}")
               if attempt < max_retries - 1:
                   time.sleep(2 ** attempt)  # Exponential backoff
               
           except Exception as e:
               print(f"\nНеожиданная ошибка: {e}")
               break
       
       return None  # Все попытки неудачны

Streaming в веб-приложениях
---------------------------

Server-Sent Events (SSE)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask, Response
   import json

   app = Flask(__name__)

   @app.route('/stream-chat')
   def stream_chat():
       message = request.args.get('message', 'Привет!')
       
       def generate():
           try:
               stream = client.chat.completions.create(
                   model="default",
                   messages=[{"role": "user", "content": message}],
                   stream=True,
                   max_tokens=200
               )
               
               for chunk in stream:
                   if chunk.choices[0].delta.content:
                       data = {
                           'content': chunk.choices[0].delta.content,
                           'done': False
                       }
                       yield f"data: {json.dumps(data)}\n\n"
               
               # Сигнал завершения
               yield f"data: {json.dumps({'done': True})}\n\n"
               
           except Exception as e:
               error_data = {'error': str(e), 'done': True}
               yield f"data: {json.dumps(error_data)}\n\n"
       
       return Response(
           generate(),
           mimetype='text/event-stream',
           headers={
               'Cache-Control': 'no-cache',
               'Connection': 'keep-alive'
           }
       )

FastAPI с streaming
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI
   from fastapi.responses import StreamingResponse
   import json

   app = FastAPI()

   @app.get("/stream")
   async def stream_endpoint(message: str = "Привет!"):
       
       async def generate():
           try:
               async with EvolutionAsyncOpenAI(
                   key_id="your_key_id",
                   secret="your_secret",
                   base_url="https://your-endpoint.cloud.ru/v1"
               ) as client:
                   
                   stream = await client.chat.completions.create(
                       model="default",
                       messages=[{"role": "user", "content": message}],
                       stream=True
                   )
                   
                   async for chunk in stream:
                       if chunk.choices[0].delta.content:
                           data = {
                               'content': chunk.choices[0].delta.content,
                               'done': False
                           }
                           yield f"data: {json.dumps(data)}\n\n"
                   
                   yield f"data: {json.dumps({'done': True})}\n\n"
                   
           except Exception as e:
               error_data = {'error': str(e)}
               yield f"data: {json.dumps(error_data)}\n\n"
       
       return StreamingResponse(
           generate(),
           media_type="text/event-stream",
           headers={
               "Cache-Control": "no-cache",
               "Connection": "keep-alive"
           }
       )

Клиентская сторона (JavaScript)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

   <!DOCTYPE html>
   <html>
   <head>
       <title>Streaming Chat</title>
   </head>
   <body>
       <div id="response"></div>
       <button onclick="startStream()">Начать streaming</button>
       
       <script>
       function startStream() {
           const responseDiv = document.getElementById('response');
           responseDiv.innerHTML = '';
           
           const eventSource = new EventSource('/stream-chat?message=Расскажи анекдот');
           
           eventSource.onmessage = function(event) {
               const data = JSON.parse(event.data);
               
               if (data.error) {
                   responseDiv.innerHTML += `<div style="color: red;">Ошибка: ${data.error}</div>`;
                   eventSource.close();
               } else if (data.done) {
                   responseDiv.innerHTML += '<div>✅ Завершено</div>';
                   eventSource.close();
               } else {
                   responseDiv.innerHTML += data.content;
               }
           };
           
           eventSource.onerror = function(event) {
               console.error('SSE error:', event);
               eventSource.close();
           };
       }
       </script>
   </body>
   </html>

Паттерны и лучшие практики
--------------------------

Буферизация для UI
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import threading

   class StreamBuffer:
       def __init__(self, update_callback, buffer_delay=0.1):
           self.buffer = ""
           self.update_callback = update_callback
           self.buffer_delay = buffer_delay
           self.last_update = time.time()
           self.timer = None
       
       def add_content(self, content):
           self.buffer += content
           
           # Обновляем UI не чаще чем buffer_delay
           now = time.time()
           if now - self.last_update >= self.buffer_delay:
               self.flush()
           else:
               # Планируем отложенное обновление
               if self.timer:
                   self.timer.cancel()
               self.timer = threading.Timer(self.buffer_delay, self.flush)
               self.timer.start()
       
       def flush(self):
           if self.buffer:
               self.update_callback(self.buffer)
               self.buffer = ""
               self.last_update = time.time()
           if self.timer:
               self.timer.cancel()
               self.timer = None

   # Использование
   def update_ui(text):
       print(f"UI Update: {text}")

   buffer = StreamBuffer(update_ui, buffer_delay=0.2)

   stream = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Длинный ответ..."}],
       stream=True
   )

   for chunk in stream:
       if chunk.choices[0].delta.content:
           buffer.add_content(chunk.choices[0].delta.content)

   buffer.flush()  # Принудительная отправка остатков

Множественный streaming
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio

   async def multiple_streams():
       async with EvolutionAsyncOpenAI(
           key_id="your_key_id",
           secret="your_secret",
           base_url="https://your-endpoint.cloud.ru/v1"
       ) as client:
           
           questions = [
               "Что такое Python?",
               "Объясни машинное обучение",
               "Расскажи про веб-разработку"
           ]
           
           async def handle_stream(question, stream_id):
               print(f"\n=== Поток {stream_id}: {question} ===")
               
               stream = await client.chat.completions.create(
                   model="default",
                   messages=[{"role": "user", "content": question}],
                   stream=True,
                   max_tokens=100
               )
               
               async for chunk in stream:
                   if chunk.choices[0].delta.content:
                       content = chunk.choices[0].delta.content
                       print(f"[{stream_id}] {content}", end="", flush=True)
               
               print(f"\n=== Поток {stream_id} завершен ===")
           
           # Запускаем все потоки параллельно
           tasks = [
               handle_stream(question, i)
               for i, question in enumerate(questions)
           ]
           
           await asyncio.gather(*tasks)

   asyncio.run(multiple_streams())

Мониторинг производительности
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from collections import deque

   class StreamingMetrics:
       def __init__(self, window_size=100):
           self.chunks = deque(maxlen=window_size)
           self.start_time = None
           self.first_chunk_time = None
           self.total_chars = 0
       
       def start(self):
           self.start_time = time.time()
       
       def add_chunk(self, chunk_content):
           now = time.time()
           
           if self.first_chunk_time is None:
               self.first_chunk_time = now
           
           self.chunks.append({
               'timestamp': now,
               'content': chunk_content,
               'length': len(chunk_content)
           })
           
           self.total_chars += len(chunk_content)
       
       def get_stats(self):
           if not self.chunks or not self.start_time:
               return {}
           
           now = time.time()
           total_time = now - self.start_time
           time_to_first_chunk = (self.first_chunk_time - self.start_time 
                                 if self.first_chunk_time else 0)
           
           return {
               'total_time': total_time,
               'time_to_first_chunk': time_to_first_chunk,
               'total_chunks': len(self.chunks),
               'total_chars': self.total_chars,
               'chars_per_second': self.total_chars / total_time if total_time > 0 else 0,
               'chunks_per_second': len(self.chunks) / total_time if total_time > 0 else 0,
               'avg_chunk_size': self.total_chars / len(self.chunks)
           }

   # Использование
   metrics = StreamingMetrics()
   metrics.start()

   stream = client.chat.completions.create(
       model="default",
       messages=[{"role": "user", "content": "Длинный ответ..."}],
       stream=True
   )

   for chunk in stream:
       if chunk.choices[0].delta.content:
           content = chunk.choices[0].delta.content
           metrics.add_chunk(content)
           print(content, end="", flush=True)

   stats = metrics.get_stats()
   print(f"\n\nМетрики streaming:")
   for key, value in stats.items():
       print(f"{key}: {value:.2f}")

Советы по оптимизации
---------------------

1. **Используйте буферизацию** для UI обновлений
2. **Обрабатывайте ошибки gracefully** с retry логикой
3. **Мониторьте производительность** и задержки
4. **Ограничивайте количество** одновременных streams
5. **Правильно закрывайте streams** во избежание утечек ресурсов
6. **Используйте stop sequences** для контроля генерации
7. **Реализуйте cancellation** для длинных операций 