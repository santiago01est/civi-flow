from telemetry_config import setup_telemetry

tracer = setup_telemetry("civi-flow-server")

@tracer.start_as_current_span("")
def roll_dice():
    pass