from jsonschemas.reused_properties import id_prop, rating_prop

appointment_rating_schema = {
    "$id": "/jsonschemas/appointment_rating",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointment_rating_schema",
    "type": "object",
    "properties": {
        **id_prop,
        **rating_prop,
    },
    "required": ["id", "rating"],
}
