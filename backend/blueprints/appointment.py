from flask import Blueprint, request, jsonify, session
from prisma.models import User, Appointment
from datetime import datetime
from helpers.views import student_view, tutor_view
from helpers.admin_id_check import admin_id_check
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

appointment = Blueprint("appointment", __name__)


@appointment.route("request/", methods=["POST"])
@error_decorator
def request():
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    if "startTime" not in args or len(str(args["startTime"]).lower().strip()) == 0:
        raise ExpectedError("startTime field was missing", 400)

    if "endTime" not in args or len(str(args["endTime"]).lower().strip()) == 0:
        raise ExpectedError("endTime field was missing", 400)

    st = datetime.fromisoformat(timeblock["startTime"])
    et = datetime.fromisoformat(timeblock["endTime"])

    if (et - st).total_seconds() <= 0:
        raise ExpectedError("endTime is before startTime", 400)

    tutor = tutor_view(id=args["id"])
    if not tutor:
        raise ExpectedError("Tutor profile does not exist", 400)

    # Check if Logged in user is a student (CLARIFY WITH DANIELS)
    student = student_view(id=session["user_id"])
    if not student:
        raise ExpectedError("Profile is not a student", 400)

    appointment = Appointment.prisma().create(
        data={
            "id": str(uuid.uuid4()),
            "startTime": args["startTime"],
            "endTime": args["endTime"],
            "studentId": session["user_id"],
            "tutorId": args["tutorId"],
            "tutorAccepted": False,
        }
    )

    Student.prisma().update(
        where={"id": session["user_id"]},
        data={"appointments": student.appointments + [appointment]},
    )

    return (
        jsonify(
            {
                "id": appointment.id,
                "startTime": appointment.startTime,
                "endTime": appointment.endTime,
                "studentId": appointment.studentId,
                "tutorId": appointment.tutorId,
                "tutorAccepted": appointment.tutorAccepted,
            }
        ),
        200,
    )
