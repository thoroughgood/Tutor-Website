from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
from prisma.models import User
from jsonschemas import student_modify_schema
from helpers.views import student_view
from helpers.admin_id_check import admin_id_check
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

student = Blueprint("student", __name__)


@student.route("/<student_id>", methods=["GET"])
@error_decorator
def get_profile(student_id):
    """Get the profile of a student

    Args:
        student_id (str): The id of the student to get the profile of

    Returns:
        id (str): The id of the student
        name (str): The name of the student
        bio (str): The bio of the student
        profilePicture (str): The profile picture of the student
        location (str): The location of the student
        phoneNumber (str): The phone number of the student

    Raises:
        ExpectedError: If the student profile does not exist

    """
    student = student_view(id=student_id)

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


@student.route("profile", methods=["PUT"])
@error_decorator
@validate_decorator("json", student_modify_schema)
def modify_profile(args):
    """Modify a profile of a student

    Args:
        id (str): The id of the student to modify (optional)
        name (str): The name of the student (optional)
        bio (str): The bio of the student (optional)
        email (str): The email of the student (optional)
        profilePicture (str): The profile picture of the student (optional)
        location (str): The location of the student (optional)
        phoneNumber (str): The phone number of the student (optional)

    Returns:
        success (bool): True

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the user is not an admin
        ExpectedError: If the student profile does not exist

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)
    mod_id = admin_id_check(args)

    student = student_view(id=mod_id)
    if not student:
        raise ExpectedError("Profile does not exist", 404)

    name = args["name"] if "name" in args else student.name
    bio = args["bio"] if "bio" in args else student.bio
    email = args["email"] if "email" in args else student.email
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
            "email": email,
            "profilePicture": profile_picture,
            "location": location,
            "phoneNumber": phone_number,
        },
    )

    return jsonify({"success": True}), 200


@student.route("/", methods=["DELETE"])
@error_decorator
def delete_profile():
    """Delete a student

    Args:
        id (str): The id of the student to delete (admin)

    Returns:
        success (bool): True

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the user is not an admin
        ExpectedError: If the student profile does not exist

    """
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
    """Gets the list of appointments the current student has requested, the tutor accepted, and completed

    Args:

    Returns:
        requested (list of str): a list of appointment ids that are requested
        accepted (list of str): a list of appointment ids that are accepted
        completed (list of str): a list of appointment ids that are completed

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the user is not a student

    """
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
