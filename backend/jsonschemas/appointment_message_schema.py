from jsonschemas.reused_properties import id_prop, message_prop

appointment_message_schema = {
    "$id": "/jsonschemas/appointment_message",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_message_schema",
    "type": "object",
    "properties": {
        **id_prop,
        **message_prop,
    },
    "required": ["id", "message"],
}
