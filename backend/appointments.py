from flask import Blueprint, jsonify, session
from helpers.views import student_view, tutor_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

appointments = Blueprint("appointments", __name__)


@appointments.route("/", methods=["GET"])
@error_decorator
# validate with sortBy
def get_appointments(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    student = student_view(id=session["user_id"])
    tutor = tutor_view(id=session["user_id"])
    user = student if student else tutor
    # if not user:
    #     raise ExpectedError("Must be a student or tutor to view appointments", 403)

    if "sortBy" in args and args["sortBy"] == "messageSent":
        apts = sorted(
            user.appointments,
            key=lambda appointment: appointment.messageSent,
            reverse=True,
        )
    else:
        apts = user.appointments

    return jsonify({"appointments": apts}), 200
