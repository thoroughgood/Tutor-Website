import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from flask.testing import FlaskClient
from prisma.models import Appointment, User, Rating
from prisma.errors import RecordNotFoundError

############################## APPOINTMENTS TESTS ##################################


def test_appointments_no_sortby(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock,
    fake_student_apt: User,
    fake_appointment_msg: Appointment,
    fake_appointment_msg2: Appointment,
):
    client = setup_test

    # No JSON Body
    resp = client.get("/appointments/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    resp = client.get("/appointments/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    client.post(
        "/login",
        json={
            "email": fake_student_apt.email,
            "password": "12345678",
            "accountType": "student",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": fake_student_apt.email}, include=mocker.ANY
    )

    resp = client.get("/appointments/", json={})
    assert resp.status_code == 200
    assert resp.json == {
        "appointments": [fake_appointment_msg.id, fake_appointment_msg2.id]
    }


def test_appointments_sortby(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock,
    fake_student_apt: User,
    fake_appointment_msg: Appointment,
    fake_appointment_msg2: Appointment,
):
    client = setup_test

    # No JSON Body
    resp = client.get("/appointments/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    resp = client.get("/appointments/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    client.post(
        "/login",
        json={
            "email": fake_student_apt.email,
            "password": "12345678",
            "accountType": "student",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": fake_student_apt.email}, include=mocker.ANY
    )

    # Invalid appointment id
    resp = client.get("/appointments/", json={"sortBy": "messageSent"})
    assert resp.status_code == 200
    assert resp.json == {
        "appointments": [fake_appointment_msg.id, fake_appointment_msg2.id]
    }


def test_appointments_no_apt(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock,
    fake_student: User,
):
    client = setup_test

    # No JSON Body
    resp = client.get("/appointments/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    resp = client.get("/appointments/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    client.post(
        "/login",
        json={
            "email": fake_student.email,
            "password": "12345678",
            "accountType": "student",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": fake_student.email}, include=mocker.ANY
    )

    resp = client.get("/appointments/", json={})
    assert resp.status_code == 200
    assert resp.json == {"appointments": []}
