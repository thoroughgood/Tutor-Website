from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Student, Admin
from re import fullmatch
from uuid import uuid4
from hashlib import sha256
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

student = Blueprint("student", __name__)

################### CLARIFY ON ARGS ERROR CHECKING ###############

@student.route("/student/profile", methods=["GET, PUT, DELETE"])
@error_decorator
def get_profile():
    args = request.get_json()

    student = Student.prisma().find_first(where={"id": args["id"]})

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

def modify_profile():
    args = request.get_json()

    admin = Admin.prisma().find_first(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    student = Student.prisma().find_first(where={"id": args["id"]})
    if not student:
        raise ExpectedError("Profile does not exist", 404)

    student.name = args["name"]
    student.bio = args["bio"]
    student.profilePicture = args["profilePicture"]
    student.location = args["location"]
    student.phoneNumber = args["phoneNumber"]

    return jsonify({"success": True}) 

def delete_profile():
    args = request.get_json()

    admin = Admin.prisma().find_first(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to delete this profile", 403)
    
    student = Student.prisma().find_first(where={"id": args["id"]})

    if not student:
        raise ExpectedError("Profile does not exist", 404)

    Student.prisma().delete(where={"id": args["id"]})

    return jsonify({"success": True})
    
    