import asyncio
import os
from evolution_openai import create_async_client

key_id = os.environ["KEY_ID"]
secret = os.environ["SECRET"]
project = os.environ["PROJECT"]
url = "https://foundation-models.api.cloud.ru/api/gigacube/openai/v1"

MODEL: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
USER_PROMPT: str = "Как написать хороший код? Не более 100 слов"
params = {
    "model": MODEL,
    "max_tokens": 5000,
    "presence_penalty": 0,
    "top_p": 0.95,
    "temperature": 0.5,
    "messages": [
        {"role": "user", "content": USER_PROMPT},
    ],
}

async def main():
    client = create_async_client(key_id=key_id, secret=secret, base_url=url, project=project)
    response = await client.chat.completions.create(**params)
    content = response.choices[0].message.content
    print(content)

if __name__ == '__main__':
    asyncio.run(main())