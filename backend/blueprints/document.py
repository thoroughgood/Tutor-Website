from uuid import uuid4
from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Document
from jsonschemas.document_upload_schema import document_upload_schema
from helpers.views import tutor_view
from helpers.error_handlers import ExpectedError, error_decorator, validate_decorator

document = Blueprint("document", __name__)


@document.route("", methods=["POST"])
@error_decorator
@validate_decorator("json", document_upload_schema)
def upload_document(args):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 401)

    tutor = tutor_view(id=session["user_id"])

    if tutor is None:
        raise ExpectedError("User is not a tutor", 401)

    args = request.get_json()

    doc = Document.prisma().create(
        data={
            "id": str(uuid4()),
            "tutor": {"connect": {"id": tutor.id}},
            "document": args["document"],
        }
    )

    return jsonify({"id": doc.id})


@document.route("/<document_id>", methods=["GET"])
@error_decorator
def get_document(document_id):
    doc = Document.prisma().find_unique(where={"id": document_id})

    if doc is None:
        raise ExpectedError("document id does not exist", 400)

    return jsonify({"document": doc.document})
