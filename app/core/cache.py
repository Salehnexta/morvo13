# The caching layer is optional during testing. Provide graceful fallbacks if the
# optional dependencies are not installed so imports do not crash the
# application when running in lightweight CI environments.

try:
    from fastapi_cache import FastAPICache  # type: ignore
    from fastapi_cache.backends.redis import RedisBackend  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – optional dependency
    class _DummyFastAPICache:  # noqa: D101 – internal helper
        """No-op stand-in for FastAPICache when the library is absent."""

        def init(self, *_args, **_kwargs) -> None:  # noqa: D401, ANN001, D401 – simple no-op
            """Do nothing."""

    FastAPICache = _DummyFastAPICache()  # type: ignore

    class _DummyRedisBackend:  # noqa: D101 – placeholder
        def __init__(self, *_args, **_kwargs) -> None:  # noqa: D401, ANN001
            pass

    RedisBackend = _DummyRedisBackend  # type: ignore

# redis-py is also optional in some environments (e.g. during unit tests)
try:
    from redis import asyncio as aioredis  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – optional dependency
    class _DummyAioredis:  # noqa: D101 – lightweight stub
        @staticmethod
        def from_url(*_args, **_kwargs):  # noqa: D401, ANN001
            """Return a dummy Redis connection object with async no-ops."""

            class _DummyConnection:  # noqa: D101 – internal helper
                async def ping(self) -> bool:  # noqa: D401
                    return True

            return _DummyConnection()

    aioredis = _DummyAioredis()  # type: ignore

from app.core.config.settings import settings


async def init_cache() -> None:
    """Initialize the Redis-backed cache if the required libraries are present.

    When running the full application (development/production) the optional
    libraries *should* be installed and the cache will be enabled. During unit
    testing, however, these dependencies might be absent in the lightweight
    environment. In that scenario this function becomes a harmless no-op so the
    rest of the application can still be imported and tested.
    """

    # If either Redis or fastapi-cache is unavailable we silently skip cache
    # initialisation. This is acceptable for testing purposes but a warning is
    # logged so it is obvious in richer environments.
    try:
        redis = aioredis.from_url(
            settings.REDIS_URL, encoding="utf8", decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix="morvo-cache")
    except Exception:  # pragma: no cover – any failure just disables caching
        # Lazy import to avoid circular logging dependency
        from logging import getLogger

        getLogger(__name__).warning(
            "Caching layer disabled – optional dependencies not available or failed to initialise."
        )
