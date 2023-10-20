import pytest
from pytest_mock import MockerFixture
from hashlib import sha256
from uuid import uuid4
from flask.testing import FlaskClient
from datetime import datetime, timedelta, timezone
from prisma.models import Appointment, User, Student, Tutor
from pytest_mock.plugin import MockType


############################## REQUEST TESTS ###################################


def test_request_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    fake_student: User,
    fake_tutor: User,
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

    find_unique_users_mock.assert_called_with(
        where={"email": fake_student.email}, include=mocker.ANY
    )

    # Missing start time
    resp = client.post("/appointment/request", json={})
    assert resp.json == {"error": "startTime field was missing"}
    assert resp.status_code == 400

    # Missing end time
    resp = client.post(
        "/appointment/request", json={"startTime": "2023-10-20T00:00:00.000+00:00"}
    )
    assert resp.json == {"error": "endTime field was missing"}
    assert resp.status_code == 400

    # Missing tutor id
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00.000+00:00",
            "endTime": "2024-10-20T01:00:00.000+00:00",
        },
    )
    assert resp.json == {"error": "Tutor id field was missing"}
    assert resp.status_code == 400

    # Invalid time (invalid start time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023",
            "endTime": "2024-10-20T01:00:00.000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "timeRange field(s) were malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid end time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00.000+00:00",
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
            "startTime": "2024-10-20T01:00:00.000+00:00",
            "endTime": "2024-10-20T00:00:00.000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "endTime cannot be less than startTime"}
    assert resp.status_code == 400

    # Invalid start time (st > now)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2022-10-20T01:00:00.000+00:00",
            "endTime": "2024-10-20T00:00:00.000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "startTime must be in the future"}
    assert resp.status_code == 400

    # Invalid tutor id
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-11-20T00:00:00.000+00:00",
            "endTime": "2024-11-20T01:00:00.000+00:00",
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
            "startTime": "2024-10-20T00:00:00.000+00:00",
            "endTime": "2024-10-20T01:00:00.000+00:00",
            "tutorId": fake_tutor.id,
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
            "startTime": "2024-10-20T00:00:00.000+00:00",
            "endTime": "2024-10-20T01:00:00.000+00:00",
            "tutorId": fake_tutor.id,
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
            "startTime": "2024-10-20T00:00:00.000+00:00",
            "endTime": "2024-10-21T00:00:00.000+00:00",
            "tutorId": fake_tutor.id,
        },
    )

    assert resp.status_code == 200
    assert resp.json["startTime"] == "2024-10-20T00:00:00.000+00:00"
    assert resp.json["endTime"] == "2024-10-21T00:00:00.000+00:00"
    assert resp.json["studentId"] == fake_student
    assert resp.json["tutorId"] == fake_tutor.id
    assert resp.json["tutorAccepted"] == False


############################### RATING TESTS ###################################


def test_rating_args(
    setup_test: FlaskClient,
    fake_student: User,
    fake_tutor: User,
    fake_admin: User,
):
    client = setup_test

    # No JSON Body
    resp = client.post("/appointment/rating")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # No logged in user
    resp = client.post("/appointment/rating", json={})
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
    resp = client.post("/appointment/rating", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # Missing end time
    resp = client.post("/appointment/rating", json={"id": "123"})
    assert resp.json == {"error": "rating field was missing"}
    assert resp.status_code == 400

    #
    resp = client.post(
        "/appointment/rating",
        json={
            "startTime": "2023-10-20T00:00:00.000+00:00",
            "endTime": "2023-10-20T01:00:00.000+00:00",
        },
    )
    assert resp.json == {"error": "Tutor id field was missing"}
    assert resp.status_code == 400

    # Invalid time (invalid start time format)
    resp = client.post(
        "/appointment/rating",
        json={
            "startTime": "2023",
            "endTime": "2023-10-20T01:00:00.000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "timeRange field(s) were malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid end time format)
    resp = client.post(
        "/appointment/rating",
        json={
            "startTime": "2023-10-20T00:00:00.000+00:00",
            "endTime": "2023",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "timeRange field(s) were malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid both time format)
    resp = client.post(
        "/appointment/rating",
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
        "/appointment/rating",
        json={
            "startTime": "2023-10-20T01:00:00.000+00:00",
            "endTime": "2023-10-20T00:00:00.000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "endTime cannot be less than startTime"}
    assert resp.status_code == 400

    # Invalid start time (st > now)
    resp = client.post(
        "/appointment/rating",
        json={
            "startTime": "2022-10-20T01:00:00.000+00:00",
            "endTime": "2023-10-20T00:00:00.000+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "startTime must be in the future"}
    assert resp.status_code == 400

    # Invalid tutor id
    resp = client.post(
        "/appointment/rating",
        json={
            "startTime": "2023-11-20T01:00:00.000+00:00",
            "endTime": "2023-11-20T00:00:00.000+00:00",
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
        "/appointment/rating",
        json={
            "startTime": "2023-11-20T01:00:00.000+00:00",
            "endTime": "2023-11-20T00:00:00.000+00:00",
            "tutorId": fake_tutor.id,
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
        "/appointment/rating",
        json={
            "startTime": "2023-11-20T01:00:00.000+00:00",
            "endTime": "2023-11-20T00:00:00.000+00:00",
            "tutorId": fake_tutor.id,
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
        "/appointment/rating",
        json={
            "startTime": "2023-11-20T00:00:00.000+00:00",
            "endTime": "2023-11-21T00:00:00.000+00:00",
            "tutorId": fake_tutor.id,
        },
    )

    assert Appointment.prisma().count() == 1
    assert resp.json["startTime"] == "2023-11-20T00:00:00.000+00:00"
    assert resp.json["endTime"] == "2023-11-21T00:00:00.000+00:00"
    assert resp.json["studentId"] == fake_student.id
    assert resp.json["tutorId"] == fake_tutor.id.id
    assert resp.json["tutorAccepted"] == False
    assert resp.status_code == 200
