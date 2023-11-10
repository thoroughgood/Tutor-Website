from jsonschemas.reused_properties import sort_by_prop

appointments_schema = {
    "$id": "/jsonschemas/appointments",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "appointments_schema",
    "type": "object",
    "properties": {**sort_by_prop},
}
