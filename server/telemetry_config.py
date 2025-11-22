from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_telemetry(service_name: str = "civi-flow-server"):
    """Configure OpenTelemetry for the application"""
    
    resource = Resource(attributes={
        "service.name": service_name
    })
    provider = TracerProvider(resource=resource)
    
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(__name__)