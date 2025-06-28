"""OpenTelemetry tracing configuration."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer

logger = logging.getLogger(__name__)

# Lazy imports to avoid hard dependencies
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    # Make httpx instrumentation optional
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPX_AVAILABLE = True
    except ImportError:
        HTTPX_AVAILABLE = False
        logger.warning("opentelemetry-instrumentation-httpx not available. HTTPX tracing disabled.")
    
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OTEL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OpenTelemetry not available: {e}")
    OTEL_AVAILABLE = False
    HTTPX_AVAILABLE = False


def init_tracing() -> Tracer | None:
    """Initialize OpenTelemetry tracing if enabled and available."""
    if not os.getenv("ENABLE_TRACING", "false").lower() == "true":
        logger.info("Tracing disabled via ENABLE_TRACING=false")
        return None

    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available. Tracing disabled.")
        return None

    try:
        # Set up the tracer provider
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)

        # Configure OTLP exporter if endpoint is provided
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            logger.info(f"OTLP tracing configured for endpoint: {otlp_endpoint}")

        logger.info("OpenTelemetry tracing initialized successfully")
        return tracer

    except Exception as e:
        logger.error(f"Failed to initialize tracing: {e}")
        return None


def instrument_fastapi(app) -> None:
    """Instrument FastAPI app with OpenTelemetry."""
    if not OTEL_AVAILABLE or not os.getenv("ENABLE_TRACING", "false").lower() == "true":
        return

    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented with OpenTelemetry")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}")


def instrument_httpx() -> None:
    """Instrument HTTPX client with OpenTelemetry."""
    if not OTEL_AVAILABLE or not HTTPX_AVAILABLE or not os.getenv("ENABLE_TRACING", "false").lower() == "true":
        return

    try:
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX instrumented with OpenTelemetry")
    except Exception as e:
        logger.error(f"Failed to instrument HTTPX: {e}") 