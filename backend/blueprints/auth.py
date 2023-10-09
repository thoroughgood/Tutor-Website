from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Student, Admin
from re import fullmatch
from uuid import uuid4
from hashlib import sha256
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
@error_decorator
def register():
    args = request.get_json()

    if "name" not in args or len(str(args["name"]).lower().strip()) == 0:
        raise ExpectedError("name field was missing", 400)

    if "email" not in args or not fullmatch(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
        str(args["email"]).lower().strip(),
    ):
        raise ExpectedError("email field is invalid", 400)

    if "password" not in args or len(str(args["password"]).lower().strip()) < 8:
        raise ExpectedError("password field must be at least 8 characters long", 400)

    new_user_id = None
    if "accountType" in args:
        student = Student.prisma().find_unique(where={"email": args["email"]})
        tutor = Tutor.prisma().find_unique(where={"email": args["email"]})
        if student or tutor:
            raise ExpectedError("user already exists with this email", 400)

        match str(args["accountType"]).lower().strip():
            case "student":
                new_user_id = str(uuid4())
                Student.prisma().create(
                    data={
                        "id": new_user_id,
                        "name": args["name"],
                        "email": args["email"],
                        "hashedPassword": sha256(
                            str(args["password"]).encode()
                        ).hexdigest(),
                        "bio": "",
                        "appointments": {},
                    }
                )
            case "tutor":
                new_user_id = str(uuid4())
                Tutor.prisma().create(
                    data={
                        "id": new_user_id,
                        "name": args["name"],
                        "email": args["email"],
                        "hashedPassword": sha256(
                            str(args["password"]).encode()
                        ).hexdigest(),
                        "bio": "",
                        "rating": {},
                        "courseOfferings": {},
                        "timesAvailable": {},
                        "appointments": {},
                    }
                )
            case _:
                raise ExpectedError("accountType must be 'student' or 'tutor'", 400)
    else:
        raise ExpectedError("accountType field missing", 400)

    session["user_id"] = new_user_id

    return jsonify({"id": new_user_id}), 200


@auth.route("/login", methods=["POST"])
@error_decorator
def login():
    args = request.get_json()

    if "user_id" in session:
        raise ExpectedError("A user is already logged in", 400)

    if "email" not in args or not fullmatch(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
        str(args["email"]).lower().strip(),
    ):
        raise ExpectedError("email field is invalid", 400)

    if "password" not in args or len(str(args["password"]).lower().strip()) < 8:
        raise ExpectedError("password field must be at least 8 characters long", 400)

    if "accountType" in args and (
        args["accountType"] == "student" or args["accountType"] == "tutor"
    ):
        student = Student.prisma().find_unique(where={"email": args["email"]})
        tutor = Tutor.prisma().find_unique(where={"email": args["email"]})
        if (
            student
            and student.hashedPassword
            == sha256(str(args["password"]).encode()).hexdigest()
        ):
            session["user_id"] = student.id
            return jsonify({"id": student.id}), 200
        elif (
            tutor
            and tutor.hashedPassword
            == sha256(str(args["password"]).encode()).hexdigest()
        ):
            session["user_id"] = tutor.id
            return jsonify({"id": tutor.id}), 200
        else:
            raise ExpectedError("Invalid login attempt", 401)
    else:
        raise ExpectedError("accountType must be 'student' or 'tutor'", 400)


@auth.route("/logout", methods=["POST"])
@error_decorator
def logout():
    if "user_id" in session:
        session.pop("user_id")
    return jsonify({"success": True}), 200


@auth.route("/resetpassword", methods=["PUT"])
@error_decorator
def resetpassword():
    args = request.get_json()

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)

    if "id" not in args:
        raise ExpectedError("id field is missing", 400)

    student = Student.prisma().find_unique(where={"id": args["id"]})
    tutor = Tutor.prisma().find_unique(where={"id": args["id"]})
    if not student and not tutor:
        raise ExpectedError("Profile does not exist", 404)

    admin = Admin.prisma().find_first(where={"id": session["user_id"]})
    if not admin and session["user_id"] != args["id"]:
        raise ExpectedError("Insufficient permission to modify this profile", 403)

    if "newPassword" not in args or len(str(args["newPassword"]).lower().strip()) < 8:
        raise ExpectedError("password field must be at least 8 characters long", 400)

    newPassword = sha256(str(args["newPassword"]).encode()).hexdigest()
    if student:
        if student.hashedPassword == newPassword:
            raise ExpectedError(
                "New password cannot be the same as the old password", 400
            )
        Student.prisma().update(
            where={"id": student.id}, data={"hashedPassword": newPassword}
        )
    if tutor:
        if tutor.hashedPassword == newPassword:
            raise ExpectedError(
                "New password cannot be the same as the old password", 400
            )
        Tutor.prisma().update(
            where={"id": tutor.id}, data={"hashedPassword": newPassword}
        )

    return jsonify({"success": True}), 200
