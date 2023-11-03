from flask import Blueprint, jsonify, session, request
from prisma.models import User, DirectMessage, Notification
from uuid import uuid4
from hashlib import sha256
from jsonschemas import direct_message_info_schema
from helpers.views import user_view, admin_view, tutor_view, student_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

direct_message = Blueprint("direct_message", __name__)


@direct_message.route("/all", methods=["GET"])
@error_decorator
def direct_message_all():
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    user_info = User.prisma().find_unique(
        where={"id": session["user_id"]},
        include={
            "messages": {
                "where": {"directMessage": True},
                "order_by": {"sentTime": "desc"},
            }
        },
    )

    return (
        jsonify(
            {
                "otherIds": [
                    message.directMessage.otherUserId for message in user_info.messages
                ]
            }
        ),
        200,
    )


@direct_message.route("/", methods=["GET"])
@error_decorator
@validate_decorator("query_string", direct_message_info_schema)
def direct_message_info(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    direct_message = DirectMessage.prisma().find_first(
        where={
            "OR": [
                {"fromUserId": session["user_id"], "otherUserId": args["otherId"]},
                {"fromUserId": args["otherId"], "otherUserId": session["user_id"]},
            ]
        },
        include={"messages": {"order_by": {"sentTime": "desc"}}},
    )
    if direct_message is None:
        return ExpectedError("Direct message doesn't exist", 400)

    messages = []
    for message in direct_message.messages:
        if message.notification is not None:
            Notification.prisma().delete(where={"id": message.notification.id})

        messages.append(
            {
                "id": message.id,
                "sentBy": message.sentById,
                "sentTime": message.sentTime.isoformat(),
                "content": message.content,
            }
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
                    for message in direct_message.messages
                ]
            }
        ),
        200,
    )
