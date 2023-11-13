from pytest_mock import MockerFixture
from flask.testing import FlaskClient
from prisma.models import Appointment, User

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

    resp = client.get("/appointments/", query_string={})
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

    resp = client.get("/appointments/", query_string={})
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

    resp = client.get("/appointments/", query_string={})
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

    # sortBy does not equal messageSent
    resp = client.get("/appointments/", query_string={"sortBy": "notmessageSent"})
    assert resp.status_code == 400
    assert (
        resp.json["error"] == "When specified, 'sortBy' must be equal to 'messageSent'"
    )

    # Invalid appointment id
    resp = client.get("/appointments/", query_string={"sortBy": "messageSent"})
    assert resp.status_code == 200
    assert resp.json == {
        "appointments": [fake_appointment_msg.id, fake_appointment_msg2.id]
    }


def test_appointments_no_apt(setup_test: FlaskClient, fake_login, fake_student):
    client = setup_test

    resp = client.get("/appointments/", query_string={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_student")

    resp = client.get("/appointments/", query_string={})
    assert resp.status_code == 200
    assert resp.json == {"appointments": []}
