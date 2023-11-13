from flask import Blueprint, jsonify, session
from prisma.models import User
from helpers.error_handlers import error_decorator
from helpers.check_user_account_type import check_type

utils = Blueprint("utils", __name__)


@utils.route("/getuserid", methods=["GET"])
@error_decorator
def get_id():
    """Gets the id of the user logged in.

    Returns:
        id (str): The id of the user
        accountType (str): The account type of the user

    """
    if "user_id" in session:
        user = User.prisma().find_unique(
            where={"id": session["user_id"]},
            include={"adminInfo": True, "studentInfo": True, "tutorInfo": True},
        )
        if user is None:
            return jsonify({}), 404
        return jsonify({"id": session["user_id"], "accountType": check_type(user)}), 200
    else:
        return jsonify({}), 404


@utils.route("/usertype/<user_id>", methods=["GET"])
@error_decorator
def get_type(user_id):
    """Gets the account type of the user logged in.

    Returns:
        accountType (str): The account type of the user

    """
    user = User.prisma().find_unique(
        where={"id": user_id},
        include={"adminInfo": True, "studentInfo": True, "tutorInfo": True},
    )
    if user is None:
        return jsonify({}), 404
    return jsonify({"accountType": check_type(user)}), 200
