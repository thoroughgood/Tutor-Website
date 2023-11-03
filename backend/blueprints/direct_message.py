from flask import Blueprint, jsonify, session, current_app
from prisma.models import User, DirectMessage, Notification
from prisma.errors import RecordNotFoundError
from datetime import datetime
from uuid import uuid4
from typing import List, TypedDict
from pusher import Pusher
from jsonschemas import direct_message_info_schema, direct_message_schema
from helpers.views import user_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

direct_message = Blueprint("direct_message", __name__)


class MessageInfo(TypedDict, total=True):
    id: str
    sentTime: datetime
    content: str
    sentBy: str


def direct_message_add_message(
    dm_id: str, sender_id: str, receiver_id: str, message: str
) -> MessageInfo:
    message_info = {
        "id": str(uuid4()),
        "sentTime": datetime.now(),
        "content": message,
        "sentBy": {"connect": {"id": sender_id}},
    }

    try:
        DirectMessage.prisma().update(
            where={"id": dm_id},
            data={"messages": {"create": message_info}},
        )
    except RecordNotFoundError:
        DirectMessage.prisma().create(
            data={
                "id": dm_id,
                "fromUser": {"connect": {"id": sender_id}},
                "otherUser": {"connect": {"id": receiver_id}},
                "messages": {"create": message_info},
            }
        )

    message_info["sentBy"] = sender_id
    return message_info


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

    messages: List[MessageInfo] = []
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

    other_user = user_view(id=args["otherId"])
    if other_user is None:
        raise ExpectedError("otherId does not correspond to an user", 400)

    dm = DirectMessage.prisma().find_first(
        where={
            "OR": [
                {"fromUserId": session["user_id"], "otherUserId": args["otherId"]},
                {"fromUserId": args["otherId"], "otherUserId": session["user_id"]},
            ]
        },
        include={"messages": {"order_by": {"sentTime": "desc"}}},
    )
    pusher_client: Pusher = current_app.extensions["pusher"]
    dm_id = dm.id if dm else str(uuid4())
    channel_info = pusher_client.channel_info(dm_id, ["subscription_count"])
    if channel_info["subscription_count"] >= 1:
        try:
            pusher_client.trigger(dm_id, "direct_message", args["message"])
        except ValueError:
            raise ExpectedError("Message format is invalid", 400)

        msg_info = direct_message_add_message(
            dm_id, session["user_id"], other_user.id, args["message"]
        )

    else:
        msg_info = direct_message_add_message(
            dm_id, session["user_id"], other_user.id, args["message"]
        )

        Notification.prisma().create(
            data={
                "id": str(uuid4()),
                "forUser": {"connect": {"id": other_user.id}},
                "message": {"connect": {"id": msg_info["id"]}},
            }
        )

    return jsonify({"id": msg_info["id"], "sentTime": msg_info["sentTime"]})
