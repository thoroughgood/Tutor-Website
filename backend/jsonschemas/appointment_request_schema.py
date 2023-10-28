from jsonschemas.reused_properties import start_time_prop, end_time_prop

appointment_request_schema = {
    "$id": "/jsonschemas/appointment_request",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_request_schema",
    "type": "object",
    "properties": {
        **start_time_prop,
        **end_time_prop,
        "tutorId": {
            "type": "string",
        },
    },
    "required": ["startTime", "endTime", "tutorId"],
}
