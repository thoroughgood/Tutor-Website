from flask import Blueprint, jsonify, session
from helpers.error_handlers import error_decorator
from prisma.models import Tutor, Student, Admin

utils = Blueprint("utils", __name__)


@utils.route("/getuserid", methods=["GET"])
@error_decorator
def get_id():
    if "user_id" in session:
        student = Student.prisma().find_unique(where={"id": session["user_id"]})
        tutor = Tutor.prisma().find_unique(where={"id": session["user_id"]})
        accountType = None
        if student:
            accountType = "student"
        elif tutor:
            accountType = "tutor"
        else:
            return jsonify({}), 401
        return jsonify({"id": session["user_id"], "accountType": accountType}), 200
    else:
        return jsonify({}), 401
