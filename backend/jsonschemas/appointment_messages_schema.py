from jsonschemas.reused_properties import id_prop

appointment_messages_schema = {
    "$id": "/jsonschemas/appointment_messages",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_messages_schema",
    "type": "object",
    "properties": {**id_prop},
    "required": ["id"],
}
