from flask import Blueprint, jsonify, session, current_app
from pusher import Pusher
from prisma import Prisma
from prisma.models import Appointment, Rating, Message, Notification
from prisma.errors import RecordNotFoundError
from jsonschemas import (
    appointment_accept_schema,
    appointment_request_schema,
    appointment_delete_schema,
    appointment_message_schema,
    appointment_messages_schema,
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
    appointment = Appointment.prisma().find_unique(where={"id": appointment_id})
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

    return jsonify(return_val), 200


@appointment.route("/accept", methods=["PUT"])
@error_decorator
@validate_decorator("json", appointment_accept_schema)
def appointment_accept(args):
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

    Appointment.prisma().delete(where={"id": args["id"]})

    return jsonify({"success": True}), 200


@appointment.route("/", methods=["PUT"])
@error_decorator
@validate_decorator("json", appointment_modify_schema)
def appointment_modify(args):
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

    return jsonify({"success": True}), 200


@appointment.route("/rating", methods=["POST"])
@error_decorator
@validate_decorator("json", appointment_rating_schema)
def appointment_rating(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    appointment = Appointment.prisma().find_unique(where={"id": args["id"]})
    if not appointment:
        raise ExpectedError("Appointment does not exist", 400)

    if session["user_id"] != appointment.studentId:
        raise ExpectedError("User is not the student of the appointment", 403)

    if appointment.endTime > datetime.now(timezone.utc):
        raise ExpectedError("Appointment isn't complete yet", 400)

    Rating.prisma().create(
        data={
            "id": str(uuid4()),
            "score": args["rating"],
            "appointment": {"connect": {"id": args["id"]}},
            "createdFor": {"connect": {"id": appointment.tutorId}},
        }
    )

    return jsonify({"success": True}), 200


@appointment.route("/messages", methods=["GET"])
@error_decorator
@validate_decorator("json", appointment_messages_schema)
def appointment_messages(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    appointment = Appointment.prisma().find_unique(where={"id": args["id"]})
    if not appointment:
        raise ExpectedError("Appointment does not exist", 400)

    if (
        session["user_id"] != appointment.studentId
        and session["user_id"] != appointment.tutorId
    ):
        raise ExpectedError("User is not the tutor or student of the appointment", 403)

    messages = Message.prisma().find_many(
        where={"appointmentId": args["id"]},
        include={"messages": {"orderBy": {"sentTime": "desc"}}},
    )

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
                    for message in messages
                ]
            }
        ),
        200,
    )


@appointment.route("/message", methods=["POST"])
@error_decorator
@validate_decorator("json", appointment_message_schema)
def appointment_message(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    appointment = Appointment.prisma().find_unique(where={"id": args["id"]})
    if not appointment:
        raise ExpectedError("Appointment does not exist", 400)

    if (
        session["user_id"] != appointment.studentId
        and session["user_id"] != appointment.tutorId
    ):
        raise ExpectedError("User is not the tutor or student of the appointment", 403)

    if session["user_id"] == appointment.studentId:
        other_id = appointment.tutorId
    else:
        other_id = appointment.studentId

    msg = Message.prisma().create(
        data={
            "id": str(uuid4()),
            "sentTime": datetime.now(),
            "content": args["message"],
            "sentBy": {"connect": {"id": appointment.studentId}},
            "appointment": {"connect": {"id": args["id"]}},
        }
    )

    pusher_client: Pusher = current_app.extensions["pusher"]
    channel_info = pusher_client.channel_info(other_id, ["subscription_count"])
    if channel_info["subscription_count"] >= 1:
        try:
            pusher_client.trigger(
                other_id,
                "message",
                {
                    "fromId": session["user_id"],
                    "content": msg.content,
                    "sentTime": msg.sentTime.isoformat(),
                },
            )
        except (ValueError, TypeError):
            raise ExpectedError("Message format is invalid", 400)
    else:
        user = user_view(id=session["user_id"])
        Notification.prisma().create(
            data={
                "id": str(uuid4()),
                "forUser": {"connect": {"id": other_id}},
                "message": {"connect": {"id": msg.id}},
                "content": f"Received a direct message from {user.name}",
            }
        )

    return (
        jsonify({"id": msg.id, "sentTime": msg.sentTime.isoformat()}),
        200,
    )
