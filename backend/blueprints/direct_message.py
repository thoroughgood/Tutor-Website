from typing import TypedDict
from flask import Blueprint, jsonify, session, current_app
from pusher import Pusher
from uuid import uuid4
from prisma.models import DirectMessage, Notification
from prisma.errors import UniqueViolationError
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
    """Retrieves all ids of other users the session user has messaged or received
    a message from, sorted by most recently messaged/received from.

    Args:

    Returns:
        (json): dictionary containing:
            - otherIds (list of str): list of ids of other users the session user
            has messaged or received

    Raises:
        ExpectedError: If the user is not logged in

    """
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
        else datetime(MINYEAR, 1, 1, tzinfo=timezone.utc),
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
    """Retrieves the direct messages of a session user with another user given
    their Id in the order of sentTime descending.

    Query Params:
        other_id (int): The id of the other user

    Returns:
        (json): dictionary containing:
            - messages (list): list of dictionaries containing:
                - id (str): id of the message
                - sentBy (str): id of the user who sent the message
                - sentTime (str): time the message was sent
                - content (str): content of the message

    Raises:
        ExpectedError: If the user is not logged in

    """
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
    """Creates a message in a direct message conversation between two users

    Args:
        dm_id (str): id of the direct message conversation
        sender_id (str): id of the user who sent the message
        receiver_id (str): id of the user who received the message
        message_info (MessageInfo): the information of the message

    Returns:
        void

    """
    # ! Upsert can and will fail when it's called multiple times due to a race condition:
    # https://www.prisma.io/docs/reference/api-reference/prisma-client-reference#unique-key-constraint-errors-on-upserts
    # https://github.com/prisma/prisma/issues/3242
    try:
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
    except UniqueViolationError:
        # attempt to update with the message when the upsert fails
        DirectMessage.prisma().update(
            where={"id": dm_id}, data={"messages": {"create": message_info}}
        )


@direct_message.route("/", methods=["POST"])
@error_decorator
@validate_decorator("json", direct_message_schema)
def dm_message(args):
    """Send a direct message to another user given their Id

    Args:
        otherId (str): The id of the other user
        message (str): The content of the message

    Returns:
        (json): dictionary containing:
            - id (str): id of the message
            - sentTime (str): time the message was sent

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the otherId does not correspond to an user
        ExpectedError: If the message format is invalid

    """
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
    dm_create_message(dm_id, session["user_id"], args["otherId"], message_info)
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

    else:
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
