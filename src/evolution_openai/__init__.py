"""
Evolution OpenAI - Полностью совместимый с официальным OpenAI Python SDK

Автоматическое управление токенами Cloud.ru для бесшовной интеграции.
"""

from importlib.metadata import version as get_version

__version__ = get_version(__package__ or "evolution-openai")
__title__ = "evolution-openai"
__author__ = "Evolution ML Inference Team"
__email__ = "support@cloud.ru"
__description__ = "Evolution OpenAI with automatic token management"

from evolution_openai.client import (
    EvolutionOpenAI,
    EvolutionAsyncOpenAI,
    create_client,
    create_async_client,
)
from evolution_openai.exceptions import EvolutionAuthError, EvolutionTokenError
from evolution_openai.token_manager import EvolutionTokenManager

# Public API aliases для совместимости
OpenAI = EvolutionOpenAI
AsyncOpenAI = EvolutionAsyncOpenAI


__all__ = [
    # Main classes
    "EvolutionOpenAI",
    "EvolutionAsyncOpenAI",
    "EvolutionTokenManager",
    # Aliases
    "OpenAI",
    "AsyncOpenAI",
    # Factory functions
    "create_client",
    "create_async_client",
    # Exceptions
    "EvolutionAuthError",
    "EvolutionTokenError",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
