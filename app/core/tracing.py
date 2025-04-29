from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.core.settings import settings


def configure_tracing() -> None:
    """Configure OpenTelemetry tracing."""
    # Create a resource with service name
    resource = Resource.create(
        {
            "service.name": settings.OTEL_SERVICE_NAME,
        }
    )

    # Create a tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Create a console exporter for development
    console_exporter = ConsoleSpanExporter()

    # Create a span processor
    span_processor = BatchSpanProcessor(console_exporter)

    # Add the span processor to the tracer provider
    tracer_provider.add_span_processor(span_processor)

    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider) 