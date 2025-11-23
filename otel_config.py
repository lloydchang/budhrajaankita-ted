"""
OpenTelemetry configuration for Honeycomb observability
Provides automatic instrumentation for FastAPI and manual instrumentation utilities
"""

import os
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS


def configure_opentelemetry(app, service_name: str = "budhrajaankita-ted"):
    """
    Configure OpenTelemetry with Honeycomb
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service (used as dataset name in Honeycomb)
    """
    
    # Get Honeycomb API key from environment
    honeycomb_api_key = os.getenv("HONEYCOMB_API_KEY")
    
    if not honeycomb_api_key:
        print("⚠️  HONEYCOMB_API_KEY not configured - observability disabled")
        return None
    
    # Determine Honeycomb endpoint (US or EU)
    honeycomb_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "https://api.honeycomb.io:443"  # Default to US instance
    )
    
    # Create resource with service name and other attributes
    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })
    
    # Configure the tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Add baggage processor to propagate baggage to spans
    tracer_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
    
    # Configure OTLP exporter for Honeycomb
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{honeycomb_endpoint}/v1/traces",
        headers={
            "x-honeycomb-team": honeycomb_api_key,
        }
    )
    
    # Add batch span processor
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument FastAPI automatically
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument requests library (for API calls to Gemini, OpenRouter, Cloudflare)
    RequestsInstrumentor().instrument()
    
    print(f"✅ Honeycomb observability enabled for service: {service_name}")
    print(f"   Endpoint: {honeycomb_endpoint}")
    
    return tracer_provider


def get_tracer(name: str = "main"):
    """
    Get a tracer instance for manual instrumentation
    
    Args:
        name: Name of the tracer (will appear as library.name in Honeycomb)
        
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def add_span_attribute(key: str, value):
    """
    Add an attribute to the current span
    
    Args:
        key: Attribute key
        value: Attribute value (string, int, float, or bool)
    """
    span = trace.get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: dict = None):
    """
    Add an event to the current span
    
    Args:
        name: Event name
        attributes: Optional dictionary of attributes
    """
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes or {})


def set_baggage(key: str, value: str):
    """
    Set a baggage item that will be added to all child spans
    
    Args:
        key: Baggage key
        value: Baggage value
        
    Returns:
        Token for detaching the baggage later
    """
    from opentelemetry.context import attach
    return attach(baggage.set_baggage(key, value))


def detach_baggage(token):
    """
    Detach a baggage item
    
    Args:
        token: Token returned from set_baggage
    """
    from opentelemetry.context import detach
    detach(token)


# Decorator for instrumenting functions
def instrument_function(span_name: str = None):
    """
    Decorator to automatically create a span around a function
    
    Args:
        span_name: Optional custom span name (defaults to function name)
        
    Example:
        @instrument_function("my_custom_operation")
        def my_function():
            # do work
            pass
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer("decorator")
            name = span_name or func.__name__
            
            with tracer.start_as_current_span(name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator
