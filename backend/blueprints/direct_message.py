from typing import TypedDict
from flask import Blueprint, jsonify, session, current_app
from pusher import Pusher
from uuid import uuid4
from prisma.models import DirectMessage, Notification, User
from datetime import datetime, MINYEAR, timezone
from jsonschemas import direct_message_schema
from helpers.views import user_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

direct_message = Blueprint("direct_message", __name__)


@direct_message.route("/all", methods=["GET"])
@error_decorator
def dm_all():
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    dms = DirectMessage.prisma().find_many(
        where={
            "OR": [
                {"fromUserId": session["user_id"]},
                {"otherUserId": session["user_id"]},
            ]
        },
        include={"messages": {"order_by": {"sentTime": "desc"}}},
    )
    sorted_dms = sorted(
        dms,
        key=lambda dm: dm.messages[0].sentTime
        if len(dm.messages) != 0
        else datetime(MINYEAR, 1, 1),
        reverse=True,
    )

    otherIds = []
    for dm in sorted_dms:
        if dm.fromUserId == session["user_id"]:
            otherIds.append(dm.otherUserId)
        elif dm.otherUserId == session["user_id"]:
            otherIds.append(dm.fromUserId)

    return jsonify({"otherIds": otherIds}), 200


@direct_message.route("/<other_id>", methods=["GET"])
@error_decorator
def dm_info(other_id):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    direct_message = DirectMessage.prisma().find_first(
        where={
            "OR": [
                {"fromUserId": session["user_id"], "otherUserId": other_id},
                {"fromUserId": other_id, "otherUserId": session["user_id"]},
            ]
        },
        include={"messages": {"order_by": {"sentTime": "desc"}}},
    )
    if direct_message is None:
        return jsonify({"messages": []}), 200

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


class MessageInfo(TypedDict, total=True):
    id: str
    sentTime: str
    content: str
    sentBy: dict


def dm_create_message(
    dm_id: str, sender_id: str, receiver_id: str, message_info: MessageInfo
):
    DirectMessage.prisma().upsert(
        where={"id": dm_id},
        data={
            "create": {
                "id": dm_id,
                "fromUser": {"connect": {"id": sender_id}},
                "otherUser": {"connect": {"id": receiver_id}},
                "messages": {"create": message_info},
            },
            "update": {"messages": {"create": message_info}},
        },
    )


@direct_message.route("/", methods=["POST"])
@error_decorator
@validate_decorator("json", direct_message_schema)
def dm_message(args):
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
        }
    )
    dm_id = dm.id if dm else str(uuid4())

    message_info = {
        "id": str(uuid4()),
        "sentTime": datetime.now(timezone.utc),
        "content": args["message"],
        "sentBy": {"connect": {"id": session["user_id"]}},
    }

    pusher_client: Pusher = current_app.extensions["pusher"]
    channel_info = pusher_client.channel_info(args["otherId"])
    if channel_info["occupied"]:
        try:
            pusher_client.trigger(
                args["otherId"],
                "direct_message",
                {
                    "fromId": session["user_id"],
                    "content": message_info["content"],
                    "sentTime": message_info["sentTime"].isoformat(),
                },
            )
        except (ValueError, TypeError):
            raise ExpectedError("Message format is invalid", 400)

        dm_create_message(dm_id, session["user_id"], args["otherId"], message_info)
    else:
        dm_create_message(dm_id, session["user_id"], args["otherId"], message_info)

        user = user_view(id=session["user_id"])
        Notification.prisma().create(
            data={
                "id": str(uuid4()),
                "forUser": {"connect": {"id": args["otherId"]}},
                "message": {"connect": {"id": message_info["id"]}},
                "content": f"Received a direct message from {user.name}",
            }
        )

    return (
        jsonify(
            {"id": message_info["id"], "sentTime": message_info["sentTime"].isoformat()}
        ),
        200,
    )
