"""
Менеджер токенов для Cloud.ru API
"""

import os
import asyncio
import logging
import threading
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

import requests

try:
    import httpx

    _httpx_available = True
except ImportError:
    httpx = None  # type: ignore[assignment]
    _httpx_available = False

from evolution_openai.exceptions import (
    EvolutionAuthError,
    EvolutionTokenError,
    EvolutionNetworkError,
)

logger = logging.getLogger(__name__)

# Configure logger level from environment (default INFO)
_level_name = os.getenv("LOG_LEVEL", "INFO").strip().upper()
if _level_name == "WARN":
    _level_name = "WARNING"
logger.setLevel(getattr(logging, _level_name, logging.INFO))
_root_logger = logging.getLogger()
if not logger.handlers and not _root_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setLevel(getattr(logging, _level_name, logging.INFO))
    _formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
logger.debug(f"LOG_LEVEL from env: {_level_name}")


class EvolutionTokenManager:
    """Менеджер токенов с автоматическим обновлением"""

    def __init__(
        self,
        key_id: str,
        secret: str,
        token_url: str = "https://iam.api.cloud.ru/api/v1/auth/token",
        buffer_seconds: int = 30,
    ):
        if not key_id or not secret:
            raise EvolutionTokenError(
                "key_id и secret обязательны для инициализации TokenManager"
            )

        self.key_id = key_id
        self.secret = secret
        self.token_url = token_url
        self.buffer_seconds = buffer_seconds
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._lock = threading.Lock()
        self._async_lock: Optional[asyncio.Lock] = None

    def _request_token(self) -> Dict[str, Any]:
        """Запрашивает новый access token"""
        payload = {"keyId": self.key_id, "secret": self.secret}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.token_url, json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise EvolutionAuthError(
                    f"Неверные учетные данные: {e}", status_code=401
                ) from None
            elif e.response.status_code == 403:
                raise EvolutionAuthError(
                    f"Доступ запрещен: {e}", status_code=403
                ) from None
            else:
                raise EvolutionNetworkError(
                    f"HTTP ошибка при получении токена: {e}", original_error=e
                ) from None
        except requests.exceptions.RequestException as e:
            raise EvolutionNetworkError(
                f"Сетевая ошибка при получении токена: {e}", original_error=e
            ) from None
        except Exception as e:
            raise EvolutionTokenError(
                f"Неожиданная ошибка при получении токена: {e}"
            ) from None

    def get_valid_token(self) -> Optional[str]:
        """Возвращает валидный токен, обновляя при необходимости"""
        with self._lock:
            now = datetime.now()

            should_refresh = (
                self.access_token is None
                or self.token_expires_at is None
                or now
                >= (
                    self.token_expires_at
                    - timedelta(seconds=self.buffer_seconds)
                )
            )

            if should_refresh:
                had_token_before = self.access_token is not None
                logger.info("Обновление access token...")
                try:
                    token_data = self._request_token()

                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = now + timedelta(seconds=expires_in)

                    logger.info(
                        f"Токен обновлен, действителен до: "
                        f"{self.token_expires_at}"
                    )
                    if had_token_before and self.access_token:
                        logger.debug(
                            f"[token] refreshed prefix={self.access_token[:16]}..."
                        )
                except KeyError as e:
                    raise EvolutionTokenError(
                        f"Неожиданный формат ответа от сервера токенов: {e}"
                    ) from None

            return self.access_token

    def invalidate_token(self) -> None:
        """Принудительно делает токен недействительным"""
        with self._lock:
            self.access_token = None
            self.token_expires_at = None
            logger.info("Токен принудительно аннулирован")

    def is_token_valid(self) -> bool:
        """Проверяет, действителен ли текущий токен"""
        if self.access_token is None or self.token_expires_at is None:
            return False

        now = datetime.now()
        return now < (
            self.token_expires_at - timedelta(seconds=self.buffer_seconds)
        )

    def get_token_info(self) -> Dict[str, Any]:
        """Возвращает информацию о токене"""
        return {
            "has_token": self.access_token is not None,
            "expires_at": self.token_expires_at.isoformat()
            if self.token_expires_at
            else None,
            "is_valid": self.is_token_valid(),
            "buffer_seconds": self.buffer_seconds,
        }

    async def _request_token_async(self) -> Dict[str, Any]:
        """Асинхронно запрашивает новый access token"""
        payload = {"keyId": self.key_id, "secret": self.secret}
        headers = {"Content-Type": "application/json"}

        if _httpx_available and httpx is not None:
            # Используем httpx для асинхронных запросов
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.token_url, json=payload, headers=headers
                    )
                    response.raise_for_status()
                    return response.json()  # type: ignore[no-any-return]

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise EvolutionAuthError(
                        f"Неверные учетные данные: {e}", status_code=401
                    ) from None
                elif e.response.status_code == 403:
                    raise EvolutionAuthError(
                        f"Доступ запрещен: {e}", status_code=403
                    ) from None
                else:
                    raise EvolutionNetworkError(
                        f"HTTP ошибка при получении токена: {e}",
                        original_error=e,
                    ) from None
            except httpx.RequestError as e:
                raise EvolutionNetworkError(
                    f"Сетевая ошибка при получении токена: {e}",
                    original_error=e,
                ) from None
            except Exception as e:
                raise EvolutionTokenError(
                    f"Неожиданная ошибка при получении токена: {e}"
                ) from None
        else:
            # Fallback: используем синхронный requests в отдельном потоке
            logger.warning(
                "httpx не установлен, используется синхронный fallback. "
                "Установите httpx для лучшей производительности: pip install httpx"
            )
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._request_token)

    async def get_valid_token_async(self) -> Optional[str]:
        """Асинхронно возвращает валидный токен, обновляя при необходимости"""
        # Ленивая инициализация async lock
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()

        async with self._async_lock:
            now = datetime.now()

            should_refresh = (
                self.access_token is None
                or self.token_expires_at is None
                or now
                >= (
                    self.token_expires_at
                    - timedelta(seconds=self.buffer_seconds)
                )
            )

            if should_refresh:
                had_token_before = self.access_token is not None
                logger.info("Обновление access token (async)...")
                try:
                    token_data = await self._request_token_async()

                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = now + timedelta(seconds=expires_in)

                    logger.info(
                        f"Токен обновлен (async), действителен до: "
                        f"{self.token_expires_at}"
                    )
                    if had_token_before and self.access_token:
                        logger.debug(
                            f"[token] refreshed (async) prefix={self.access_token[:16]}..."
                        )
                except KeyError as e:
                    raise EvolutionTokenError(
                        f"Неожиданный формат ответа от сервера токенов: {e}"
                    ) from None

            return self.access_token
