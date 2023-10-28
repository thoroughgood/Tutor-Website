from flask import Blueprint, jsonify, session
from prisma.models import User
from helpers.error_handlers import error_decorator
from helpers.check_user_account_type import check_type
from helpers.views import student_view, tutor_view, admin_view

utils = Blueprint("utils", __name__)


@utils.route("/getuserid", methods=["GET"])
@error_decorator
def get_id():
    if "user_id" in session:
        user = User.prisma().find_unique(
            where={"id": session["id"]},
            include={"adminInfo": True, "studentInfo": True, "tutorInfo": True},
        )
        return jsonify({"id": session["user_id"], "accountType": check_type(user)}), 200
    else:
        return jsonify({}), 401
