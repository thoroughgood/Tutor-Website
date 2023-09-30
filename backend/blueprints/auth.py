from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Student, Admin
from re import fullmatch
from uuid import uuid4
from hashlib import sha256

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
def register():
    args = request.get_json(silent=True)
    if not args:
        return (
            jsonify({"error": "content-type was not json or data was malformed"}),
            415,
        )

    if not "name" in args or len(str(args["name"]).lower().strip()) == 0:
        return jsonify({"error": "name field missing"}), 400

    if not "email" in args or not fullmatch(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
        str(args["email"]).lower().strip(),
    ):
        return jsonify({"error": "email field is invalid"}), 400

    if not "password" in args or len(str(args["password"]).lower().strip()) < 8:
        return (
            jsonify({"error": "password field must be at least 8 characters long"}),
            400,
        )

    new_user_id = None
    if "accountType" in args:
        student = Student.prisma().find_first(where={"email": args["email"]})
        tutor = Tutor.prisma().find_first(where={"email": args["email"]})
        if student or tutor:
            return jsonify({"error": "user already exists with this email"}), 400

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
                return (
                    jsonify({"error": "accountType must be 'student' or 'tutor'"}),
                    400,
                )
    else:
        return jsonify({"error": "accountType field missing"}), 400

    session["user_id"] = new_user_id

    return jsonify({"id": new_user_id}), 200
