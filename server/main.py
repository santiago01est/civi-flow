from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


#Trace provider
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "civi-flow-server"}))
)
tracer_provider = trace.get_tracer_provider()

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)


processor = BatchSpanProcessor(ConsoleSpanExporter())
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def root():
    return {"message": "Hello OpenTelemetry"}
