from flask import Blueprint, jsonify, session
from prisma.models import User, Notification
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

notifications = Blueprint("notifications", __name__)

@notifications.route("notifications", methods=["GET"])
@error_decorator
def notifications_get():
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)
    
    user = User.prisma().find_unique(where={"id": session["user_id"]})

    notifications_l = list(map(lambda n: n.id, user.notifications))

    return jsonify({"notifications": notifications_l})

@notifications.route("notifications/<id>", methods=["GET"])
@error_decorator
def notifications_get_by_id(notification_id):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    notification = Notification.prisma().find_unique(
        where={"id": notification_id}
    )

    if notification is None:
        raise ExpectedError("id does not correspond to a notification")

    if notification.userId != session["user_id"]:
        raise ExpectedError("notification is not for this user")

    if notification.messageId is None:
        type = "appointment"
    elif notification.appointmentId is None:
        type = "message"

    Notification.prisma().delete(
        where={"id": notification_id}
    )

    return jsonify({
        "id": notification.id,
        "type": type,
        "content": notification.content
    })