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


@student.route("/student/profile", methods=["GET"])
@error_decorator
def view_profile():
    args = request.get_json()

    if session["user_id"] == None:
        raise ExpectedError("No user is logged in", 400)
    
    if not "id" in args:
        raise ExpectedError("id field was missing", 400)

    student = Student.prisma().find_first(where={"id": args["id"]})

    if not student:
        raise ExpectedError("No student exists with this id", 400)
    
    return jsonify({
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "address": student.address,
        "timezones": student.timezones,
        "bio": student.bio,
    })
    

@auth.route("/student/profile", methods=["POST"])
@error_decorator
def edit_profile():
    args = request.get_json()

    if session["user_id"] == None:
        raise ExpectedError("No user is logged in", 400)
    
    if not "id" in args:
        raise ExpectedError("id field was missing", 400)

    student = Student.prisma().find_first(where={"id": args["id"]})

    if not student:
        raise ExpectedError("No student exists with this id", 400)

    if "name" in args:
        student.name = args["name"]
    
    if "email" in args:
        student.email = args["email"]

    if "phone" in args:
        student.phone = args["phone"]
    
    if "address" in args:
        student.address = args["address"]

    if "timezones" in args:
        student.timezones = args["timezones"]

    if "bio" in args:
        student.name = args["bio"]
    
    return jsonify({
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "address": student.address,
        "timezones": student.timezones,
        "bio": student.bio,
    })
      