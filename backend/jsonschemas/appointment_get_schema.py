from jsonschemas.reused_properties import id_prop

appointment_get_schema = {
    "$id": "/jsonschemas/appointment_get",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_get_schema",
    "type": "object",
    "properties": {
        **id_prop,
    },
    "required": ["id"],
}
