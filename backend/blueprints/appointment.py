from flask import Blueprint, jsonify, session, current_app
from pusher import Pusher
from prisma.models import Appointment, Rating, Message, Notification
from prisma.errors import RecordNotFoundError
from jsonschemas import (
    appointment_accept_schema,
    appointment_request_schema,
    appointment_delete_schema,
    appointment_message_schema,
    appointment_modify_schema,
    appointment_rating_schema,
)
from helpers.process_time_block import process_time_block
from uuid import uuid4
from datetime import datetime, timezone
from helpers.views import student_view, tutor_view, user_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

appointment = Blueprint("appointment", __name__)


@appointment.route("/<appointment_id>", methods=["GET"])
@error_decorator
def get_appointment(appointment_id):
    """Get a pre-existing appointment given the id of the appointment

    Args:
        appointment_id (int): the id of the appointment

    Returns:
        id (str): id of the appointment
        startTime (str): start time of the appointment
        endTime (str): end time of the appointment
        studentId (str): id of the student
        tutorId (str): id of the tutor
        tutorAccepted (bool): whether the tutor has accepted the appointment
        rating (int): rating of the appointment (if the user is the student)

    Raises:
        ExpectedError: if the appointment id does not match an appointment

    """
    appointment = Appointment.prisma().find_unique(
        where={"id": appointment_id}, include={"rating": True}
    )
    if appointment is None:
        raise ExpectedError("Given id does not correspond to an appointment", 404)

    return_val = {
        "id": appointment.id,
        "startTime": appointment.startTime.isoformat(),
        "endTime": appointment.endTime.isoformat(),
        "tutorId": appointment.tutorId,
        "tutorAccepted": appointment.tutorAccepted,
    }

    if "user_id" in session and (
        appointment.tutorId == session["user_id"]
        or appointment.studentId == session["user_id"]
    ):
        return_val["studentId"] = appointment.studentId

    if "user_id" in session and appointment.studentId == session["user_id"]:
        return_val["rating"] = appointment.rating.score if appointment.rating else None

    return jsonify(return_val), 200


@appointment.route("/accept", methods=["PUT"])
@error_decorator
@validate_decorator("json", appointment_accept_schema)
def appointment_accept(args):
    """A tutor accepts or rejects an appointment

    Args:
        id (str): The id of the appointment to accept
        accept (bool): Whether to accept or reject the appointment

    Returns:
        id (str): the id of the appointment
        startTime (str): the start time of the appointment
        endTime (str): the end time of the appointment
        studentId (str): the id of the student in the appointment
        tutorId (str): the id of the tutor in the appointment
        tutorAccepted (bool): whether the tutor accept of denys the appointment request

    Raises:
        ExpectedError: id does not match to an appointment or does not involve the logged in tutor

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    tutor = tutor_view(id=session["user_id"])
    if not tutor:
        raise ExpectedError("Must be a tutor to modify appointments", 403)

    try:
        appointment = Appointment.prisma().update(
            where={"id_tutorId": {"id": args["id"], "tutorId": tutor.id}},
            data={"tutorAccepted": args["accept"]},
        )
    except RecordNotFoundError:
        raise ExpectedError(
            "Appointment corresponding to id does not exist or, appointment does not involve tutor",
            400,
        )

    Notification.prisma().create(
        data={
            "id": str(uuid4()),
            "forUser": {"connect": {"id": appointment.studentId}},
            "content": f"{tutor.name} has accepted your appointment",
            "appointment": {"connect": {"id": appointment.id}},
        }
    )

    return (
        jsonify(
            {
                "id": appointment.id,
                "startTime": appointment.startTime.isoformat(),
                "endTime": appointment.endTime.isoformat(),
                "studentId": appointment.studentId,
                "tutorId": appointment.tutorId,
                "tutorAccepted": appointment.tutorAccepted,
            }
        ),
        200,
    )


@appointment.route("/request", methods=["POST"])
@error_decorator
@validate_decorator("json", appointment_request_schema)
def appointment_request(args):
    """Student requests a tutor for an appointment.

    Args:
        startTime (str): the start time of the appointment
        endTime (str): the end time of the appointment
        tutorId (str): the id of the tutor of the appointment

    Returns:
        id (str): the id of the appointment
        startTime (str): the start time of the appointment
        endTime (str): the end time of the appointment
        studentId (str): the id of the student in the appointment
        tutorId (str): the id of the tutor in the appointment
        tutorAccepted (bool): whether the tutor accept of denys the appointment request

    Raises:
        ExpectedError: if the user is not logged in
        ExpectedError: if the user is not a student
        ExpectedError: if the tutor profile does not exist
        ExpectedError: if the tutor does not exist or if the student already has an appointment at that time

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    data = process_time_block(
        {"startTime": args["startTime"], "endTime": args["endTime"]}
    )
    st = data["startTime"]
    et = data["endTime"]

    tutor = tutor_view(id=args["tutorId"])
    if not tutor:
        raise ExpectedError("Tutor profile does not exist", 400)

    student = student_view(id=session["user_id"])
    if not student:
        raise ExpectedError("Profile is not a student", 400)

    if student.appointments is not None:
        for appointment in student.appointments:
            if (
                appointment.startTime <= st < appointment.endTime
                or appointment.startTime < et <= appointment.endTime
            ):
                raise ExpectedError(
                    "Cannot request an appointment which overlaps with another one",
                    400,
                )

    appointment = Appointment.prisma().create(
        data={
            "id": str(uuid4()),
            "startTime": args["startTime"],
            "endTime": args["endTime"],
            "tutorAccepted": False,
            "tutor": {"connect": {"id": args["tutorId"]}},
            "student": {"connect": {"id": session["user_id"]}},
            "notification": {
                "create": {
                    "id": str(uuid4()),
                    "forUser": {"connect": {"id": args["tutorId"]}},
                    "content": f"{student.name} has requested an appointment with you",
                }
            },
        }
    )

    return (
        jsonify(
            {
                "id": appointment.id,
                "startTime": appointment.startTime.isoformat(),
                "endTime": appointment.endTime.isoformat(),
                "studentId": appointment.studentId,
                "tutorId": appointment.tutorId,
                "tutorAccepted": appointment.tutorAccepted,
            }
        ),
        200,
    )


@appointment.route("/", methods=["DELETE"])
@error_decorator
@validate_decorator("json", appointment_delete_schema)
def appointment_delete(args):
    """A tutor can delete an appointment

    Args:
        id (str): the id of the appointment wanting to delete

    Returns:
        success (bool): True

    Raises:
        ExpectedError: if the user is not logged in
        ExpectedError: if the user is not a tutor
        ExpectedError: appointment does not exist
        ExpectedError: logged in user is not the tutor of the appointment

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    tutor = tutor_view(id=session["user_id"])
    if not tutor:
        raise ExpectedError("Logged in user is not a tutor", 404)

    appointment = Appointment.prisma().find_unique(where={"id": args["id"]})
    if not appointment:
        raise ExpectedError("Appointment does not exist", 404)

    if tutor.appointments is None or appointment not in tutor.appointments:
        raise ExpectedError("Logged in user is not the tutor of the appointment", 403)

    Notification.prisma().create(
        data={
            "id": str(uuid4()),
            "forUser": {"connect": {"id": appointment.studentId}},
            "content": f"Your appointment with {tutor.name} has been deleted",
        }
    )

    Notification.prisma().delete_many(where={"appointmentId": appointment.id})

    Appointment.prisma().delete(where={"id": args["id"]})

    return jsonify({"success": True}), 200


@appointment.route("/", methods=["PUT"])
@error_decorator
@validate_decorator("json", appointment_modify_schema)
def appointment_modify(args):
    """A tutor can modify a pre-existing appointment

    Args:
        id (str): the id of the appointment wanting to modify
        startTime (str): the new start time of the appointment
        endTime (str): the new end time of the appointment

    Returns:
        success (bool): True

    Raises:
        ExpectedError: if the user is not logged in
        ExpectedError: logged in user is not a tutor
        ExpectedError: appointment does not exist
        ExpectedError: logged in user is not the tutor of the appointment
        ExpectedError: appointment overlaps with another appointment

    """

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    data = process_time_block(
        {"startTime": args["startTime"], "endTime": args["endTime"]}
    )
    st = data["startTime"]
    et = data["endTime"]

    tutor = tutor_view(id=session["user_id"])
    if not tutor:
        raise ExpectedError("Logged in user is not a tutor", 404)

    appointment = Appointment.prisma().find_unique(where={"id": args["id"]})
    if not appointment:
        raise ExpectedError("Appointment does not exist", 404)

    if appointment not in tutor.appointments:
        raise ExpectedError("Logged in user is not the tutor of the appointment", 403)

    for apt in tutor.appointments:
        if apt != appointment and (
            apt.startTime <= st < apt.endTime or apt.startTime < et <= apt.endTime
        ):
            raise ExpectedError("Appointment overlaps with another appointment", 400)

    Appointment.prisma().update(
        where={"id": args["id"]},
        data={"startTime": args["startTime"], "endTime": args["endTime"]},
    )

    Notification.prisma().create(
        data={
            "id": str(uuid4()),
            "forUser": {"connect": {"id": appointment.studentId}},
            "content": f"Your appointment with {tutor.name} has been modified",
            "appointment": {"connect": {"id": appointment.id}},
        }
    )

    return jsonify({"success": True}), 200


@appointment.route("/rating", methods=["POST"])
@error_decorator
@validate_decorator("json", appointment_rating_schema)
def appointment_rating(args):
    """Rate an appointment given its Id

    Args:
        id (str): the id of the appointment
        rating (int): the rating of the appointment

    Returns:
        success (bool): True

    Raises:
        ExpectedError: if user is not logged in
        ExpectedError: appointment does not exist
        ExpectedError: user is not the student of the appointment
        ExpectedError: appointment is not complete yet

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    appointment = Appointment.prisma().find_unique(
        where={"id": args["id"]}, include={"rating": True}
    )
    if not appointment:
        raise ExpectedError("Appointment does not exist", 400)

    if session["user_id"] != appointment.studentId:
        raise ExpectedError("User is not the student of the appointment", 403)

    if appointment.endTime > datetime.now(timezone.utc):
        raise ExpectedError("Appointment isn't complete yet", 400)

    rating_id = appointment.rating.id if appointment.rating else str(uuid4())
    Rating.prisma().upsert(
        where={"id": rating_id},
        data={
            "create": {
                "id": rating_id,
                "score": args["rating"],
                "appointment": {"connect": {"id": args["id"]}},
                "createdFor": {"connect": {"id": appointment.tutorId}},
            },
            "update": {"score": args["rating"]},
        },
    )

    return jsonify({"success": True}), 200


@appointment.route("/<appointment_id>/messages", methods=["GET"])
@error_decorator
def appointment_messages(appointment_id):
    """Returns all messages of an appointment given its Id, in the order of sentTime descending.

    Args:
        appointment_id (int): the id of the appointment

    Returns:
        messages (list): list of dictionaries containing:
            - id (str): id of the message
            - sentBy (str): id of the user who sent the message
            - sentTime (str): time the message was sent
            - content (str): content of the message

    Raises:
        ExpectedError: if the user is not logged in
        ExpectedError: appointment does not exist
        ExpectedError: user is not the tutor or student of the appointment

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    appointment = Appointment.prisma().find_unique(
        where={"id": appointment_id},
        include={"messages": {"orderBy": {"sentTime": "desc"}}},
    )

    if not appointment:
        raise ExpectedError("Appointment does not exist", 400)

    if (
        session["user_id"] != appointment.studentId
        and session["user_id"] != appointment.tutorId
    ):
        raise ExpectedError("User is not the tutor or student of the appointment", 403)

    return (
        jsonify(
            {
                "messages": [
                    {
                        "id": message.id,
                        "sentBy": message.sentById,
                        "sentTime": message.sentTime.isoformat(),
                        "content": message.content,
                    }
                    for message in appointment.messages
                ]
            }
        ),
        200,
    )


@appointment.route("/message", methods=["POST"])
@error_decorator
@validate_decorator("json", appointment_message_schema)
def appointment_message(args):
    """Sends a message to an appointment given its id.

    Args:
        id (str): the id of the appointment
        message (str): the content of the message

    Returns:
        id (str): the id of the message sent
        sentTime (str): the time the message was sent

    Raises:
        ExpectedError: if the user is not logged in
        ExpectedError: appointment does not exist
        ExpectedError: user is not the tutor or student of the appointment
        ExpectedError: invalid message format

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    appointment = Appointment.prisma().find_unique(where={"id": args["id"]})
    if not appointment:
        raise ExpectedError("Appointment does not exist", 400)

    if session["user_id"] == appointment.studentId:
        other_id = appointment.tutorId
    elif session["user_id"] == appointment.tutorId:
        other_id = appointment.studentId
    else:
        raise ExpectedError("User is not the tutor or student of the appointment", 403)

    message_info = {
        "id": str(uuid4()),
        "sentTime": datetime.now(timezone.utc),
        "content": args["message"],
        "sentBy": {"connect": {"id": session["user_id"]}},
        "appointment": {"connect": {"id": args["id"]}},
    }

    pusher_client: Pusher = current_app.extensions["pusher"]
    channel_info = pusher_client.channel_info(args["id"])
    msg = Message.prisma().create(data=message_info)
    if channel_info["occupied"]:
        try:
            pusher_client.trigger(
                args["id"],
                "appointment_message",
                {
                    "fromId": session["user_id"],
                    "content": message_info["content"],
                    "sentTime": message_info["sentTime"].isoformat(),
                },
            )
        except (ValueError, TypeError):
            raise ExpectedError("Message format is invalid", 400)
        Appointment.prisma().update(
            where={"id": args["id"]},
            data={"messages": {"connect": {"id": msg.id}}},
        )
    else:
        user = user_view(id=session["user_id"])
        Notification.prisma().create(
            data={
                "id": str(uuid4()),
                "forUser": {"connect": {"id": other_id}},
                "message": {"connect": {"id": msg.id}},
                "content": f"Received a message in appointment with {user.name}, for appointment scheduled at {appointment.startTime.isoformat()}",
            }
        )
        Appointment.prisma().update(
            where={"id": args["id"]},
            data={"messages": {"connect": {"id": msg.id}}},
        )

    return (
        jsonify({"id": message_info["id"], "sentTime": message_info["sentTime"]}),
        200,
    )
