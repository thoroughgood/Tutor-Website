from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Subject, User
from jsonschemas import tutor_modify_schema
from helpers.process_time_block import process_time_block
from helpers.views import tutor_view
from helpers.admin_id_check import admin_id_check
from helpers.rating_calc import rating_calc
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

tutor = Blueprint("tutor", __name__)


def addingSubjects(course_offerings, tutor):
    """Adds the subjects to the tutor's course offerings

    Args:
        course_offerings (list of str): the list of subjects to add
        tutor (User): the tutor to add the subjects to

    """
    # tutor is adding/deleting subjects
    # wipe previous stuff, if there is any
    Tutor.prisma().update(
        where={"id": tutor.id},
        data={
            "courseOfferings": {
                "disconnect": [
                    {"name": subject.name} for subject in tutor.course_offerings
                ]
            }
        },
    )

    # tutor is changing their subjects offered to zero
    if course_offerings is None or len(course_offerings) == 0:
        return

    # connect all subjects in the courseofferings list back to the tutor record
    # connect the tutor to the respective subject
    data = [{"name": subject_name} for subject_name in course_offerings]
    # Given connect or create does not yet exist in prisma python client,
    # we must resort to this instead
    Subject.prisma().create_many(
        data=data,
        skip_duplicates=True,
    )
    Tutor.prisma().update(
        where={"id": tutor.id},
        data={"courseOfferings": {"connect": data}},
    )


def addingTimes(times_available, tutor):
    """Adds the availabilities  to the tutor's time schedule

    Args:
        times_available (list of str): the list of times available
        tutor (User): the tutor to add the availabilities  to

    Raises:
        ExpectedError: If the times_available are overlapping

    """
    # tutor is adding/deleting timesAvailable
    # wipe previous stuff, if there is any
    Tutor.prisma().update(
        where={"id": tutor.id}, data={"timesAvailable": {"deleteMany": {}}}
    )

    if times_available is None or len(times_available) == 0:
        return

    formatted_availabilities = sorted(
        map(lambda t: process_time_block(t), times_available),
        key=lambda d: d["startTime"],
    )

    to_create = []
    prev_block = None
    # create all the tutoravailability records again with the new timesAvailable
    for i, time_block in enumerate(formatted_availabilities):
        if i == 0:
            to_create.append(time_block)
            prev_block = time_block
            continue

        if prev_block["endTime"] > time_block["startTime"]:
            raise ExpectedError("Time availabilities should not overlap", 400)

        to_create.append(time_block)
        prev_block = time_block

    Tutor.prisma().update(
        where={"id": tutor.id},
        data={"timesAvailable": {"create": to_create}},
    )


@tutor.route("/<tutor_id>", methods=["GET"])
@error_decorator
def get_profile(tutor_id):
    """Get the profile of a tutor

    Args:
        tutor_id (str): The id of the tutor to get

    Returns:
        id (str): The id of the tutor to modify (optional)
        name (str): The name of the tutor (optional)
        bio (str): The bio of the tutor (optional)
        email (str): The email of the tutor (optional)
        profilePicture (str): The profile picture of the tutor (optional)
        location (str): The location of the tutor (optional)
        phoneNumber (str): The phone number of the tutor (optional)
        courseOfferings (list of str): The course offerings of the tutor (optional)
        timesAvailable (list of dict): The times available of the tutor (optional)
            - startTime (str): The start time of the tutor
            - endTime (str): The end time of the tutor

    Raises:
        ExpectedError: If the times_available are overlapping

    """
    tutor = tutor_view(id=tutor_id)
    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    if tutor.course_offerings is None:
        course_offerings = []
    else:
        course_offerings = list(map(lambda c: c.name, tutor.course_offerings))

    if tutor.times_available is None:
        times_available = []
    else:
        times_available = list(
            map(
                lambda d: {
                    "startTime": d.startTime.isoformat(),
                    "endTime": d.endTime.isoformat(),
                },
                tutor.times_available,
            )
        )

    if tutor.ratings is None:
        rating = 0
    else:
        rating = rating_calc(tutor.ratings)

    if tutor.documents is None:
        documents = []
    else:
        documents = list(map(lambda d: d.id, tutor.documents))

    return jsonify(
        {
            "id": tutor.id,
            "name": tutor.name,
            "bio": tutor.bio if tutor.bio else "",
            "email": tutor.email,
            "rating": rating,
            "profilePicture": tutor.profile_picture,
            "location": tutor.location,
            "phoneNumber": tutor.phone_number,
            "courseOfferings": course_offerings,
            "timesAvailable": times_available,
            "documentIds": documents,
        }
    )


@tutor.route("/profile", methods=["PUT"])
@error_decorator
@validate_decorator("json", tutor_modify_schema)
def modify_profile(args):
    """Modify a profile of a tutor

    Args:
        id (str): The id of the tutor to modify (optional)
        name (str): The name of the tutor (optional)
        bio (str): The bio of the tutor (optional)
        email (str): The email of the tutor (optional)
        profilePicture (str): The profile picture of the tutor (optional)
        location (str): The location of the tutor (optional)
        phoneNumber (str): The phone number of the tutor (optional)
        courseOfferings (list of str): The course offerings of the tutor (optional)
        timesAvailable (list of dict): The times available of the tutor (optional)
            - startTime (str): The start time of the tutor
            - endTime (str): The end time of the tutor

    Returns:
        success (bool): True

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the tutor profile does not exist

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)

    modify_tutor_id = admin_id_check(args)

    tutor = tutor_view(id=modify_tutor_id)
    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    name = tutor.name if "name" not in args else args["name"]
    bio = tutor.bio if "bio" not in args else args["bio"]
    email = tutor.email if "email" not in args else args["email"]

    profile_picture = (
        tutor.profile_picture
        if "profilePicture" not in args
        else args["profilePicture"]
    )
    location = tutor.location if "location" not in args else args["location"]
    phone_number = (
        tutor.phone_number if "phoneNumber" not in args else args["phoneNumber"]
    )
    if "courseOfferings" in args:
        addingSubjects(args["courseOfferings"], tutor)

    if "timesAvailable" in args:
        addingTimes(args["timesAvailable"], tutor)

    User.prisma().update(
        where={"id": tutor.id},
        data={
            "name": name,
            "bio": bio,
            "email": email,
            "profilePicture": profile_picture,
            "location": location,
            "phoneNumber": phone_number,
        },
    )

    return jsonify({"success": True})


@tutor.route("/", methods=["DELETE"])
@error_decorator
def delete_profile():
    """Delete a tutor

    Args:
        id (str): The id of the tutor to delete (admin)

    Returns:
        success (bool): True

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the tutor profile does not exist

    """
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)

    delete_tutor_id = admin_id_check(args)

    tutor = tutor_view(id=delete_tutor_id)
    if tutor is None:
        raise ExpectedError("Profile does not exist", 404)

    # All fields other than course_offerings will cascade delete in the db
    Tutor.prisma().update(
        where={"id": tutor.id},
        data={
            "courseOfferings": {
                "disconnect": [
                    {"name": subject.name} for subject in tutor.course_offerings
                ]
            }
        },
    )

    User.prisma().delete(where={"id": tutor.id})

    return jsonify({"success": True})


@tutor.route("/<tutor_id>/appointments", methods=["GET"])
@error_decorator
def get_tutor_appointments(tutor_id):
    """Get appointments of the current tutor.

    Args:
        tutor_id (str): The id of the tutor

    Returns:
        yourAppointments (list of str): the list of appointments of the tutor
        other (list of str): the list of appointments of the tutor

    Raises:
        ExpectedError: No tutor related to the id

    """
    tutor = tutor_view(id=tutor_id)

    if tutor is None:
        raise ExpectedError("no tutor relates to the id", 404)
    your_appointments = []
    other = []

    for appointment in tutor.appointments:
        if "user_id" in session and (
            appointment.studentId == session["user_id"]
            or appointment.tutorId == session["user_id"]
        ):
            your_appointments.append(appointment.id)
            continue

        other.append(appointment.id)

    return (
        jsonify(
            {
                "yourAppointments": your_appointments,
                "other": other,
            }
        ),
        200,
    )
