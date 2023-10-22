from typing import List
import pytest
import json
from flask.testing import FlaskClient
from prisma.models import Subject, User, Tutor, Appointment, Rating, TutorAvailability
from datetime import datetime, timedelta, timezone
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType


@pytest.fixture
def generate_users(fake_user) -> List[User]:
    admin = fake_user("mail3@gmail.com", "12345678", "admin")
    admin.name = "admin"
    admin.phoneNumber = "04111222333"
    tutor = fake_user("mail2@gmail.com", "12345678", "tutor")
    tutor.name = "tutor"
    tutor.phoneNumber = "+6123456789"
    student = fake_user("mail@gmail.com", "12345678", "student")
    student.name = "student"
    student.phoneNumber = "+0202020202"

    return [admin, tutor, student]


def test_admin_search_not_login(setup_test: FlaskClient):
    client = setup_test

    resp = client.get("/admin/search")
    assert resp.status_code == 401
    assert resp.json["error"] == "No user is logged in"


def test_admin_search_student_login(
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

    resp = client.get("/admin/search")
    resp.status_code == 403
    resp.json["error"] == "Insufficient permission to search for users"


def test_admin_search_tutor_login(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
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

    resp = client.get("/admin/search")
    resp.status_code == 403
    resp.json["error"] == "Insufficient permission to search for users"


def test_admin_search_no_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    find_many_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
):
    client = setup_test

    # login as admin
    client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": fake_admin.email}, include=mocker.ANY
    )

    resp = client.get("/admin/search")
    resp.status_code == 200
    resp.json["userIds"] == []
