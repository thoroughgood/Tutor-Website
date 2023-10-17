from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import User
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


############################## REQUEST TESTS ###################################


def test_request_args(
    setup_test: FlaskClient,
    initialise_student: str,
    initialise_tutor: str,
    initialise_admin: str,
):
    client = setup_test

    # No JSON Body
    resp = client.post("/appointment/request")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # No logged in user
    resp = client.post("/appointment/request", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )

    # Missing start time
    resp = client.post("/appointment/request", json={})
    assert resp.json == {"error": "startTime field was missing"}
    assert resp.status_code == 400

    # Missing end time
    resp = client.post(
        "/appointment/request", json={"startTime": "2023-10-20T00:00:00.00000+00:00"}
    )
    assert resp.json == {"error": "endTime field was missing"}
    assert resp.status_code == 400

    #
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-10-20T00:00:00.00000+00:00",
            "endTime": "2023-10-20T01:00:00.00000+00:00",
        },
    )
    assert resp.json == {"error": "Tutor id field was missing"}
    assert resp.status_code == 400

    # Invalid time (invalid start time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023",
            "endTime": "2023-10-20T01:00:00.00000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "timeRange field(s) were malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid end time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-10-20T00:00:00.00000+00:00",
            "endTime": "2023",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "timeRange field(s) were malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid both time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023",
            "endTime": "2024",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "timeRange field(s) were malformed"}
    assert resp.status_code == 400

    # Invalid end time (et < st)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-10-20T01:00:00.00000+00:00",
            "endTime": "2023-10-20T00:00:00.00000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "endTime cannot be less than startTime"}
    assert resp.status_code == 400

    # Invalid start time (st > now)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2022-10-20T01:00:00.00000+00:00",
            "endTime": "2023-10-20T00:00:00.00000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "startTime must be in the future"}
    assert resp.status_code == 400

    # Invalid tutor id
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-11-20T01:00:00.00000+00:00",
            "endTime": "2023-11-20T00:00:00.00000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "Tutor profile does not exist"}
    assert resp.status_code == 400

    client.post("/logout")
    client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    # Invalid user (tutor is logged in)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-11-20T01:00:00.00000+00:00",
            "endTime": "2023-11-20T00:00:00.00000+00:00",
            "tutorId": initialise_tutor,
        },
    )
    assert resp.json == {"error": "Profile is not a student"}
    assert resp.status_code == 400

    client.post("/logout")
    client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    # Invalid user (admin is logged in)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-11-20T01:00:00.00000+00:00",
            "endTime": "2023-11-20T00:00:00.00000+00:00",
            "tutorId": initialise_tutor,
        },
    )
    assert resp.json == {"error": "Profile is not a student"}
    assert resp.status_code == 400

    client.post("/logout")
    client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )

    # Valid Input
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023-11-20T00:00:00.00000+00:00",
            "endTime": "2023-11-21T00:00:00.00000+00:00",
            "tutorId": initialise_tutor,
        },
    )

    assert Appointment.prisma().count() == 1
    assert resp.json["startTime"] == "2023-11-20T00:00:00.00000+00:00"
    assert resp.json["endTime"] == "2023-11-21T00:00:00.00000+00:00"
    assert resp.json["studentId"] == initialise_student
    assert resp.json["tutorId"] == initialise_tutor
    assert resp.json["tutorAccepted"] == False
    assert resp.status_code == 200
