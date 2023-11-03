from flask import Blueprint, jsonify, session, current_app
from prisma.models import User, DirectMessage, Notification
from uuid import uuid4
from hashlib import sha256

from pusher import Pusher
from jsonschemas import direct_message_info_schema, direct_message_schema
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
    notifications_to_clear = []
    for message in direct_message.messages:
        if message.notification is not None:
            notifications_to_clear.append(message.notification.id)

        messages.append(
            {
                "id": message.id,
                "sentBy": message.sentById,
                "sentTime": message.sentTime.isoformat(),
                "content": message.content,
            }
        )

    Notification.prisma().delete_many(where={"id": {"in": notifications_to_clear}})

    return jsonify({"messages": messages}), 200


@direct_message.route("/", methods=["POST"])
@error_decorator
@validate_decorator("json", direct_message_schema)
def direct_message(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    user = user_view(id=args["otherId"])
    if user is None:
        raise ExpectedError("otherId does not correspond to an user", 400)

    direct_message = DirectMessage.prisma().find_first(
        where={
            "OR": [
                {"fromUserId": session["user_id"], "otherUserId": args["otherId"]},
                {"fromUserId": args["otherId"], "otherUserId": session["user_id"]},
            ]
        },
        include={"messages": {"order_by": {"sentTime": "desc"}}},
    )
    pusher_client: Pusher = current_app.extensions["pusher"]
    dm_id = direct_message.id if direct_message else str(uuid4())
    channel_info = pusher_client.channel_info(dm_id, ["subscription_count"])
    if channel_info["subscription_count"] >= 1:
        try:
            pusher_client.trigger(dm_id, "direct_message", args["message"])
        except ValueError:
            raise ExpectedError("Message format is invalid", 400)
    # else:
    #     Notification.prisma().create(data={"id": str(uuid4())})
