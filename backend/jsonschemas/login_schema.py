from jsonschemas.reused_properties import email_prop, password_prop

login_schema = {
    "$id": "/jsonschemas/login",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "login_schema",
    "type": "object",
    "properties": {
        **email_prop,
        **password_prop,
        "accountType": {"type": "string", "pattern": "student|tutor|admin"},
    },
    "required": ["email", "password", "accountType"],
}
