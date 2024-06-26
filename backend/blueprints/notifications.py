from flask import Blueprint, jsonify, session
from prisma.models import User, Notification
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

notifications = Blueprint("notifications", __name__)


@notifications.route("/", methods=["GET"])
@error_decorator
def notifications_get():
    """Return all current waiting notifications of the session user.ns/[notificationId]

    Returns:
        notifications (list of str): the list of notifications

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the user does not exist

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    user = User.prisma().find_unique(
        where={"id": session["user_id"]},
        include={
            "notifications": True,
        },
    )

    if user is None:
        raise ExpectedError("User does not exist", 400)

    notifications_l = (
        list(map(lambda n: n.id, user.notifications))
        if user.notifications is not None
        else []
    )

    return jsonify({"notifications": notifications_l})


@notifications.route("/<notificationId>", methods=["GET"])
@error_decorator
def notifications_get_by_id(notificationId):
    """Returns the details of a notification by its id.

    Args:
        notificationId (str): id of the notification

    Returns:
        id (str): the id of the notification
        type (str): the type of the notification
        content (str): the content of the notification

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the id does not correspond to a notification
        ExpectedError: If the notification is not for this user

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    notification = Notification.prisma().find_unique(where={"id": notificationId})

    if notification is None:
        raise ExpectedError("id does not correspond to a notification", 404)

    if notification.userId != session["user_id"]:
        raise ExpectedError("notification is not for this user", 403)

    if notification.messageId is None:
        type = "appointment"
    elif notification.appointmentId is None:
        type = "message"

    Notification.prisma().delete(where={"id": notificationId})

    return jsonify(
        {"id": notification.id, "type": type, "content": notification.content}
    )
