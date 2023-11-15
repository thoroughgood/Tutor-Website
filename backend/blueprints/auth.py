from flask import Blueprint, jsonify, session
from prisma.models import User
from uuid import uuid4
from hashlib import sha256
from jsonschemas import register_schema, reset_password_schema, login_schema
from helpers.views import user_view, admin_view, tutor_view, student_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
@error_decorator
@validate_decorator("json", register_schema)
def register(args):
    """Register a user as a tutor or student

    Args:
        accountType (str): The type of account to create
        name (str): The name of the user
        password (str): The password of the user
        email (str): The email of the user

    Returns:
        id (str): The id of the user

    Raises:
        ExpectedError: If the user already exists

    """
    user = user_view(email=args["email"])
    if user:
        raise ExpectedError("user already exists with this email", 400)

    new_user_id = str(uuid4())
    data = {
        "id": new_user_id,
        "name": args["name"],
        "email": args["email"],
        "hashedPassword": sha256(args["password"].encode()).hexdigest(),
    }

    match args["accountType"]:
        # id the of 'typed' tables are the same such it's possible
        # to still query on those tables with id
        case "student":
            data["studentInfo"] = {"create": {"id": new_user_id}}
            User.prisma().create(data=data)
        case "tutor":
            data["tutorInfo"] = {"create": {"id": new_user_id}}
            User.prisma().create(data=data)

    session["user_id"] = new_user_id

    return jsonify({"id": new_user_id}), 200


@auth.route("/login", methods=["POST"])
@error_decorator
@validate_decorator("json", login_schema)
def login(args):
    """Login a pre-existing user as a tutor or student

    Args:
        accountType (str): The type of account to create
        password (str): The password of the user
        email (str): The email of the user

    Returns:
        id (str): The id of the user

    Raises:
        ExpectedError: If the user credentials are invalid

    """
    match args["accountType"]:
        case "student":
            user = student_view(email=args["email"])
        case "tutor":
            user = tutor_view(email=args["email"])
        case "admin":
            user = admin_view(email=args["email"])
    if (
        user
        and user.hashed_password == sha256(str(args["password"]).encode()).hexdigest()
    ):
        session["user_id"] = user.id
        return jsonify({"id": user.id}), 200
    else:
        raise ExpectedError("Invalid login attempt", 401)


@auth.route("/logout", methods=["POST"])
@error_decorator
def logout():
    """Logout a currently active user

    Returns:
        success (bool): True

    """
    if "user_id" in session:
        session.pop("user_id")
    return jsonify({"success": True}), 200


@auth.route("/resetpassword", methods=["PUT"])
@error_decorator
@validate_decorator("json", reset_password_schema)
def resetpassword(args):
    """Changes a user’s password

    Args:
        id (str): The id of the user
        newPassword (str): The new password of the user

    Returns:
        success (bool): True

    Raises:
        ExpectedError: If the user is not logged in
        ExpectedError: If the user is not an admin
        ExpectedError: If the user does not exist
        ExpectedError: If the new password is the same as the old password

    """
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    admin = admin_view(id=session["user_id"])
    if not admin:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    user = user_view(id=args["id"])
    # ? we'll tentatively say an admin may reset their own password
    if not user:
        raise ExpectedError("Profile does not exist", 404)

    new_password = sha256(str(args["newPassword"]).encode()).hexdigest()
    if new_password == user.hashed_password:
        raise ExpectedError("New password cannot be the same as the old password", 400)

    User.prisma().update(where={"id": user.id}, data={"hashedPassword": new_password})

    return jsonify({"success": True}), 200
