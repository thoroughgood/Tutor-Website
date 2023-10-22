from jsonschemas.reused_properties import email_prop, password_prop, name_prop

register_schema = {
    "$id": "/jsonschemas/register",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "register_schema",
    "type": "object",
    "properties": {
        **name_prop,
        **email_prop,
        **password_prop,
        "accountType": {"type": "string", "pattern": "student|tutor"},
    },
    "required": ["name", "email", "password", "accountType"],
}
