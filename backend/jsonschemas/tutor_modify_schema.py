from jsonschemas.reused_properties import (
    make_or_null,
    email_prop,
    bio_prop,
    name_prop,
    location_prop,
    profile_picture_prop,
    phone_number_prop,
    course_offerings_prop,
    times_available_prop,
)

tutor_modify_schema = {
    "$id": "/jsonschemas/tutor_modify",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "tutor_modify_schema",
    "type": "object",
    "properties": {
        **name_prop,
        **email_prop,
        **bio_prop,
        **make_or_null(
            **location_prop,
            **profile_picture_prop,
            **phone_number_prop,
        ),
        **course_offerings_prop,
        **times_available_prop,
    },
}
