from uuid import uuid4
from flask import Blueprint, request, jsonify, session
from prisma.models import Tutor, Subject, User
from helpers.views import tutor_view
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

document = Blueprint("document", __name__)

@document.route("document", methods=["POST"])
@error_decorator
def upload_document(document):
    if "user_id" not in session:
        raise ExpectedError("No user is logged in", 400)
    
    tutor = tutor_view(id=session["user_id"])

    if tutor is None:
        raise ExpectedError("User is not a tutor", 401)
    
    if not isinstance(document, bytes):
        raise ExpectedError("passed data is not binary", 415)
    
    document_id = str(uuid4())
    
    Tutor.prisma().update(
        where={"id": tutor.id},
        data={"documents": {
            "connect": {
                "id": document_id,
                "tutorId": tutor.id,
                "document": str(document, 'UTF-8') 
            }
        }}
    )

    return jsonify({"id": document_id})
