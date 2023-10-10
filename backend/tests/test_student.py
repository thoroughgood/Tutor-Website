from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import Tutor, Student, User


@pytest.fixture
def initialise_student() -> str:
    id = str(uuid4())
    student = User.prisma().create(
        data={
            "id": id,
            "email": "validemail@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name1",
            "location": "Australia",
            "studentInfo": {"create": {"id": id}},
        },
    )
    return student.id


@pytest.fixture
def initialise_tutor() -> str:
    id = str(uuid4())
    tutor = User.prisma().create(
        data={
            "id": id,
            "email": "validemail2@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name2",
            "location": "Australia",
            "tutorInfo": {"create": {"id": id}},
        },
    )
    return tutor.id


############################ GET PROFILE TESTS #################################


# No query string
def test_get_no_query(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/student/profile/")
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400


def test_register_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test

    # Missing id
    resp = client.get("/student/profile/", query_string={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.get("/student/profile/", query_string={"id": "invalid"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid id
    resp = client.get("/student/profile/", query_string={"id": initialise_student})
    assert resp.status_code == 200
    assert resp.json["id"] == initialise_student
    assert resp.json["name"] == "Name1"
    assert resp.json["bio"] == ""
    assert resp.json["profilePicture"] == None
    assert resp.json["location"] == "Australia"
    assert resp.json["phoneNumber"] == None


########################### MODIFY PROFILE TESTS ###############################


def test_modify_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.put("/student/profile/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


def test_modify_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test

    # No user logged in
    resp = client.put("/student/profile/", json={})
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

    # Missing name
    resp = client.put("/student/profile/", json={})
    assert resp.json == {"error": "name field was missing"}
    assert resp.status_code == 400

    # Missing name 2
    resp = client.put("/student/profile/", json={"name": ""})
    assert resp.json == {"error": "name field was missing"}
    assert resp.status_code == 400

    # Missing bio
    resp = client.put("/student/profile/", json={"name": "Jerry"})
    assert resp.json == {"error": "bio field was missing"}
    assert resp.status_code == 400

    # Missing profilePicture
    resp = client.put("/student/profile/", json={"name": "Jerry", "bio": "bio"})
    assert resp.json == {"error": "profilePicture field was missing"}
    assert resp.status_code == 400

    # Missing location
    resp = client.put(
        "/student/profile/", json={"name": "Name1", "bio": "bio", "profilePicture": ""}
    )
    assert resp.json == {"error": "location field was missing"}
    assert resp.status_code == 400

    # Missing phoneNumber
    resp = client.put(
        "/student/profile/",
        json={"name": "Name1", "bio": "", "profilePicture": "", "location": ""},
    )
    assert resp.json == {"error": "phoneNumber field was missing"}
    assert resp.status_code == 400

    # Valid modification
    resp = client.put(
        "/student/profile/",
        json={
            "name": "Name1",
            "bio": "",
            "profilePicture": "",
            "location": "Australia",
            "phoneNumber": "",
        },
    )
    assert resp.json == {"success": True}
    assert resp.status_code == 200


########################### DELETE PROFILE TESTS ###############################


# No JSON
def test_delete_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/student/profile/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


# No user logged in
def test_delete_no_user(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/student/profile/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 400


def test_delete_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )

    # No id
    resp = client.delete("/student/profile/", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.delete("/student/profile/", json={"id": "invalid"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid id
    resp = client.delete("/student/profile/", json={"id": initialise_student})
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    assert Student.prisma().count() == 0
