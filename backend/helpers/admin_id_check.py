from flask import session
from helpers.views import admin_view
from helpers.error_handlers import ExpectedError


# Function that checks admin permissions and returns the respective id
def admin_id_check(args) -> str:
    # Check if admin
    admin = admin_view(id=session["user_id"])
    if admin:
        # Check id in args if admin
        if "id" not in args:
            raise ExpectedError("id field was missing", 400)

        return args["id"]
    else:
        # If no "id" in args for admin
        if "id" in args:
            raise ExpectedError(
                "id field should not be supplied by a non admin user", 403
            )
        return session["user_id"]
