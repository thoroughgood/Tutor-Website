import pytest
from pytest_mock import MockerFixture
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.models import User, Notification
from pytest_mock.plugin import MockType

@pytest.fixture
def find_unique_notification_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.NotificationActions.find_unique")

@pytest.fixture
def fake_notification(fake_tutor, fake_student) -> Notification:
    notification = Notification(
        id=str(uuid4()),
        forUser=fake_student,
        userId=fake_student.id,
        content="fake notification",
    )

def test_get_notification_user_not_logged_in(
        setup_test: FlaskClient,
        fake_student: User,
        mocker: MockerFixture,
        find_unique_users_mock: MockType,
        find_unique_notification_mock: MockType,
        fake_user: User,
):
    client = setup_test

    resp = client.get("/notifications")
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    resp = client.get("/notifications/1")
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
    find_unique_users_mock.assert_called_with(
        where={"email": fake_student.email}, include=mocker.ANY
    )
    assert resp.status_code == 200
    
    resp = client.get("/notifications/123")
    assert resp.json == {"error": "id does not correspond to a notification"}
    assert resp.status_code == 404

    # Generate another student
    fake_student2 = fake_user("validemailtest@mail.com", "12345678", "student")
    # Generate a fake notification that belongs to t
    notification_id = str(uuid4())
    notification = Notification(
        id = notification_id,
        forUser = fake_student2,
        userId = fake_student2.id,
        content = "fake notification"
    )

    find_unique_notification_mock.return_value = notification

    resp = client.get(f"/notifications/{notification_id}")
    find_unique_notification_mock.assert_called()
    assert resp.json == {"error": "notification is not for this user"}

def test_get_notification_invalid_id(
        setup_test: FlaskClient,
        fake_student: User,
        mocker: MockerFixture,
        find_unique_users_mock: MockType,
        find_unique_notification_mock: MockType,
):
    client = FlaskClient

    resp = client.post(
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
    assert resp.status_code == 200

    resp = client.get("/notifications/123")
    assert resp.json == {"error": "id does not correspond to a notification"}
    assert resp.status_code == 404




# valid tests
# structure
    # call get notifications, ensure empty
    # call route that raises notification
    # call get notifications, ensure it has the notification id
    # call get notifications[id], ensure notification is correct

# appointent accept
# appointment modify
# appointment delete

def test_get_notification_valid(
        setup_test: FlaskClient,
        fake_student: User,
        mocker: MockerFixture,
        find_unique_users_mock: MockType,
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
    find_unique_users_mock.assert_called_with(
        where={"email": fake_student.email}, include=mocker.ANY
    )
    assert resp.status_code == 200

    # call get notifications, check empty

    resp = client.post("/notifications")


    # call appointment accept route

    # call get notifications, check if notification for appointment accept exists
