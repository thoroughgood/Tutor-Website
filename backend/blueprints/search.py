from flask import Blueprint, request, jsonify
from prisma.models import Tutor, TutorAvailability
from datetime import datetime
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

search_tutor = Blueprint("search_tutor", __name__)


@search_tutor.route("/searchtutor", methods=["GET"])
@error_decorator
def search():
    args = request.get_json()

    return jsonify({"tutorIds": []}), 200
