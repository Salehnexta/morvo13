"""
Error tracking and monitoring integration for Morvo13.
"""

import logging
import os
from typing import Any, Callable, Literal, TypeVar

# Third-party dependency `sentry_sdk` is optional in testing environments. Provide
# a graceful degradation path so the application can be imported even when the
# library is absent.

try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.fastapi import FastApiIntegration  # type: ignore
    from sentry_sdk.integrations.logging import LoggingIntegration  # type: ignore
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration  # type: ignore

    _SENTRY_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover – optional dependency
    # Build minimal stubs so that the rest of this module can still be used.
    _SENTRY_AVAILABLE = False

    class _DummySentry:  # noqa: D101 – minimal replacement
        def init(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401, ANN401
            pass

        def configure_scope(self):  # noqa: D401
            class _DummyScope:  # noqa: D101
                def __enter__(self):  # noqa: D401
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: D401
                    return False

                def set_extra(self, *_args: Any, **_kwargs: Any) -> None:  # noqa: D401
                    pass

                def set_user(self, *_args: Any, **_kwargs: Any) -> None:  # noqa: D401
                    pass

                def set_tag(self, *_args: Any, **_kwargs: Any) -> None:  # noqa: D401
                    pass

            return _DummyScope()

        def capture_exception(self, *_args: Any, **_kwargs: Any):  # noqa: D401, ANN401
            return None

        def capture_message(self, *_args: Any, **_kwargs: Any):  # noqa: D401, ANN401
            return None

        def add_breadcrumb(self, *_args: Any, **_kwargs: Any):  # noqa: D401, ANN401
            pass

    sentry_sdk = _DummySentry()  # type: ignore

    # Dummy integration placeholders to keep type hints intact where used
    class _DummyIntegration:  # noqa: D101
        def __init__(self, *_: Any, **__: Any) -> None:  # noqa: D401
            pass

    FastApiIntegration = LoggingIntegration = SqlalchemyIntegration = _DummyIntegration  # type: ignore

from fastapi import FastAPI

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


def init_error_tracking(app: FastAPI) -> None:
    """
    Initialize error tracking with Sentry.

    Args:
        app: FastAPI application instance
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")

    if not sentry_dsn:
        logger.warning("SENTRY_DSN not configured. Error tracking disabled.")
        return

    if not _SENTRY_AVAILABLE:
        logger.info("sentry_sdk not installed – skipping error tracking setup.")
        return

    # Configure Sentry integrations
    integrations = [
        FastApiIntegration(),
        SqlalchemyIntegration(),
        LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        ),
    ]

    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=integrations,
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        send_default_pii=False,  # Don't send personally identifiable information
        debug=environment == "development",
        release=getattr(settings, "VERSION", "unknown"),
    )

    logger.info("Sentry error tracking initialized for environment: %s", environment)


def capture_exception(error: Exception, extra_data: dict | None = None) -> str | None:
    """
    Manually capture an exception with optional extra data.

    Args:
        error: The exception to capture
        extra_data: Additional context data

    Returns:
        Sentry event ID or None
    """
    with sentry_sdk.configure_scope() as scope:
        if extra_data:
            for key, value in extra_data.items():
                scope.set_extra(key, value)

        event_id = sentry_sdk.capture_exception(error)
        if event_id:
            logger.error(f"Exception captured by Sentry: {event_id}")
        return event_id


def capture_message(
    message: str,
    level: Literal["fatal", "critical", "error", "warning", "info", "debug"] = "info",
    extra_data: dict | None = None,
) -> str | None:
    """
    Capture a custom message.

    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
        extra_data: Additional context data

    Returns:
        Sentry event ID or None
    """
    with sentry_sdk.configure_scope() as scope:
        if extra_data:
            for key, value in extra_data.items():
                scope.set_extra(key, value)

        event_id = sentry_sdk.capture_message(message, level=level)
        if event_id:
            logger.info(f"Message captured by Sentry: {event_id}")
        return event_id


def set_user_context(user_id: str, email: str | None = None, username: str | None = None) -> None:
    """
    Set user context for error tracking.

    Args:
        user_id: User identifier
        email: User email (optional)
        username: Username (optional)
    """
    with sentry_sdk.configure_scope() as scope:
        scope.set_user(
            {
                "id": user_id,
                "email": email,
                "username": username,
            }
        )


def set_tag(key: str, value: str) -> None:
    """
    Set a custom tag for error tracking.

    Args:
        key: Tag key
        value: Tag value
    """
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag(key, value)


def add_breadcrumb(
    message: str, category: str = "custom", level: str = "info", data: dict | None = None
) -> None:
    """
    Add a breadcrumb for debugging context.

    Args:
        message: Breadcrumb message
        category: Category of the breadcrumb
        level: Log level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(message=message, category=category, level=level, data=data or {})


F = TypeVar("F", bound=Callable[..., Any])


# Error tracking decorator
def track_errors(operation_name: str) -> Callable[[F], F]:
    """
    Decorator to automatically track errors in functions.

    Args:
        operation_name: Name of the operation for tracking
    """

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                add_breadcrumb(f"Starting operation: {operation_name}")
                result = func(*args, **kwargs)
                add_breadcrumb(f"Completed operation: {operation_name}")
                return result
            except Exception as e:
                capture_exception(
                    e,
                    {
                        "operation": operation_name,
                        "function": func.__name__,
                        "args": str(args)[:500],  # Limit length
                        "kwargs": str(kwargs)[:500],
                    },
                )
                raise

        return wrapper  # type: ignore

    return decorator
 