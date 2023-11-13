from flask import Blueprint, jsonify, session
from datetime import datetime, MINYEAR, timezone
from prisma.models import User
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

    user = User.prisma().find_unique(
        where={
            "id": session["user_id"],
        },
        include={
            "adminInfo": True,
            "tutorInfo": {
                "include": {
                    "appointments": {
                        "include": {
                            "messages": {"order_by": {"sentTime": "desc"}},
                        }
                    }
                }
            },
            "studentInfo": {
                "include": {
                    "appointments": {
                        "include": {
                            "messages": {"order_by": {"sentTime": "desc"}},
                        }
                    }
                }
            },
        },
    )

    appointments = []
    if user.adminInfo is not None:
        raise ExpectedError("Must be a student or tutor to view appointments", 403)
    elif user.studentInfo is not None:
        appointments = user.studentInfo.appointments
    elif user.tutorInfo is not None:
        appointments = user.tutorInfo.appointments

    if "sortBy" in args:
        # figure out a way to sort by msgs
        appointments = sorted(
            appointments,
            key=lambda apt: apt.messages[0].sentTime
            if len(apt.messages) != 0
            else datetime(MINYEAR, 1, 1, tzinfo=timezone.utc),
            reverse=True,
        )

    return jsonify({"appointments": [apt.id for apt in appointments]}), 200
