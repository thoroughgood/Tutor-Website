from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from datetime import datetime, timedelta
from prisma.models import User, Appointment
from prisma.models import Student


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


@pytest.fixture
def initialise_admin() -> str:
    id = str(uuid4())
    admin = User.prisma().create(
        data={
            "id": id,
            "email": "validemail3@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name3",
            "adminInfo": {"create": {"id": id}},
        },
    )
    return admin.id


############################ GET PROFILE TESTS #################################


def test_get_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test

    # Missing id
    # resp = client.get("/student/")
    # assert resp.json == {"error": "id field was missing"}
    # assert resp.status_code == 405

    # Invalid id
    resp = client.get("/student/1")
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid id
    resp = client.get(f"/student/{initialise_student}")
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
    resp = client.put("/student/profile")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


# Non-admin modifying their profile
def test_modify_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test

    # No user logged in
    resp = client.put("/student/profile", json={})
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

    # Invalid name
    resp = client.put("/student/profile", json={"name": ""})
    assert resp.json == {"error": "name field is invalid"}
    assert resp.status_code == 400

    # Invalid email
    resp = client.put("/student/profile", json={"name": "Jerry", "email": ""})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Invalid email 2
    resp = client.put("/student/profile", json={"name": "Jerry", "email": "hi"})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Invalid email 3
    resp = client.put("/student/profile", json={"name": "Jerry", "email": "hello@hi"})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Valid modification
    resp = client.put(
        "/student/profile",
        json={
            "name": "Name1",
            "email": "hello@hi.com",
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
    resp = client.put("/student/profile", json={"id": initialise_student})
    assert resp.json == {"error": "id field should not be supplied by a non admin user"}
    assert resp.status_code == 403

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
    resp = client.put("/student/profile", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Invalid name
    resp = client.put("/student/profile", json={"id": initialise_student, "name": ""})
    assert resp.json == {"error": "name field is invalid"}
    assert resp.status_code == 400

    # Invalid email
    resp = client.put(
        "/student/profile", json={"id": initialise_student, "name": "Hi", "email": ""}
    )
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Invalid email 2
    resp = client.put(
        "/student/profile",
        json={"id": initialise_student, "name": "Hi", "email": "hi"},
    )
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Invalid email 3
    resp = client.put(
        "/student/profile",
        json={"id": initialise_student, "name": "Hi", "email": "hello@hi"},
    )
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.put(
        "/student/profile",
        json={
            "id": "invalid",
            "name": "Name1",
            "bio": "",
            "email": "hello@hi.com",
            "profilePicture": "",
            "location": "Australia",
            "phoneNumber": "",
        },
    )
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid modification
    resp = client.put(
        "/student/profile",
        json={
            "id": initialise_student,
            "name": "Name123",
            "bio": "hi",
            "email": "hello@hi.com",
            "profilePicture": "hi",
            "location": "Sydney",
            "phoneNumber": "000",
        },
    )
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    resp = client.get(f"/student/{initialise_student}")
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
    resp = client.delete("/student")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


# No user logged in
def test_delete_no_user(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/student", json={})
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
    resp = client.delete("/student", json={"id": "invalid"})
    assert resp.json == {"error": "id field should not be supplied by a non admin user"}
    assert resp.status_code == 403

    # Valid id
    resp = client.delete("/student", json={"id": initialise_student})
    assert resp.json == {"error": "id field should not be supplied by a non admin user"}
    assert resp.status_code == 403

    # No id
    resp = client.delete("/student", json={})
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
    resp = client.delete("/student", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.delete("/student", json={"id": "invalid"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Valid id
    resp = client.delete("/student", json={"id": initialise_student})
    assert resp.json == {"success": True}
    assert resp.status_code == 200


########################### STUDENT APPOINTMENT TESTS ##########################


@pytest.fixture
def generate_appointments(generate_dummy_tutor, initialise_student):
    id1 = str(uuid4())
    Appointment.prisma().create(
        data={
            "id": id1,
            "student": {"connect": {"id": initialise_student}},
            "tutor": {"connect": {"id": generate_dummy_tutor}},
            "startTime": datetime.now() + timedelta(days=1, hours=0),
            "endTime": datetime.now() + timedelta(days=1, hours=1),
            "tutorAccepted": False,
        }
    )

    id2 = str(uuid4())
    Appointment.prisma().create(
        data={
            "id": id2,
            "student": {"connect": {"id": initialise_student}},
            "tutor": {"connect": {"id": generate_dummy_tutor}},
            "startTime": datetime.now() + timedelta(days=1, hours=0),
            "endTime": datetime.now() + timedelta(days=1, hours=1),
            "tutorAccepted": True,
        }
    )

    id3 = str(uuid4())
    Appointment.prisma().create(
        data={
            "id": id3,
            "student": {"connect": {"id": initialise_student}},
            "tutor": {"connect": {"id": generate_dummy_tutor}},
            "startTime": datetime.now() - timedelta(days=1, hours=1),
            "endTime": datetime.now() - timedelta(days=1),
            "tutorAccepted": True,
        }
    )

    return (id1, id2, id3)


def test_student_appointment_not_login(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/student/appointments")
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401


def test_student_appointment_not_student_login(
    setup_test: FlaskClient, initialise_tutor
):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    resp = client.get("/student/appointments")
    assert resp.json["error"] == "Current user is not a student"
    assert resp.status_code == 400


def test_student_appointments(setup_test: FlaskClient, generate_appointments):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )

    resp = client.get("student/appointments")
    resp.status_code == 200

    id1, id2, id3 = generate_appointments
    assert "requested" in resp.json
    assert "accepted" in resp.json
    assert "completed" in resp.json

    assert id1 in resp.json["requested"]
    assert id2 in resp.json["accepted"]
    assert id3 in resp.json["completed"]
