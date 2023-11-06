from flask import Blueprint, jsonify, session, current_app
from pusher import Pusher
from prisma import Prisma
from uuid import uuid4
from prisma.models import DirectMessage, Notification
from datetime import datetime, MINYEAR, timezone
from jsonschemas import direct_message_info_schema, direct_message_schema
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


@direct_message.route("/", methods=["GET"])
@error_decorator
@validate_decorator("query_string", direct_message_info_schema)
def dm_info(args):
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
def dm_message(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    other_user = user_view(id=args["otherId"])
    if other_user is None:
        raise ExpectedError("otherId does not correspond to an user", 400)

    prisma_client: Prisma = current_app.extensions["prisma"]
    pusher_client: Pusher = current_app.extensions["pusher"]
    with prisma_client.tx() as transaction:
        dm = transaction.directmessage.find_first(
            where={
                "OR": [
                    {"fromUserId": session["user_id"], "otherUserId": args["otherId"]},
                    {"fromUserId": args["otherId"], "otherUserId": session["user_id"]},
                ]
            }
        )

        message_info = {
            "id": str(uuid4()),
            "sentTime": datetime.now(timezone.utc),
            "content": args["message"],
            "sentBy": {"connect": {"id": session["user_id"]}},
        }

        dm_id = dm.id if dm else str(uuid4())
        if dm is not None:
            transaction.directmessage.update(
                where={"id": dm_id}, data={"messages": {"create": message_info}}
            )
        else:
            transaction.directmessage.upsert(
                where={"id": dm_id},
                data={
                    "create": {
                        "id": dm_id,
                        "fromUser": {"connect": {"id": session["user_id"]}},
                        "otherUser": {"connect": {"id": args["otherId"]}},
                        "messages": {"create": message_info},
                    },
                    "update": {"messages": {"create": message_info}},
                },
            )

        channel_info = pusher_client.channel_info(
            args["otherId"], ["subscription_count"]
        )
        if channel_info["subscription_count"] >= 1:
            try:
                pusher_client.trigger(
                    args["otherId"],
                    "direct_message",
                    {
                        "fromId": session["user_id"],
                        "content": message_info["content"],
                        "sentTime": message_info["sentTime"],
                    },
                )
            except ValueError:
                raise ExpectedError("Message format is invalid", 400)
        else:
            transaction.notification.create(
                data={
                    "id": str(uuid4()),
                    "forUser": {"connect": {"id": args["otherId"]}},
                    "message": {"connect": {"id": message_info["id"]}},
                }
            )

    return (
        jsonify(
            {"id": message_info["id"], "sentTime": message_info["sentTime"].isoformat()}
        ),
        200,
    )
