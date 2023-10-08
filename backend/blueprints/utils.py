from flask import Blueprint, jsonify, session
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

utils = Blueprint("utils", __name__)


@utils.route("/getuserid", methods=["GET"])
@error_decorator
def get_id():
    if "user_id" in session:
        return jsonify({"id": session["user_id"]}), 200
    else:
        return jsonify({}), 200
