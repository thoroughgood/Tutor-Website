import pytest
from pytest_mock import MockerFixture
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.models import User, Document
from prisma.errors import RecordNotFoundError
from pytest_mock.plugin import MockType


@pytest.fixture
def fake_document(fake_tutor) -> Document:
    doc_content = "test document"

    doc = Document(
        id=str(uuid4()),
        tutor=fake_tutor.tutorInfo,
        tutorId=fake_tutor.id,
        document=doc_content,
    )

    fake_tutor.tutorInfo.documents = [doc]

    return doc


@pytest.fixture
def document_delete_mock(mocker: MockerFixture, fake_document):
    def mocked_document_delete(**kwargs):
        if (
            kwargs["where"]["id_tutorId"]["id"] != fake_document.id
            or kwargs["where"]["id_tutorId"]["tutorId"] != fake_document.tutorId
        ):
            raise RecordNotFoundError(
                mocker.Mock(), message="from mocked document_delete"
            )
        else:
            return fake_document

    return mocker.patch(
        "tests.conftest.DocumentActions.delete",
        new=mocker.Mock(side_effect=mocked_document_delete),
    )


# Test Upload user not logged in
def test_doc_upload_invalid(setup_test: FlaskClient, fake_login):
    client = setup_test

    resp = client.post("document/", json={"document": "test string input"})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_student")

    resp = client.post("document/", json={"document": "test string input"})
    assert resp.json == {"error": "User is not a tutor"}
    assert resp.status_code == 401

    resp = client.post("/logout")
    assert resp.status_code == 200

    fake_login("fake_tutor")

    resp = client.post("document/", json={})
    assert resp.json == {"error": "'document' was missing from field(s)"}
    assert resp.status_code == 400

    resp = client.post("document/", json={"document": None})
    assert resp.json == {"error": "field 'document' must be of type string"}
    assert resp.status_code == 400


# Valid Test of uploading and getting document
def test_upload_and_get_valid(
    setup_test: FlaskClient,
    fake_document: Document,
    mocker: MockerFixture,
    fake_login,
):
    client = setup_test

    doc = fake_document

    fake_login("fake_tutor")

    create_doc_mock = mocker.patch("tests.conftest.DocumentActions.create")
    create_doc_mock.return_value = doc

    resp = client.post("document/", json={"document": "test string input"})
    create_doc_mock()

    assert resp.status_code == 200
    assert resp.json["id"] == doc.id

    find_doc_mock = mocker.patch("tests.conftest.DocumentActions.find_unique")
    find_doc_mock.return_value = doc

    resp = client.get(f"document/{doc.id}")

    # find_doc_mock.assert_called(where={"id": doc.id}, include=mocker.ANY)

    find_doc_mock()
    assert resp.status_code == 200
    assert resp.json["document"] == doc.document


# test get document id doesnt exist
def test_get_document_invalid_id(setup_test: FlaskClient):
    client = setup_test

    resp = client.get("document/1")
    assert resp.status_code == 400
    assert resp.json == {"error": "document id does not exist"}


def test_document_delete_invalid(
    setup_test: FlaskClient, document_delete_mock, fake_document, fake_login
):
    client = setup_test

    # id is missing
    resp = client.delete("document/", json={})
    assert resp.json["error"] == "'id' was missing from field(s)"
    assert resp.status_code == 400

    # not logged in
    resp = client.delete("document/", json={"id": "notvalid"})
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401

    fake_login("fake_student")

    # invalid id
    resp = client.delete("document/", json={"id": "notvalid"})
    document_delete_mock.assert_called()
    assert (
        resp.json["error"]
        == "Document doesn't belong to user or no document exists with id"
    )
    assert resp.status_code == 400

    # valid id, but document does not belong to user
    resp = client.delete("document/", json={"id": fake_document.id})
    document_delete_mock.assert_called()
    assert (
        resp.json["error"]
        == "Document doesn't belong to user or no document exists with id"
    )
    assert resp.status_code == 400


def test_document_delete_args(
    setup_test: FlaskClient, document_delete_mock, fake_document, fake_login
):
    client = setup_test
    fake_login("fake_tutor")

    resp = client.delete("document/", json={"id": fake_document.id})
    document_delete_mock.assert_called()
    assert resp.json["success"] == True
    assert resp.status_code == 200
