"""
Менеджер токенов для Cloud.ru API
"""

import logging
import threading
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

import requests

from evolution_openai.exceptions import (
    EvolutionAuthError,
    EvolutionTokenError,
    EvolutionNetworkError,
)

logger = logging.getLogger(__name__)


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
