from jsonschemas.reused_properties import id_prop

document_delete_schema = {
    "$id": "/jsonschemas/document_delete",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "document_delete_schema",
    "type": "object",
    "properties": {
        **id_prop,
    },
    "required": ["id"],
}
