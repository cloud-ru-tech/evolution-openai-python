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
        project: str,
        # Параметры совместимые с OpenAI SDK
        api_key: Optional[str] = None,  # Игнорируется
        organization: Optional[str] = None,
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
        self.project = project

        # Инициализируем token manager
        self.token_manager = EvolutionTokenManager(key_id, secret)
        self._need_token_refresh: bool = False

        # Получаем первоначальный токен
        initial_token = self.token_manager.get_valid_token()

        # Инициализируем родительский OpenAI client
        super().__init__(  # type: ignore[reportUnknownMemberType]
            api_key=initial_token,
            organization=organization,
            project=project,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            **kwargs,
        )

    @override
    def _should_retry(self, response: Any) -> bool: # type: ignore[reportUnknownMemberType]
        """Определяет, нужно ли повторять запрос для данного ответа.

        При получении 401 или 403 инициирует обновление токена и позволяет выполнить повтор.

        :param response: Ответ httpx.Response от сервера.
        :return: True если нужно сделать retry, иначе — результат родительского метода.
        """
        if response.status_code in (401, 403):
            self._need_token_refresh = True
            return True
        return super()._should_retry(response)  # type: ignore[reportUnknownMemberType]

    @override
    def _prepare_request(self, request: Any) -> None:  # type: ignore[reportUnknownMemberType]
        """Мутирует объект запроса перед отправкой.

        При необходимости обновляет токен авторизации
        и всегда добавляет заголовок x-project-id с текущим проектом.

        :param request: Объект httpx.Request, готовящийся к отправке.
        """
        if self._need_token_refresh or not self.is_token_valid:
            token = self.refresh_token()
            self.api_key = token
            request.headers["Authorization"] = f"Bearer {token}"
            self._need_token_refresh = False
        request.headers["x-project-id"] = self.project


    @property
    def is_token_valid(self) -> bool:
        """Возвращает статус валидности токена."""
        return self.token_manager.is_token_valid()

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

    @override
    def with_options(self, **kwargs: Any) -> "EvolutionOpenAI":  # type: ignore[reportUnknownReturnType,misc]
        """Создает новый клиент с дополнительными опциями"""
        # Объединяем текущие параметры с новыми
        options: Dict[str, Any] = {
            "key_id": self.key_id,
            "secret": self.secret,
            "base_url": self.base_url,
            "organization": self.organization,
            "project": getattr(self, "project", None),
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
        project: str,
        # Параметры совместимые с AsyncOpenAI
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
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
        self.project = project

        # Инициализируем token manager
        self.token_manager = EvolutionTokenManager(key_id, secret)
        self._need_token_refresh: bool = False
        # Получаем первоначальный токен
        initial_token = self.token_manager.get_valid_token()

        # Инициализируем родительский AsyncOpenAI client
        super().__init__(  # type: ignore[reportUnknownMemberType]
            api_key=initial_token,
            organization=organization,
            project=project,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            **kwargs,
        )

    @override
    def _should_retry(self, response: Any) -> bool: # type: ignore[reportUnknownMemberType]
        """Определяет, нужно ли повторять запрос для данного ответа.

        При получении 401 или 403 инициирует обновление токена и позволяет выполнить повтор.

        :param response: Ответ httpx.Response от сервера.
        :return: True если нужно сделать retry, иначе — результат родительского метода.
        """
        if response.status_code in (401, 403):
            self._need_token_refresh = True
            return True
        return super()._should_retry(response) # type: ignore[reportUnknownMemberType]

    @override
    async def _prepare_request(self, request: Any) -> None: # type: ignore[reportUnknownMemberType]
        """Мутирует объект запроса перед отправкой.

        При необходимости обновляет токен авторизации
        и всегда добавляет заголовок x-project-id с текущим проектом.

        :param request: Объект httpx.Request, готовящийся к отправке.
        """
        if self._need_token_refresh or not self.is_token_valid:
            token = self.refresh_token()
            self.api_key = token
            request.headers["Authorization"] = f"Bearer {token}"
            self._need_token_refresh = False
        request.headers["x-project-id"] = self.project


    @property
    def is_token_valid(self) -> bool:
        """Возвращает статус валидности токена."""
        return self.token_manager.is_token_valid()

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

    @override
    def with_options(self, **kwargs: Any) -> "EvolutionAsyncOpenAI":  # type: ignore[reportUnknownReturnType,misc]
        """Создает новый асинхронный клиент с дополнительными опциями"""
        # Объединяем текущие параметры с новыми
        options: Dict[str, Any] = {
            "key_id": self.key_id,
            "secret": self.secret,
            "base_url": self.base_url,
            "organization": self.organization,
            "project": getattr(self, "project", None),
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
