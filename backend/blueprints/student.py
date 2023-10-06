from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Student, Admin
from re import fullmatch
from uuid import uuid4
from hashlib import sha256
from backend.helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

student = Blueprint("student", __name__)

################### CLARIFY ON ARGS ERROR CHECKING ###############

@student.route("/", methods=["GET"])
@error_decorator
def get_profile():
    args = request.get_json()

    student = Student.prisma().find_unique(where={"id": args["id"]})

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    return jsonify({
        "id": student.id,
        "name": student.name,
        "bio": student.bio,
        "profilePicture": student.profilePicture,
        "location": student.location,
        "phoneNumber": student.phoneNumber
    })

@student.route("/", methods=["PUT"])
@error_decorator
def modify_profile():
    args = request.get_json()

    admin = Admin.prisma().find_unique(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    student = Student.prisma().find_unique(where={"id": args["id"]})
    if not student:
        raise ExpectedError("Profile does not exist", 404)

    if "name" not in args or len(str(args["name"]).lower().strip()) == 0:
        name = student.name
    if "bio" not in args:
        bio = student.bio
    if "profilePicture" not in args:
        profilePicture = student.profilePicture
    if "location" not in args:  
        location = student.location
    if "phoneNumber" not in args:
        phoneNumber = student.phoneNumber
    
    Student.prisma().update(
        where = {"id": student.id},
        data = {
            "name": name,
            "bio": bio,
            "profilePicture": profilePicture,
            "location": location,
            "phoneNumber": phoneNumber
        }
    )

    return jsonify({"success": True}) 

@student.route("/", methods=["DELETE"])
@error_decorator
def delete_profile():
    args = request.get_json()

    admin = Admin.prisma().find_unique(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to delete this profile", 403)
    
    student = Student.prisma().find_unique(where={"id": args["id"]})

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    Student.prisma().delete(where={"id": args["id"]})

    return jsonify({"success": True})
    
    