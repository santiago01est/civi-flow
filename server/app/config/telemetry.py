# OpenTelemetry configuration

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import logging

logger = logging.getLogger(__name__)

'''


def setup_opentelemetry(app, service_name: str, otlp_endpoint: str):
    """
    Configure OpenTelemetry for FastAPI application
    """
    # Create resource with service information
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    # Configure Tracing
    tracer_provider = TracerProvider(resource=resource)
    otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_trace_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    
    # Configure Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    
    # Instrument FastAPI automatically
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument SQLAlchemy for database tracing
    SQLAlchemyInstrumentor().instrument()
    
    # Instrument Redis for caching tracing
    RedisInstrumentor().instrument()
    
    # Instrument HTTP requests
    RequestsInstrumentor().instrument()
    
    logger.info(f"OpenTelemetry configured for {service_name}")
    
    return trace.get_tracer(__name__), metrics.get_meter(__name__)


'''