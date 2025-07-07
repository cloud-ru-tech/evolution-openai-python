"""
Основные клиенты Evolution OpenAI
"""

import logging
from typing import Any, Dict, Type, Union, Optional
from typing_extensions import override

from evolution_openai.token_manager import EvolutionTokenManager

# Fallback base classes to ensure names are always defined
_BaseOpenAI: Type[Any] = object  # type: ignore[reportGeneralTypeIssues]
_BaseAsyncOpenAI: Type[Any] = object  # type: ignore[reportGeneralTypeIssues]

try:
    import openai
    from openai import OpenAI as _BaseOpenAI, AsyncOpenAI as _BaseAsyncOpenAI

    OPENAI_AVAILABLE = True

    # Проверяем версию OpenAI SDK
    openai_version = openai.__version__
    version_parts = openai_version.split(".")
    major_version = int(version_parts[0])
    minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0

    if major_version < 1 or (major_version == 1 and minor_version < 30):
        raise ImportError(
            f"OpenAI SDK version {openai_version} is not supported. "
            "Please upgrade to version 1.30.0 or later: "
            "pip install openai>=1.30.0"
        )

    # В новых версиях project всегда поддерживается
    SUPPORTS_PROJECT = True

except ImportError:
    # Если OpenAI SDK не установлен или версия неподходящая
    _BaseOpenAIFallback: Type[Any] = object  # type: ignore[reportGeneralTypeIssues]
    _BaseAsyncOpenAIFallback: Type[Any] = object  # type: ignore[reportGeneralTypeIssues]
    OPENAI_AVAILABLE = False  # type: ignore[assignment]
    SUPPORTS_PROJECT = False  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class EvolutionOpenAI(_BaseOpenAI):  # type: ignore[reportUnknownBaseType,reportUnknownMemberType,reportUnknownArgumentType,misc]
    """
    Evolution OpenAI Client - Полностью совместимый с официальным OpenAI SDK

    Просто замените:
        from openai import OpenAI
        client = OpenAI(api_key="...")

    На:
        from evolution_openai import OpenAI
        client = OpenAI(key_id="...", secret="...", base_url="...")

    И все остальные методы будут работать точно так же!
    """

    def __init__(
        self,
        key_id: str,
        secret: str,
        base_url: str,
        # Параметры совместимые с OpenAI SDK
        api_key: Optional[str] = None,  # Игнорируется
        organization: Optional[str] = None,
        project_id: Optional[str] = None,
        timeout: Union[float, None] = None,
        max_retries: int = 2,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:  # type: ignore[reportUnknownParameterType,reportUnknownMemberType,reportUnknownArgumentType,reportUnknownVariableType]
        # Проверяем что OpenAI SDK установлен
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI SDK required. Install with: pip install openai>=1.30.0"
            )

        # Сохраняем Cloud.ru credentials
        self.key_id = key_id
        self.secret = secret
        self.project_id = project_id

        # Инициализируем token manager
        self.token_manager = EvolutionTokenManager(key_id, secret)

        # Получаем первоначальный токен
        initial_token = self.token_manager.get_valid_token()

        # Подготавливаем заголовки с project_id
        prepared_headers = self._prepare_default_headers(default_headers)

        # Инициализируем родительский OpenAI client
        super().__init__(  # type: ignore[reportUnknownMemberType]
            api_key=initial_token,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=prepared_headers,
            default_query=default_query,
            http_client=http_client,
            **kwargs,
        )

        # Переопределяем _client для автоматического обновления токенов
        self._patch_client()

        # Устанавливаем заголовки после инициализации родительского класса
        self._initialize_headers()

    def _prepare_default_headers(
        self, user_headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Подготавливает заголовки по умолчанию с учетом project_id"""
        headers: Dict[str, str] = {}

        # Добавляем пользовательские заголовки
        if user_headers:
            headers.update(user_headers)

        # Добавляем project_id заголовок если он установлен
        if self.project_id:
            headers["x-project-id"] = self.project_id

        return headers

    def _initialize_headers(self) -> None:
        """Инициализирует заголовки после создания клиента"""
        current_token = self.token_manager.get_valid_token()
        if current_token:
            self._update_auth_headers(current_token)

    def _patch_client(self) -> None:  # type: ignore[reportUnknownMemberType]
        """Патчим client для автоматического обновления токенов"""
        # В новых версиях используется 'request'
        if hasattr(self._client, "request"):  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
            original_request = self._client.request  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
            method_name = "request"
        else:
            logger.warning("Не удалось найти метод request в HTTP клиенте")
            return

        def patched_request(*args: Any, **kwargs: Any) -> Any:  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportUnknownVariableType,reportUnknownReturnType]
            # Обновляем токен перед каждым запросом
            current_token = self.token_manager.get_valid_token()
            self.api_key = current_token or ""  # type: ignore[reportUnknownMemberType]
            self._update_auth_headers(current_token or "")

            try:
                return original_request(*args, **kwargs)
            except Exception as e:
                # Если ошибка авторизации, принудительно обновляем токен
                if self._is_auth_error(e):
                    logger.warning(
                        "Ошибка авторизации, принудительно обновляем токен"
                    )
                    self.token_manager.invalidate_token()
                    new_token = self.token_manager.get_valid_token()
                    self.api_key = new_token or ""  # type: ignore[reportUnknownMemberType]
                    # Повторяем запрос с новым токеном
                    self._update_auth_headers(new_token or "")
                    return original_request(*args, **kwargs)
                else:
                    raise

        # Устанавливаем патченый метод
        setattr(self._client, method_name, patched_request)  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]

    def _update_auth_headers(self, token: str) -> None:
        """Обновляет заголовки авторизации"""
        auth_header = f"Bearer {token}"
        headers_updated = False

        # Пытаемся обновить заголовки различными способами
        if hasattr(self._client, "_auth_headers"):
            self._client._auth_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            # Добавляем project_id заголовок если он установлен
            if self.project_id:
                self._client._auth_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        if hasattr(self._client, "default_headers"):
            self._client.default_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            # Добавляем project_id заголовок если он установлен
            if self.project_id:
                self._client.default_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        # Пытаемся обновить заголовки через _default_headers (для новых версий OpenAI SDK)
        if hasattr(self._client, "_default_headers"):
            self._client._default_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            if self.project_id:
                self._client._default_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        # Обновляем заголовки на уровне самого клиента
        if hasattr(self, "default_headers") and self.default_headers:
            self.default_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            if self.project_id:
                self.default_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        if not headers_updated:
            logger.warning(
                "Не удалось обновить заголовки - структура HTTP клиента не распознана"
            )

    def _is_auth_error(self, error: Exception) -> bool:
        """Проверяет, является ли ошибка связанной с авторизацией"""
        error_str = str(error).lower()
        return any(
            keyword in error_str
            for keyword in [
                "unauthorized",
                "401",
                "authentication",
                "forbidden",
                "403",
            ]
        )

    @property
    def current_token(self) -> Optional[str]:
        """Возвращает текущий действующий токен"""
        return self.token_manager.get_valid_token()

    def refresh_token(self) -> Optional[str]:
        """Принудительно обновляет токен"""
        self.token_manager.invalidate_token()
        return self.token_manager.get_valid_token()

    def get_token_info(self) -> Dict[str, Any]:
        """Возвращает информацию о токене"""
        return self.token_manager.get_token_info()

    def get_request_headers(self) -> Dict[str, str]:
        """Возвращает текущие заголовки запроса для отладки"""
        headers: Dict[str, str] = {}

        # Собираем заголовки из различных источников
        if (
            hasattr(self._client, "_auth_headers")
            and self._client._auth_headers
        ):
            headers.update(self._client._auth_headers)  # type: ignore[reportAttributeAccessIssue]
        if (
            hasattr(self._client, "default_headers")
            and self._client.default_headers
        ):
            headers.update(self._client.default_headers)  # type: ignore[reportAttributeAccessIssue]
        if (
            hasattr(self._client, "_default_headers")
            and self._client._default_headers
        ):
            headers.update(self._client._default_headers)  # type: ignore[reportAttributeAccessIssue]
        if hasattr(self, "default_headers") and self.default_headers:
            headers.update(self.default_headers)  # type: ignore[reportAttributeAccessIssue]

        return headers

    @override
    def with_options(self, **kwargs: Any) -> "EvolutionOpenAI":  # type: ignore[reportUnknownReturnType,misc]
        """Создает новый клиент с дополнительными опциями"""
        # Объединяем текущие параметры с новыми
        options: Dict[str, Any] = {
            "key_id": self.key_id,
            "secret": self.secret,
            "base_url": self.base_url,
            "organization": self.organization,
            "project_id": self.project_id,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": getattr(self, "_client", None),
        }
        options.update(kwargs)
        return EvolutionOpenAI(**options)

    @override
    def __enter__(self) -> "EvolutionOpenAI":  # type: ignore[reportUnknownReturnType,reportUnknownMemberType,misc]
        """Контекстный менеджер - вход"""
        # Вызываем родительский контекстный менеджер если он есть
        if hasattr(super(), "__enter__"):
            super().__enter__()  # type: ignore[reportUnknownMemberType]
        return self

    @override
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:  # type: ignore[reportUnknownReturnType,reportUnknownMemberType,misc]
        """Контекстный менеджер - выход"""
        try:
            # Вызываем родительский контекстный менеджер если он есть
            if hasattr(super(), "__exit__"):
                super().__exit__(exc_type, exc_val, exc_tb)  # type: ignore[reportUnknownMemberType]
        except Exception as e:
            logger.warning(f"Error in parent __exit__: {e}")
        return None  # Не подавляем исключения


class EvolutionAsyncOpenAI(_BaseAsyncOpenAI):  # type: ignore[reportUnknownBaseType,reportUnknownMemberType,reportUnknownArgumentType,misc]
    """
    Асинхронная версия Evolution OpenAI Client

    Полностью совместим с AsyncOpenAI
    """

    def __init__(
        self,
        key_id: str,
        secret: str,
        base_url: str,
        # Параметры совместимые с AsyncOpenAI
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        project_id: Optional[str] = None,
        timeout: Union[float, None] = None,
        max_retries: int = 2,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI SDK required. Install with: pip install openai>=1.30.0"
            )

        # Сохраняем Cloud.ru credentials
        self.key_id = key_id
        self.secret = secret
        self.project_id = project_id

        # Инициализируем token manager
        self.token_manager = EvolutionTokenManager(key_id, secret)

        # Получаем первоначальный токен
        initial_token = self.token_manager.get_valid_token()

        # Подготавливаем заголовки с project_id
        prepared_headers = self._prepare_default_headers(default_headers)

        # Инициализируем родительский AsyncOpenAI client
        super().__init__(  # type: ignore[reportUnknownMemberType]
            api_key=initial_token,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=prepared_headers,
            default_query=default_query,
            http_client=http_client,
            **kwargs,
        )

        # Патчим async client
        self._patch_async_client()

        # Устанавливаем заголовки после инициализации родительского класса
        self._initialize_headers()

    def _prepare_default_headers(
        self, user_headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Подготавливает заголовки по умолчанию с учетом project_id"""
        headers: Dict[str, str] = {}

        # Добавляем пользовательские заголовки
        if user_headers:
            headers.update(user_headers)

        # Добавляем project_id заголовок если он установлен
        if self.project_id:
            headers["x-project-id"] = self.project_id

        return headers

    def _initialize_headers(self) -> None:
        """Инициализирует заголовки после создания клиента"""
        current_token = self.token_manager.get_valid_token()
        if current_token:
            self._update_auth_headers(current_token)

    def _patch_async_client(self) -> None:
        """Патчим async client для автоматического обновления токенов"""
        # В новых версиях используется 'request'
        if hasattr(self._client, "request"):  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
            original_request = self._client.request  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
            method_name = "request"
        else:
            logger.warning(
                "Не удалось найти метод request в async HTTP клиенте"
            )
            return

        async def patched_request(*args: Any, **kwargs: Any) -> Any:  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportUnknownVariableType,reportUnknownReturnType]
            # Обновляем токен перед каждым запросом
            current_token = self.token_manager.get_valid_token()
            self.api_key = current_token or ""  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
            self._update_auth_headers(current_token or "")

            try:
                return await original_request(*args, **kwargs)
            except Exception as e:
                if self._is_auth_error(e):
                    logger.warning(
                        "Ошибка авторизации, принудительно обновляем токен"
                    )
                    self.token_manager.invalidate_token()
                    new_token = self.token_manager.get_valid_token()
                    self.api_key = new_token or ""  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
                    self._update_auth_headers(new_token or "")
                    return await original_request(*args, **kwargs)
                else:
                    raise

        # Устанавливаем патченый метод
        setattr(self._client, method_name, patched_request)  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]

    def _update_auth_headers(self, token: str) -> None:
        """Обновляет заголовки авторизации"""
        auth_header = f"Bearer {token}"
        headers_updated = False

        # Пытаемся обновить заголовки различными способами
        if hasattr(self._client, "_auth_headers"):
            self._client._auth_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            # Добавляем project_id заголовок если он установлен
            if self.project_id:
                self._client._auth_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        if hasattr(self._client, "default_headers"):
            self._client.default_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            # Добавляем project_id заголовок если он установлен
            if self.project_id:
                self._client.default_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        # Пытаемся обновить заголовки через _default_headers (для новых версий OpenAI SDK)
        if hasattr(self._client, "_default_headers"):
            self._client._default_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            if self.project_id:
                self._client._default_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        # Обновляем заголовки на уровне самого клиента
        if hasattr(self, "default_headers") and self.default_headers:
            self.default_headers["Authorization"] = auth_header  # type: ignore[reportAttributeAccessIssue]
            if self.project_id:
                self.default_headers["x-project-id"] = self.project_id  # type: ignore[reportAttributeAccessIssue]
            headers_updated = True

        if not headers_updated:
            logger.warning(
                "Не удалось обновить заголовки - структура HTTP клиента не распознана"
            )

    def _is_auth_error(self, error: Exception) -> bool:
        """Проверяет, является ли ошибка связанной с авторизацией"""
        error_str = str(error).lower()
        return any(
            keyword in error_str
            for keyword in [
                "unauthorized",
                "401",
                "authentication",
                "forbidden",
                "403",
            ]
        )

    @property
    def current_token(self) -> Optional[str]:
        """Возвращает текущий действующий токен"""
        return self.token_manager.get_valid_token()

    def refresh_token(self) -> Optional[str]:
        """Принудительно обновляет токен"""
        self.token_manager.invalidate_token()
        return self.token_manager.get_valid_token()

    def get_token_info(self) -> Dict[str, Any]:
        """Возвращает информацию о токене"""
        return self.token_manager.get_token_info()

    def get_request_headers(self) -> Dict[str, str]:
        """Возвращает текущие заголовки запроса для отладки"""
        headers: Dict[str, str] = {}

        # Собираем заголовки из различных источников
        if (
            hasattr(self._client, "_auth_headers")
            and self._client._auth_headers
        ):
            headers.update(self._client._auth_headers)  # type: ignore[reportAttributeAccessIssue]
        if (
            hasattr(self._client, "default_headers")
            and self._client.default_headers
        ):
            headers.update(self._client.default_headers)  # type: ignore[reportAttributeAccessIssue]
        if (
            hasattr(self._client, "_default_headers")
            and self._client._default_headers
        ):
            headers.update(self._client._default_headers)  # type: ignore[reportAttributeAccessIssue]
        if hasattr(self, "default_headers") and self.default_headers:
            headers.update(self.default_headers)  # type: ignore[reportAttributeAccessIssue]

        return headers

    @override
    def with_options(self, **kwargs: Any) -> "EvolutionAsyncOpenAI":  # type: ignore[reportUnknownReturnType,misc]
        """Создает новый асинхронный клиент с дополнительными опциями"""
        # Объединяем текущие параметры с новыми
        options: Dict[str, Any] = {
            "key_id": self.key_id,
            "secret": self.secret,
            "base_url": self.base_url,
            "organization": self.organization,
            "project_id": self.project_id,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": getattr(self, "_client", None),
        }
        options.update(kwargs)
        return EvolutionAsyncOpenAI(**options)

    async def __aenter__(self) -> "EvolutionAsyncOpenAI":  # type: ignore[reportUnknownReturnType,reportUnknownMemberType]
        """Асинхронный контекстный менеджер - вход"""
        # Вызываем родительский асинхронный контекстный менеджер если он есть
        if hasattr(super(), "__aenter__"):
            await super().__aenter__()  # type: ignore[reportUnknownMemberType]
        return self

    async def __aexit__(  # type: ignore[reportUnknownMemberType]
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:  # type: ignore[reportUnknownReturnType]
        """Асинхронный контекстный менеджер - выход с очисткой ресурсов"""
        try:
            # Вызываем родительский асинхронный контекстный менеджер если он есть
            if hasattr(super(), "__aexit__"):
                await super().__aexit__(exc_type, exc_val, exc_tb)  # type: ignore[reportUnknownMemberType]
        except Exception as e:
            logger.warning(f"Error in parent async __aexit__: {e}")
        return None  # Не подавляем исключения


# Удобные функции
def create_client(
    key_id: str, secret: str, base_url: str, **kwargs: Any
) -> EvolutionOpenAI:
    """Создает Evolution OpenAI client"""
    return EvolutionOpenAI(
        key_id=key_id, secret=secret, base_url=base_url, **kwargs
    )


def create_async_client(
    key_id: str, secret: str, base_url: str, **kwargs: Any
) -> EvolutionAsyncOpenAI:
    """Создает асинхронный Evolution OpenAI client"""
    return EvolutionAsyncOpenAI(
        key_id=key_id, secret=secret, base_url=base_url, **kwargs
    )
