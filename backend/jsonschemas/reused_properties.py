email_prop = {
    "email": {
        "type": "string",
        "format": "email",
    },
}

password_prop = {
    "password": {
        "type": "string",
        "minLength": 8,
    },
}

id_prop = {
    "id": {
        "type": "string",
    }
}

bio_prop = {
    "id": {
        "type": "string",
    }
}

name_prop = {
    "name": {
        "type": "string",
        "minLength": 1,
    }
}

location_prop = {
    "location": {
        "type": "string",
    }
}

rating_prop = {
    "rating": {
        "type": "integer",
        "minimum": 1,
        "maximum": 5,
    }
}
