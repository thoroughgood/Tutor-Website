import pytest
from pytest_mock import MockerFixture
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.models import User, Document
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

# Test Upload user not logged in
def test_doc_upload_invalid(
        setup_test: FlaskClient, 
        fake_tutor: User,
        fake_student: User, 
        mocker: MockerFixture, 
        find_unique_users_mock: MockType
):
    client = setup_test

    resp = client.post("/document", json={"document": "test string input"})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 400

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    find_unique_users_mock.assert_called_with(
        where={"email": fake_student.email}, include=mocker.ANY
    )

    assert resp.status_code == 200

    resp = client.post("/document", json={"document": "test string input"})
    assert resp.json == {"error": "User is not a tutor"}
    assert resp.status_code == 401

    resp = client.post("/logout")
    assert resp.status_code == 200

    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    find_unique_users_mock.assert_called_with(
        where={"email": fake_tutor.email}, include=mocker.ANY
    )
    assert resp.status_code == 200

    resp = client.post("/document", json={})
    assert resp.json == {"error": "No document was provided"}
    assert resp.status_code == 400

    resp = client.post("/document", json={"document": None})
    assert resp.json == {"error": "No document was provided"}
    assert resp.status_code == 400

# Valid Test of uploading and getting document
def test_upload_and_get_valid(
        setup_test: FlaskClient, 
        fake_tutor: User,
        fake_document: Document,
        mocker: MockerFixture, 
        find_unique_users_mock: MockType
):
    client = setup_test

    doc = fake_document

    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    find_unique_users_mock.assert_called_with(
        where={"email": fake_tutor.email}, include=mocker.ANY
    )
    assert resp.status_code == 200

    create_doc_mock = mocker.patch("tests.conftest.DocumentActions.create")
    create_doc_mock.return_value = doc

    resp = client.post("/document", json={"document": "test string input"})
    create_doc_mock()

    print(doc.id)
    assert resp.status_code == 200
    assert resp.json["id"] == doc.id

    find_doc_mock = mocker.patch("tests.conftest.DocumentActions.find_unique")
    find_doc_mock.return_value = doc

    resp = client.get(f"/document/{doc.id}")

    #find_doc_mock.assert_called(where={"id": doc.id}, include=mocker.ANY)

    find_doc_mock()
    assert resp.status_code == 200
    assert resp.json["document"] == doc.document

# test get document id doesnt exist
def test_get_document_invalid_id(setup_test: FlaskClient):
    client = setup_test

    resp = client.get("document/1")
    assert resp.status_code == 400
    assert resp.json == {"error": "document id does not exist"}