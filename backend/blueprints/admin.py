from hashlib import sha256
import re
from uuid import uuid4
from flask import Blueprint, request, jsonify, session
from prisma.models import User, Tutor, Admin, Student
from helpers.views import user_view, admin_view, tutor_view, student_view
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

admin = Blueprint("admin", __name__)


@admin.route("/search", methods=["GET"])
@error_decorator
def user_search():
    args = request.args
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    admin = admin_view(id=session["user_id"])
    if not admin:
        raise ExpectedError("Insufficient permission to search for users", 403)

    if "accountType" in args:
        match args["accountType"]:
            case "student":
                users = Student.prisma().find_many(include={"userInfo": True})
            case "tutor":
                users = Tutor.prisma().find_many(include={"userInfo": True})
            case "admin":
                users = Admin.prisma().find_many(include={"userInfo": True})
    else:
        users = User.prisma().find_many()

    if len(args) == 0:
        return jsonify({"userIds": [user.id for user in users]}), 200
    elif "id" in args:
        user = user_view(id=args["id"])
        if user:
            return jsonify({"userIds": [user.id]})

    valid_users = []
    for user in users:
        valid = True
        if "name" in args:
            valid &= re.search(args["name"].lower().strip(), user.name.lower()) != None

        if "phoneNumber" in args and user.phoneNumber:
            valid &= args["phoneNumber"] == user.phoneNumber
        elif "phoneNumber" in args:
            continue

        if valid:
            valid_users.append(user.id)

    return jsonify({"userIds": valid_users}), 200


@admin.route("/create", methods=["POST"])
@error_decorator
def admin_create():
    args = request.get_json()
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    admin = admin_view(id=session["user_id"])
    if not admin:
        raise ExpectedError(
            "Insufficient permission to create a new admin account", 403
        )

    new_admin_id = str(uuid4())
    User.prisma().create(
        data={
            "id": new_admin_id,
            "name": args["name"],
            "email": args["email"],
            "hashedPassword": sha256(str(args["password"]).encode()).hexdigest(),
            "adminInfo": {"create": {"id": new_admin_id}},
        }
    )

    return jsonify({"userIds": new_admin_id}), 200
