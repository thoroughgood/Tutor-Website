from flask import Blueprint, jsonify, session, Response
from prisma.models import User
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

tutorial = Blueprint("tutorial", __name__)


@tutorial.route("/complete", methods=["POST"])
@error_decorator
def tutorial_complete():
    """Sets the session user to have completed the tutorial.

    Returns:
        Response with status code 204

    Raises:
        ExpectedError: No user is logged in

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    User.prisma().update(
        where={"id": session["user_id"]},
        data={"tutorialState": True},
    )

    return Response(status=204)


@tutorial.route("/", methods=["GET"])
@error_decorator
def tutorial_get():
    """Returns if the session user has completed the tutorial

    Returns:
        completed (bool): if the user has completed the tutorial

    Raises:
        ExpectedError: No user is logged in

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    user = User.prisma().find_unique(where={"id": session["user_id"]})

    return jsonify({"completed": user.tutorialState})
