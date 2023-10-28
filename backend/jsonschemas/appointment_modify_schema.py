from jsonschemas.reused_properties import id_prop, start_time_prop, end_time_prop

appointment_modify_schema = {
    "$id": "/jsonschemas/appointment_modify",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_modify_schema",
    "type": "object",
    "properties": {
        **id_prop,
        **start_time_prop,
        **end_time_prop,
    },
    "required": ["id", "startTime", "endTime"],
}
