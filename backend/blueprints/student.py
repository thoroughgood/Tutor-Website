from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
from prisma.models import User
from helpers.views import student_view
from helpers.admin_id_check import admin_id_check
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

student = Blueprint("student", __name__)


@student.route("profile/", methods=["GET"])
@error_decorator
def get_profile():
    args = request.args

    if "id" not in args:
        raise ExpectedError("id field was missing", 400)

    student = student_view(id=args["id"])

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    return (
        jsonify(
            {
                "id": student.id,
                "name": student.name,
                "bio": student.bio if student.bio else "",
                "profilePicture": student.profile_picture,
                "location": student.location,
                "phoneNumber": student.phone_number,
            }
        ),
        200,
    )


@student.route("profile/", methods=["PUT"])
@error_decorator
def modify_profile():
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)
    mod_id = admin_id_check(args)

    if "name" not in args or len(str(args["name"]).lower().strip()) == 0:
        raise ExpectedError("name field was missing", 400)
    if "bio" not in args:
        raise ExpectedError("bio field was missing", 400)
    if "profilePicture" not in args:
        raise ExpectedError("profilePicture field was missing", 400)
    if "location" not in args:
        raise ExpectedError("location field was missing", 400)
    if "phoneNumber" not in args:
        raise ExpectedError("phoneNumber field was missing", 400)

    student = student_view(id=mod_id)
    if not student:
        raise ExpectedError("Profile does not exist", 404)

    name = (
        args["name"]
        if ("name" in args and len(str(args["name"]).lower().strip()) != 0)
        else student.name
    )
    bio = args["bio"] if "bio" in args else student.bio
    profile_picture = (
        args["profilePicture"] if "profilePicture" in args else student.profile_picture
    )
    location = args["location"] if "location" in args else student.location
    phone_number = (
        args["phoneNumber"] if "phoneNumber" in args else student.phone_number
    )

    User.prisma().update(
        where={"id": student.id},
        data={
            "name": name,
            "bio": bio if bio else "",
            "profilePicture": profile_picture,
            "location": location,
            "phoneNumber": phone_number,
        },
    )

    return jsonify({"success": True}), 200


@student.route("/", methods=["DELETE"])
@error_decorator
def delete_profile():
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    mod_id = admin_id_check(args)

    student = student_view(id=mod_id)

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    User.prisma().delete(where={"id": mod_id})

    return jsonify({"success": True}), 200


@student.route("/appointments", methods=["GET"])
@error_decorator
def get_appointment_lists():
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    student = student_view(id=session["user_id"])
    if not student:
        raise ExpectedError("Current user is not a student", 400)

    requested = []
    accepted = []
    completed = []
    for appointment in student.appointments:
        # Note: All datetimes retrieved from db are UTC by default
        # Also note: as utcnow() is offset naive, this approach is preferred
        if (
            datetime.now(timezone.utc) > appointment.endTime
            and appointment.tutorAccepted
        ):
            completed.append(appointment.id)
        elif appointment.tutorAccepted:
            accepted.append(appointment.id)
        # * We shouldn't get an requested appointment with no tutor
        # As long as erroneous data isn't directly added to db
        else:
            requested.append(appointment.id)

    return (
        jsonify(
            {
                "requested": requested,
                "accepted": accepted,
                "completed": completed,
            }
        ),
        200,
    )
