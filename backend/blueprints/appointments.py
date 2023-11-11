from flask import Blueprint, jsonify, session
from helpers.views import student_view, tutor_view
from jsonschemas import appointments_schema
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
    validate_decorator,
)

appointments = Blueprint("appointments", __name__)


@appointments.route("/", methods=["GET"])
@error_decorator
@validate_decorator("query_string", appointments_schema)
def get_appointments(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    student = student_view(id=session["user_id"])
    tutor = tutor_view(id=session["user_id"])
    if not student and not tutor:
        raise ExpectedError("Must be a student or tutor to view appointments", 403)

    user = student if student else tutor

    if user.appointments is None:
        user.appointments = []

    if "sortBy" in args:
        # figure out a way to sort by msgs
        apts = sorted(
            user.appointments, key=lambda apt: apt.messages[0].sentTime, reverse=True
        )
    else:
        apts = user.appointments

    return jsonify({"appointments": [apt.id for apt in apts]}), 200
