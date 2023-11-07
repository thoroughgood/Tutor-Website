from flask import Blueprints, jsonify, session
from prisma.models import User
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

tutorial = Blueprints("tutorial", __name__)

@tutorial.route("/complete", methods=["POST"])
@error_decorator
def tutorial_complete():
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)
    
    User.prisma().update(
        where={"id": session["user_id"]},
        data={"tutorialState": True},
    )

@tutorial.route("", methods=["GET"])
@error_decorator
def tutorial_get():
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)
    
    user = User.prisma().find_unique(where={"id": session["user_id"]})
    
    return jsonify({"completed": user.tutorialState})
