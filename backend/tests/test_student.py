from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import Admin, Tutor, Student


@pytest.fixture
def initialise_student() -> str:
    student = Student.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name1",
            "bio": "",
            "location": "Australia",
        },
    )
    return student.id


@pytest.fixture
def initialise_tutor() -> str:
    tutor = Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail2@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name2",
            "bio": "",
            "location": "Australia",
        },
    )
    return tutor.id


@pytest.fixture
def initialise_admin() -> str:
    admin = Admin.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail3@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name3",
        },
    )
    return admin.id


############################ GET PROFILE TESTS #################################


# No query string
def test_get_no_query(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/student/profile/")
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400


def test_get_args(setup_test: FlaskClient, initialise_student: str):
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
    assert resp.json == {
        "id": initialise_student,
        "name": "Name1",
        "bio": "",
        "profilePicture": None,
        "location": "Australia",
        "phoneNumber": None,
    }


########################### MODIFY PROFILE TESTS ###############################


def test_modify_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.put("/student/profile/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


# Non-admin modifying their profile
def test_modify_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test

    # No user logged in
    resp = client.put("/student/profile/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

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


# Admin modifying a student profile
def test_admin_modify_args(
    setup_test: FlaskClient, initialise_admin: str, initialise_student: str
):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    client = setup_test
    resp = client.put("/student/profile/", json={"id": initialise_student})
    assert resp.json == {"error": "id should not be supplied from non admin user"}
    assert resp.status_code == 400

    resp = client.post("/logout")
    resp = client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    # Missing id
    resp = client.put("/student/profile/", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Missing name
    resp = client.put("/student/profile/", json={"id": initialise_student})
    assert resp.json == {"error": "name field was missing"}
    assert resp.status_code == 400

    # Missing name 2
    resp = client.put("/student/profile/", json={"id": initialise_student, "name": ""})
    assert resp.json == {"error": "name field was missing"}
    assert resp.status_code == 400

    # Missing bio
    resp = client.put(
        "/student/profile/", json={"id": initialise_student, "name": "Jerry"}
    )
    assert resp.json == {"error": "bio field was missing"}
    assert resp.status_code == 400

    # Missing profilePicture
    resp = client.put(
        "/student/profile/",
        json={"id": initialise_student, "name": "Name1", "bio": "bio"},
    )
    assert resp.json == {"error": "profilePicture field was missing"}
    assert resp.status_code == 400

    # Missing location
    resp = client.put(
        "/student/profile/",
        json={
            "id": initialise_student,
            "name": "Name1",
            "bio": "bio",
            "profilePicture": "",
        },
    )
    assert resp.json == {"error": "location field was missing"}
    assert resp.status_code == 400

    # Missing phoneNumber
    resp = client.put(
        "/student/profile/",
        json={
            "id": initialise_student,
            "name": "Name1",
            "bio": "",
            "profilePicture": "",
            "location": "",
        },
    )
    assert resp.json == {"error": "phoneNumber field was missing"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.put(
        "/student/profile/",
        json={
            "id": "invalid",
            "name": "Name1",
            "bio": "",
            "profilePicture": "",
            "location": "Australia",
            "phoneNumber": "",
        },
    )
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid modification
    resp = client.put(
        "/student/profile/",
        json={
            "id": initialise_student,
            "name": "Name123",
            "bio": "hi",
            "profilePicture": "hi",
            "location": "Sydney",
            "phoneNumber": "000",
        },
    )
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    resp = client.get("/student/profile/", query_string={"id": initialise_student})
    assert resp.json == {
        "id": initialise_student,
        "name": "Name123",
        "bio": "hi",
        "profilePicture": "hi",
        "location": "Sydney",
        "phoneNumber": "000",
    }


########################### DELETE PROFILE TESTS ###############################


# No JSON
def test_delete_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/student/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


# No user logged in
def test_delete_no_user(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/student/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401


def test_delete_student_login(setup_test: FlaskClient, initialise_student: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )

    # Invalid id
    resp = client.delete("/student/", json={"id": "invalid"})
    assert resp.json == {"error": "id should not be supplied from non admin user"}
    assert resp.status_code == 400

    # Valid id
    resp = client.delete("/student/", json={"id": initialise_student})
    assert resp.json == {"error": "id should not be supplied from non admin user"}
    assert resp.status_code == 400

    # No id
    resp = client.delete("/student/", json={})
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    assert Student.prisma().count() == 0


def test_delete_admin_login(
    setup_test: FlaskClient, initialise_admin: str, initialise_student: str
):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    # No id
    resp = client.delete("/student/", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.delete("/student/", json={"id": "invalid"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid id
    resp = client.delete("/student/", json={"id": initialise_student})
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    assert Student.prisma().count() == 0
