document_upload_schema = {
    "$id": "/jsonschemas/document_upload",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "document_upload_schema",
    "type": "object",
    "properties": {
        "document": {
            "type": "string",
        },
    },
    "required": ["document"],
}