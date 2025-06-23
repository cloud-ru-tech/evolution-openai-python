"""
Исключения для Evolution OpenAI
"""

from typing import Optional


class EvolutionSDKError(Exception):
    """Базовое исключение для всех ошибок Evolution SDK"""

    pass


class EvolutionAuthError(EvolutionSDKError):
    """Ошибка авторизации в Cloud.ru"""

    def __init__(
        self, message: str, status_code: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class EvolutionTokenError(EvolutionSDKError):
    """Ошибка при работе с токенами"""

    def __init__(self, message: str, token_expired: bool = False) -> None:
        super().__init__(message)
        self.token_expired = token_expired


class EvolutionConfigError(EvolutionSDKError):
    """Ошибка конфигурации SDK"""

    pass


class EvolutionNetworkError(EvolutionSDKError):
    """Сетевая ошибка при обращении к Cloud.ru API"""

    def __init__(
        self, message: str, original_error: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.original_error = original_error
