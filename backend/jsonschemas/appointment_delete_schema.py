from jsonschemas.reused_properties import id_prop

appointment_delete_schema = {
    "$id": "/jsonschemas/appointment_delete",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_delete_schema",
    "type": "object",
    "properties": {
        **id_prop,
    },
    "required": ["id"],
}
