from pytest_mock import MockerFixture
from flask.testing import FlaskClient
from prisma.models import User
from pytest_mock.plugin import MockType


def test_tutorial(
    setup_test: FlaskClient,
    fake_tutor: User,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    fake_login,
):
    client = setup_test

    fake_tutor.tutorialState = False

    resp = client.get("tutorial/")
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    resp = client.post("tutorial/complete")
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_tutor")

    resp = client.get("tutorial/")
    assert resp.json == {"completed": False}
    assert resp.status_code == 200

    update_user_mock = mocker.patch("tests.conftest.UserActions.update")
    resp = client.post("tutorial/complete")
    update_user_mock.assert_called()
    assert resp.status_code == 204

    find_unique_users_mock = mocker.patch("tests.conftest.UserActions.find_unique")
    find_unique_users_mock.return_value = fake_tutor
    fake_tutor.tutorialState = True

    resp = client.get("tutorial/")
    find_unique_users_mock.assert_called()
    assert resp.json == {"completed": True}
    assert resp.status_code == 200
