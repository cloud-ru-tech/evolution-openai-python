"""
Pytest configuration and fixtures for evolution-openai tests
"""

from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING, Dict, Iterator, Optional, AsyncIterator

import pytest
from dotenv import load_dotenv
from pytest_asyncio import is_async_test

from evolution_openai import (
    OpenAI as EvolutionOpenAI,
    AsyncOpenAI as CloudAsyncOpenAI,
)

if TYPE_CHECKING:
    from _pytest.config import (
        Config,  # pyright: ignore[reportPrivateImportUsage]
    )
    from _pytest.fixtures import (
        FixtureRequest,  # pyright: ignore[reportPrivateImportUsage]
    )

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("evolution_openai").setLevel(logging.DEBUG)

# Load .env file if it exists
load_dotenv()


# automatically add `pytest.mark.asyncio()` to all of our async tests
# so we don't have to add that boilerplate everywhere
def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)

    # Skip integration tests if not enabled
    if not os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true":
        skip_integration = pytest.mark.skip(
            reason="Integration tests disabled. "
            "Set ENABLE_INTEGRATION_TESTS=true to enable."
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

    # Skip foundation models tests if not enabled
    foundation_models_enabled = (
        os.getenv("ENABLE_FOUNDATION_MODELS_TESTS", "false").lower() == "true"
        or os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true"
    )
    if not foundation_models_enabled:
        skip_foundation_models = pytest.mark.skip(
            reason="Foundation Models tests disabled. "
            "Set ENABLE_FOUNDATION_MODELS_TESTS=true or ENABLE_INTEGRATION_TESTS=true to enable."
        )
        for item in items:
            if (
                "foundation_models" in item.keywords
                or "test_foundation_models" in item.name
            ):
                item.add_marker(skip_foundation_models)


def pytest_configure(config: Config) -> None:
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "foundation_models: mark test as foundation models test"
    )

    # Load environment variables from .env file if exists
    try:
        from dotenv import load_dotenv

        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ Loaded .env file: {env_path}")
    except ImportError:
        # python-dotenv not installed - not critical for tests
        pass


@pytest.fixture(scope="session")
def test_credentials() -> Dict[str, Optional[str]]:
    """Fixture providing test credentials from environment variables"""
    return {
        "key_id": os.getenv("EVOLUTION_KEY_ID"),
        "secret": os.getenv("EVOLUTION_SECRET"),
        "base_url": os.getenv("EVOLUTION_BASE_URL"),
        "project_id": os.getenv("EVOLUTION_PROJECT_ID"),
        "token_url": os.getenv(
            "EVOLUTION_TOKEN_URL", "https://iam.api.cloud.ru/api/v1/auth/token"
        ),
    }


@pytest.fixture(scope="session")
def integration_enabled() -> bool:
    """Fixture checking if integration tests are enabled"""
    return os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true"


@pytest.fixture
def mock_credentials() -> Dict[str, str]:
    """Fixture providing mock credentials for unit tests"""
    return {
        "key_id": "test_key_id",
        "secret": "test_secret",
        "base_url": "https://test.example.com/v1",
        "project_id": "test_project_id",
        "token_url": "https://iam.api.cloud.ru/api/v1/auth/token",
    }


@pytest.fixture(scope="session")
def project_id() -> Optional[str]:
    """Fixture providing project_id from environment variables"""
    return os.getenv("EVOLUTION_PROJECT_ID")


@pytest.fixture
def mock_project_id() -> str:
    """Fixture providing mock project_id for unit tests"""
    return "test_project_id"


@pytest.fixture(scope="session")
def client(
    request: FixtureRequest, test_credentials: Dict[str, Optional[str]]
) -> Iterator[EvolutionOpenAI]:
    """Session-scoped sync client fixture with proper cleanup"""
    if not test_credentials["key_id"] or not test_credentials["secret"]:
        pytest.skip("Real credentials not provided for client fixture")

    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(
            f"Unexpected fixture parameter type {type(strict)}, expected {bool}"
        )

    try:
        with EvolutionOpenAI(
            key_id=test_credentials["key_id"] or "",
            secret=test_credentials["secret"] or "",
            base_url=test_credentials["base_url"] or "",
            timeout=30.0,
        ) as client:
            yield client
    except Exception as e:
        pytest.skip(f"Failed to create client: {e}")


@pytest.fixture(scope="session")
async def async_client(
    request: FixtureRequest, test_credentials: Dict[str, Optional[str]]
) -> AsyncIterator[CloudAsyncOpenAI]:
    """Session-scoped async client fixture with proper cleanup"""
    if not test_credentials["key_id"] or not test_credentials["secret"]:
        pytest.skip("Real credentials not provided for async client fixture")

    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(
            f"Unexpected fixture parameter type {type(strict)}, expected {bool}"
        )

    try:
        async with CloudAsyncOpenAI(
            key_id=test_credentials["key_id"] or "",
            secret=test_credentials["secret"] or "",
            base_url=test_credentials["base_url"] or "",
            timeout=30.0,
        ) as client:
            yield client
    except Exception as e:
        pytest.skip(f"Failed to create async client: {e}")


@pytest.fixture(scope="session")
def foundation_models_credentials() -> Dict[str, Optional[str]]:
    """Fixture providing Foundation Models specific credentials from environment variables"""
    return {
        "key_id": os.getenv("EVOLUTION_KEY_ID"),
        "secret": os.getenv("EVOLUTION_SECRET"),
        "base_url": os.getenv(
            "EVOLUTION_FOUNDATION_MODELS_URL",
            "https://foundation-models.api.cloud.ru/api/gigacube/openai/v1",
        ),
        "project_id": os.getenv("EVOLUTION_PROJECT_ID"),
        "token_url": os.getenv(
            "EVOLUTION_TOKEN_URL", "https://iam.api.cloud.ru/api/v1/auth/token"
        ),
    }


@pytest.fixture(scope="session")
def foundation_models_enabled() -> bool:
    """Fixture checking if foundation models integration tests are enabled"""
    return (
        os.getenv("ENABLE_FOUNDATION_MODELS_TESTS", "false").lower() == "true"
        or os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true"
    )


@pytest.fixture(scope="session")
def foundation_models_client(
    request: FixtureRequest,
    foundation_models_credentials: Dict[str, Optional[str]],
) -> Iterator[EvolutionOpenAI]:
    """Session-scoped Foundation Models sync client fixture with proper cleanup"""
    if (
        not foundation_models_credentials["key_id"]
        or not foundation_models_credentials["secret"]
    ):
        pytest.skip(
            "Real Foundation Models credentials not provided for client fixture"
        )

    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(
            f"Unexpected fixture parameter type {type(strict)}, expected {bool}"
        )

    try:
        with EvolutionOpenAI(
            key_id=foundation_models_credentials["key_id"] or "",
            secret=foundation_models_credentials["secret"] or "",
            base_url=foundation_models_credentials["base_url"] or "",
            project_id=foundation_models_credentials["project_id"],
            timeout=60.0,
        ) as client:
            yield client
    except Exception as e:
        pytest.skip(f"Failed to create Foundation Models client: {e}")


@pytest.fixture(scope="session")
async def foundation_models_async_client(
    request: FixtureRequest,
    foundation_models_credentials: Dict[str, Optional[str]],
) -> AsyncIterator[CloudAsyncOpenAI]:
    """Session-scoped Foundation Models async client fixture with proper cleanup"""
    if (
        not foundation_models_credentials["key_id"]
        or not foundation_models_credentials["secret"]
    ):
        pytest.skip(
            "Real Foundation Models credentials not provided for async client fixture"
        )

    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(
            f"Unexpected fixture parameter type {type(strict)}, expected {bool}"
        )

    try:
        async with CloudAsyncOpenAI(
            key_id=foundation_models_credentials["key_id"] or "",
            secret=foundation_models_credentials["secret"] or "",
            base_url=foundation_models_credentials["base_url"] or "",
            project_id=foundation_models_credentials["project_id"],
            timeout=60.0,
        ) as client:
            yield client
    except Exception as e:
        pytest.skip(f"Failed to create Foundation Models async client: {e}")


@pytest.fixture(scope="session")
def foundation_models_default_model() -> str:
    """Fixture providing default Foundation Models model name"""
    return os.getenv(
        "EVOLUTION_FOUNDATION_MODELS_DEFAULT_MODEL",
        "RefalMachine/RuadaptQwen2.5-7B-Lite-Beta",
    )
