from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Student, Admin, Subject, TutorAvailability
from re import fullmatch
from uuid import uuid4
from datetime import datetime
from hashlib import sha256
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

tutor = Blueprint("tutor", __name__)


@tutor.route("/", methods=["GET"])
@error_decorator
def get_profile():
    args = request.get_json()

    tutor = Tutor.prisma().find_unique(
        where={"id": args["id"]},
        include={
            "courseOfferings": {"include": {"tutorsTeaching": True}},
            "timesAvailable": True,
        },
    )

    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    if tutor.courseOfferings is None:
        courseOfferings = []
    else:
        courseOfferings = list(map(formatCourseOfferings, tutor.courseOfferings))

    if tutor.timesAvailable is None:
        timesAvailable = []
    else:
        timesAvailable = list(map(formatTimesAvailable, tutor.timesAvailable))

    return jsonify(
        {
            "id": tutor.id,
            "name": tutor.name,
            "bio": tutor.bio,
            "email": tutor.email,
            "rating": tutor.rating,
            "profilePicture": tutor.profilePicture,
            "location": tutor.location,
            "phoneNumber": tutor.phoneNumber,
            "courseOfferings": courseOfferings,
            "timesAvailable": timesAvailable,
        }
    )


def formatCourseOfferings(subject):
    return subject.name


def formatTimesAvailable(timeBlock):
    return {"startTime": timeBlock.startTime, "endTime": timeBlock.endTime}


@tutor.route("/", methods=["PUT"])
@error_decorator
def modify_profile():
    args = request.get_json()

    admin = Admin.prisma().find_unique(where={"id": session["user_id"]})
    if admin is None and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    tutor = Tutor.prisma().find_unique(
        where={"id": args["id"]},
        include={
            "courseOfferings": {"include": {"tutorsTeaching": True}},
            "timesAvailable": True,
        },
    )

    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    if "name" not in args:
        name = tutor.name
    else:
        name = args["name"]

    # name = tutor.name if "name" not in args else name = args["name"]

    if "bio" not in args:
        bio = tutor.bio
    else:
        bio = args["bio"]

    if "email" not in args:
        email = tutor.email
    else:
        email = args["email"]

    if "profilePicture" not in args:
        profilePicture = tutor.profilePicture
    else:
        profilePicture = args["profilePicture"]

    if "location" not in args:
        location = tutor.location
    else:
        location = args["location"]

    if "phoneNumber" not in args:
        phoneNumber = tutor.phoneNumber
    else:
        phoneNumber = args["phoneNumber"]

    # need to validate courseofferings
    if "courseOfferings" in args:
        courseOfferings = args["courseOfferings"]
        addingSubjects(courseOfferings, args["id"])

    if "timesAvailable" not in args:
        timesAvailable = tutor.timesAvailable
    else:
        timesAvailable = args["timesAvailable"]
        addingTimes(timesAvailable, args["id"])
    # timesavailable should also change when appointments are made and cancelled

    Tutor.prisma().update(
        where={"id": tutor.id},
        data={
            "name": name,
            "bio": bio,
            "email": email,
            "profilePicture": profilePicture,
            "location": location,
            "phoneNumber": phoneNumber,
        },
    )

    # call function that updates course offerings, passin through the list of courseofferings

    return jsonify({"success": True})


@tutor.route("/", methods=["DELETE"])
@error_decorator
def delete_profile():
    args = request.get_json()

    admin = Admin.prisma().find_unique(where={"id": args["id"]})
    if admin is None and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to delete this profile", 403)

    tutor = Tutor.prisma().find_unique(where={"id": args["id"]})

    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    Tutor.prisma().delete(where={"id": tutor.id})

    return jsonify({"success": True})


def addingSubjects(courseOfferings, tutorId):
    tutor = Tutor.prisma().find_unique(
        where={"id": tutorId},
        include={
            "courseOfferings": {"include": {"tutorsTeaching": True}},
            "timesAvailable": True,
        },
    )

    # tutor is changing their subjects offered to zero
    # wipe previous stuff if required
    if courseOfferings == None or len(courseOfferings) == 0:
        if tutor.courseOfferings != None:
            for subject in tutor.courseOfferings:
                Tutor.prisma().update(
                    where={"id": tutorId},
                    data={"courseOfferings": {"disconnect": {"name": subject.name}}},
                )
        return

    # tutor is adding/deleting subjects
    # wipe previous stuff, if there is any
    if tutor.courseOfferings != None:
        for subject in tutor.courseOfferings:
            Tutor.prisma().update(
                where={"id": tutorId},
                data={"courseOfferings": {"disconnect": {"name": subject.name}}},
            )

    # connect all subjects in the courseofferings list back to the tutor record
    # connect the tutor to the respective subject

    for subjectName in courseOfferings:
        subject = Subject.prisma().find_first(where={"name": subjectName})

        if subject is None:
            raise ExpectedError("Subject isnt offered", 404)

        Tutor.prisma().update(
            where={"id": tutorId},
            data={"courseOfferings": {"connect": {"name": subjectName}}},
        )


def addingTimes(timesAvailable, tutorId):
    tutor = Tutor.prisma().find_unique(where={"id": tutorId})

    Tutor.prisma().update(
        where={"id": tutorId}, data={"timesAvailable": {"deleteMany": {}}}
    )

    if timesAvailable is None:
        return

    # create all the tutoravailability records again with the new timesAvailable
    for timeBlock in timesAvailable:
        try:
            st = datetime.fromisoformat(timeBlock["startTime"])
            et = datetime.fromisoformat(timeBlock["endTime"])
        except ValueError:
            raise ExpectedError("timeRange field(s) were malformed", 400)

        if st > et:
            raise ExpectedError("endTime cannot be less than startTime", 400)
        elif st < datetime.now():
            raise ExpectedError("startTime must be in the future", 400)

        Tutor.prisma().update(
            where={"id": tutorId},
            data={
                "timesAvailable": {
                    "create": {
                        "id": str(uuid4()),
                        "startTime": st,
                        "endTime": et,
                    }
                }
            },
        )
