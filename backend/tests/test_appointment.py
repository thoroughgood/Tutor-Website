from uuid import uuid4
import pytest
from datetime import datetime
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from flask.testing import FlaskClient
from prisma.models import Appointment
from prisma.errors import RecordNotFoundError


########################### APPOINTMENT ACCEPT TESTS ###########################


@pytest.fixture
def appointment_update_mock(mocker: MockerFixture, fake_tutor, fake_appointment):
    apt = fake_appointment

    def mocked_appointment_update(**kwargs):
        if (
            "tutorId" in kwargs["where"] and kwargs["where"]["tutorId"] == fake_tutor.id
        ) and ("id" in kwargs["where"] and kwargs["where"]["id"] == apt.id):
            apt.tutorAccepted = (
                kwargs["data"]["tutorAccepted"]
                if "data" in kwargs and "tutorAccepted" in kwargs["data"]
                else apt.tutorAccepted
            )
            return apt
        else:
            raise RecordNotFoundError(
                mocker.Mock(), message="from mocked appointment update"
            )

    return mocker.patch(
        "tests.conftest.AppointmentActions.update",
        new=mocker.Mock(side_effect=mocked_appointment_update),
    )


def test_appointment_accept_missing_args(setup_test: FlaskClient):
    client = setup_test

    # Id was missing from field
    resp = client.put("/appointment/accept", json={})
    assert resp.json["error"] == "'id' was missing from field(s)"
    assert resp.status_code == 400

    # accept was missing from field
    resp = client.put("/appointment/accept", json={"id": "id"})
    assert resp.json["error"] == "'accept' was missing from field(s)"
    assert resp.status_code == 400

    # Nothing missing, but not login
    resp = client.put("/appointment/accept", json={"id": "id", "accept": True})
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401


def test_appointment_accept_student_login(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    fake_student,
):
    client = setup_test

    # login as student
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

    resp = client.put("/appointment/accept", json={"id": "id", "accept": True})
    assert resp.json["error"] == "Must be a tutor to modify appointments"
    assert resp.status_code == 403


def test_appointment_accept_invalid_id(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    appointment_update_mock: MockType,
    fake_tutor,
):
    client = setup_test

    # login as tutor
    client.post(
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

    resp = client.put("/appointment/accept", json={"id": "id", "accept": True})
    appointment_update_mock.assert_called()

    assert (
        resp.json["error"]
        == "Appointment corresponding to id does not exist or, appointment does not involve tutor"
    )
    assert resp.status_code == 400


def test_appointment_accept(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    appointment_update_mock: MockType,
    fake_appointment,
    fake_tutor,
):
    client = setup_test
    apt = fake_appointment

    # login as tutor
    client.post(
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

    resp = client.put(
        "/appointment/accept", json={"id": fake_appointment.id, "accept": True}
    )
    appointment_update_mock.assert_called()

    assert resp.status_code == 200
    assert resp.json["id"] == apt.id
    assert resp.json["startTime"] == apt.startTime.isoformat()
    assert resp.json["endTime"] == apt.endTime.isoformat()
    assert resp.json["studentId"] == apt.studentId
    assert resp.json["tutorId"] == apt.tutorId
    assert resp.json["tutorAccepted"] == True
