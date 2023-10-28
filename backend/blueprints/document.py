from uuid import uuid4
from flask import Blueprint, request , jsonify, session
from prisma.models import Tutor, Document
from helpers.views import tutor_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

document = Blueprint("document", __name__)

@document.route("document", methods=["POST"])
@error_decorator
def upload_document():

    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)
    
    tutor = tutor_view(id=session["user_id"])

    if tutor is None:
        raise ExpectedError("User is not a tutor", 401)
    
    args = request.get_json()

    if "document" not in args or args["document"] is None:
        raise ExpectedError("No document was provided", 400)
    
    doc = Document.prisma().create(
        data={
            "id": str(uuid4()),
            "tutor": {"connect": {"id": tutor.id}},
            "document": args["document"]
        }
    )
    
    Tutor.prisma().update(
        where={"id": tutor.id},
        data={"documents": {"connect": {"id": doc.id}}},
    )

    return jsonify({"id": doc.id})

@document.route("document/<document_id>", methods=["GET"])
@error_decorator
def get_document(document_id):
    doc = Document.prisma().find_unique(
        where={"id": document_id}
    )

    if doc is None:
        raise ExpectedError("document id does not exist", 400)
    
    return jsonify({"document": doc.document})