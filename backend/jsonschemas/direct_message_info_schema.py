from reused_properties import other_id_prop

direct_message_info_schema = {
    "$id": "/jsonschemas/direct_message_info",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "direct_message_info_schema",
    "type": "object",
    "properties": {
        **other_id_prop,
    },
    "required": ["otherId"],
}
