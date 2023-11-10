from jsonschemas.reused_properties import message_prop, other_id_prop

direct_message_schema = {
    "$id": "/jsonschemas/direct_message",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "direct_message_schema",
    "type": "object",
    "properties": {
        **other_id_prop,
        **message_prop,
    },
    "required": ["otherId", "message"],
}
