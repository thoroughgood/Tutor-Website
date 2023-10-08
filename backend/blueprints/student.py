from flask import Blueprint, request, jsonify, session
from prisma.models import Student, Admin
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

student = Blueprint("student", __name__)

@student.route("/", methods=["GET"])
@error_decorator
def get_profile():
    args = request.get_json()

    if "id" not in args:
        raise ExpectedError("id field was missing", 400)
    
    student = Student.prisma().find_unique(where={"id": args["id"]})

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    return jsonify(
        {
            "id": student.id,
            "name": student.name,
            "bio": student.bio,
            "profilePicture": student.profilePicture,
            "location": student.location,
            "phoneNumber": student.phoneNumber,
        }
    ), 200


@student.route("/", methods=["PUT"])
@error_decorator
def modify_profile():
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)

    if "name" not in args:
        raise ExpectedError("name field was missing", 400)
    if "bio" not in args:
        raise ExpectedError("bio field was missing", 400)
    if "profilePicture" not in args:
        raise ExpectedError("profilePicture field was missing", 400)
    if "location" not in args:
        raise ExpectedError("location field was missing", 400)
    if "phoneNumber" not in args:
        raise ExpectedError("phoneNumber field was missing", 400)

    admin = Admin.prisma().find_unique(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    student = Student.prisma().find_unique(where={"id": args["id"]})
    if not student:
        raise ExpectedError("Profile does not exist", 404)

    name = (
        args["name"]
        if ("name" in args and len(str(args["name"]).lower().strip()) != 0)
        else student.name
    )
    bio = args["bio"] if "bio" in args else student.bio
    profilePicture = (
        args["profilePicture"] if "profilePicture" in args else student.profilePicture
    )
    location = args["location"] if "location" in args else student.location
    phoneNumber = args["phoneNumber"] if "phoneNumber" in args else student.phoneNumber

    Student.prisma().update(
        where={"id": student.id},
        data={
            "name": name,
            "bio": bio,
            "profilePicture": profilePicture,
            "location": location,
            "phoneNumber": phoneNumber,
        },
    )

    return jsonify({"success": True}), 200


@student.route("/", methods=["DELETE"])
@error_decorator
def delete_profile():
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)

    if "id" not in args:
        raise ExpectedError("id field was missing", 400)

    admin = Admin.prisma().find_unique(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to delete this profile", 403)

    student = Student.prisma().find_unique(where={"id": args["id"]})

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    Student.prisma().delete(where={"id": args["id"]})

    return jsonify({"success": True}), 200