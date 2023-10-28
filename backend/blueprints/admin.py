import re
from hashlib import sha256
from uuid import uuid4
from flask import Blueprint, jsonify, session
from prisma.models import User, Tutor, Admin, Student
from jsonschemas.user_search_schema import user_search_schema
from jsonschemas.admin_create_schema import admin_create_schema
from helpers.views import admin_view
from helpers.check_user_account_type import check_type
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

admin = Blueprint("admin", __name__)


@admin.route("/search", methods=["GET"])
@error_decorator
@validate_decorator("query_string", user_search_schema)
def user_search(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    admin = admin_view(id=session["user_id"])
    if not admin:
        raise ExpectedError("Insufficient permission to search for users", 403)

    if "id" in args:
        user = User.prisma().find_unique(
            where={"id": args["id"]},
            include={"adminInfo": True, "studentInfo": True, "tutorInfo": True},
        )
        if user:
            return jsonify(
                {"userInfos": [{"id": user.id, "accountType": check_type(user)}]}
            )

    if "accountType" in args:
        match args["accountType"]:
            case "student":
                res = Student.prisma().find_many(include={"userInfo": True})
                users = map(lambda user: (user.userInfo, "student"), res)
            case "tutor":
                res = Tutor.prisma().find_many(include={"userInfo": True})
                users = map(lambda user: (user.userInfo, "tutor"), res)
            case "admin":
                res = Admin.prisma().find_many(include={"userInfo": True})
                users = map(lambda user: (user.userInfo, "admin"), res)

    else:
        users = User.prisma().find_many(
            include={"adminInfo": True, "studentInfo": True, "tutorInfo": True}
        )
        users = map(lambda user: (user, check_type(user)), users)

    if len(args) == 0:
        return (
            jsonify(
                {
                    "userInfos": [
                        {"id": user.id, "accountType": account_type}
                        for user, account_type in users
                    ]
                }
            ),
            200,
        )

    valid_users = []
    for user, account_type in users:
        valid = True
        if "name" in args:
            valid &= re.search(args["name"].lower().strip(), user.name.lower()) != None

        if "phoneNumber" in args and user.phoneNumber:
            valid &= args["phoneNumber"] == user.phoneNumber
        elif "phoneNumber" in args:
            continue

        if "email" in args:
            valid &= args["email"] == user.email

        if valid:
            valid_users.append({"id": user.id, "accountType": account_type})

    return jsonify({"userInfos": valid_users}), 200


@admin.route("/create", methods=["POST"])
@error_decorator
@validate_decorator("json", admin_create_schema)
def admin_create(args):
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

    return jsonify({"id": new_admin_id}), 200
