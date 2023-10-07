from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Student, Admin
from re import fullmatch
from uuid import uuid4
from hashlib import sha256
from backend.helpers.error_handlers import (
    ExpectedError,
    error-decorator,
)

tutor = Blueprint("tutor", __name__)

@tutor.route("/tutorprofile", methods=["GET"])
@error_decorator
def get_profile():
    args = request.get_json()

    tutor = Tutor.prisma().find_unique(where={"id" : args["id"]})

    if tutor is None:
        raise ExpectedError("Profile does not exist" , 404)
    #need to validate course offerings
    return jsonify({
        "id": tutor.id,
        "name": tutor.name,
        "bio": tutor.bio,
        "profilePicture": tutor.profilePicture,
        "location": tutor.location,
        "phonenumber": tutor.phonenumber,
        "rating": tutor.rating,
        "courseOfferings": tutor.courseOfferings,
        "timesAvailable": tutor.timesAvailable
    })

@tutor.route("/modifytutorprofile", methods=["PUT"])
@error_decorator
def modify_profile():
    args = request.get_json()

    admin = Admin.prisma().find_unique(where={"id" : session["user_id"]})
    if admin is None and session["user_id"] !=args["id"]:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    tutor = Tutor.prisma().find_unique(where={"id": args["id"]})
    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)


    if "name" not in args:
        name = tutor.name
    if "bio" not in args:
        bio = tutor.bio
    if "profilePicture" not in args:
        profilePicture = tutor.profilePicture
    if "location" not in args:
        location = tutor.location
    if "phoneNumber" not in args:
        phoneNumber = tutor.phoneNumber
    #need to validate courseofferings
    if "courseOfferings" not in args:
        courseOfferings = tutor.courseOfferings
    if "timesAvailable" not in args:
        timesAvailable = tutor.timesAvailable
    #timesavailable should also change when appointments are made and cancelled

    Tutor.prisma.update({
        where = {"id: tutor_id"},
        data = {
            "name": name,
            "bio": bio,
            "profilePicture": profilePicture,
            "location": location,
            "phoneNumber": phoneNumber,
            "courseOfferings": courseOfferings,
            "timesAvailable": timesAvailable
        }
    })

    return jsonify({"success": True})

@student.route("/deletetutorprofile", methods=["DELETE"])
@error_decorator
def delete_profile():
    args = request.get_json()

    admin = Admin.prisma.find_unique(where={"id": args["id"]})
    if admin is None and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to delete this profile", 403)
    
    tutor = Tutor.prisma.find_unique(where={"id": args["id"]})

    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    Tutor.prisma.delete({
        where = {"id": tutor.id},
    })

    return jsonify({"success": True})