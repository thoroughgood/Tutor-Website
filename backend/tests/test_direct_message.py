from datetime import datetime
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.models import User, Message, Appointment
import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType


@pytest.fixture
def direct_message_find_many_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.DirectMessageActions.find_many")


def test_dm_all_invalid(setup_test: FlaskClient):
    client = setup_test

    # not logged in
    resp = client.get("directmessage/all")
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401


def test_dm_all_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    fake_login,
    find_unique_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_appointment,
    fake_dm,
):
    client = setup_test
    fake_login("fake_student")
