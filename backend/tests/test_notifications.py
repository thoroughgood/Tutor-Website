import pytest
from pytest_mock import MockerFixture
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.models import User, Notification, Appointment
from datetime import datetime, timedelta
from pytest_mock.plugin import MockType


@pytest.fixture
def find_unique_notification_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.NotificationActions.find_unique")


@pytest.fixture
def update_appt_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.AppointmentActions.update")


@pytest.fixture
def create_notification_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.NotificationActions.create")


@pytest.fixture
def find_unique_appt_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.AppointmentActions.find_unique")


@pytest.fixture
def fake_student_notification(fake_student) -> Notification:
    notification = Notification(
        id=str(uuid4()),
        forUser=fake_student,
        userId=fake_student.id,
        content="fake notification",
    )

    return notification


@pytest.fixture
def fake_tutor_notification(fake_tutor) -> Notification:
    notification = Notification(
        id=str(uuid4()),
        forUser=fake_tutor,
        userId=fake_tutor.id,
        content="fake notification",
    )

    return notification


def test_get_notification_invalid(
    setup_test: FlaskClient,
    find_unique_notification_mock: MockType,
    fake_user: User,
    fake_login,
):
    client = setup_test

    resp = client.get("notifications/")
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    resp = client.get("notifications/1")
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_student")

    find_unique_notification_mock.return_value = None

    resp = client.get("notifications/123")
    find_unique_notification_mock.assert_called()
    find_unique_notification_mock.rest_mock()

    assert resp.json == {"error": "id does not correspond to a notification"}
    assert resp.status_code == 404

    # Generate another student
    fake_student2 = fake_user("validemailtest@mail.com", "12345678", "student")
    # Generate a fake notification that belongs to the other student
    notification_id = str(uuid4())
    notification = Notification(
        id=notification_id,
        forUser=fake_student2,
        userId=fake_student2.id,
        content="fake notification",
    )

    find_unique_notification_mock.return_value = notification

    resp = client.get(f"notifications/{notification_id}")
    find_unique_notification_mock.assert_called()
    find_unique_notification_mock.mock_reset()

    assert resp.json == {"error": "notification is not for this user"}


# valid tests
# structure
# call get notifications, ensure empty
# call route that raises notification
# call get notifications, ensure it has the notification id
# call get notifications[id], ensure notification is correct

# appointent accept
# appointment modify
# appointment delete


def test_get_notification_tutor_valid(
    setup_test: FlaskClient,
    fake_student: User,
    fake_tutor: User,
    fake_appointment: Appointment,
    fake_tutor_notification: Notification,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    find_unique_notification_mock: MockType,
    fake_login,
):
    client = setup_test

    fake_login("fake_student")

    # call get notifications, check empty

    resp = client.get("notifications/")
    assert resp.json == {"notifications": []}
    assert resp.status_code == 200

    # call appointment request route
    appointment_create_mock = mocker.patch("tests.conftest.AppointmentActions.create")
    appointment_create_mock.return_value = fake_appointment
    startTime = datetime.now() + timedelta(days=1)
    endTime = datetime.now() + timedelta(days=2)

    fake_appointment.startTime = startTime
    fake_appointment.endTime = endTime
    fake_appointment.notification = fake_tutor_notification

    fake_tutor_notification.content = (
        f"{fake_student.name} has requested an appointment with you"
    )
    fake_tutor_notification.appointment = fake_appointment
    fake_tutor_notification.appointmentId = fake_appointment.id

    resp = client.post(
        "/appointment/request",
        json={
            "startTime": startTime.isoformat(),
            "endTime": endTime.isoformat(),
            "tutorId": fake_tutor.id,
        },
    )

    appointment_create_mock.assert_called()

    assert resp.status_code == 200

    # logout of student
    resp = client.post("/logout")
    assert resp.json == {"success": True}

    # login as tutor
    fake_login("fake_tutor")

    # call get notifications
    #   check if tutor has notification

    find_unique_users_mock.return_value = fake_tutor
    fake_tutor.notifications = [fake_tutor_notification]

    resp = client.get("notifications/")
    find_unique_users_mock.assert_called_with(
        where={"id": fake_tutor.id}, include={"notifications": True}
    )
    assert resp.status_code == 200
    assert resp.json == {"notifications": [fake_tutor_notification.id]}

    # call get notification by id,
    #   check if return is right

    find_unique_notification_mock.return_value = fake_tutor_notification
    notification_delete_mock = mocker.patch("tests.conftest.NotificationActions.delete")

    resp = client.get(f"notifications/{fake_tutor_notification.id}")
    find_unique_notification_mock.assert_called()

    notification_delete_mock.assert_called_with(
        where={"id": fake_tutor_notification.id}
    )

    assert resp.status_code == 200
    assert resp.json["id"] == fake_tutor_notification.id
    assert resp.json["type"] == "appointment"
    assert resp.json["content"] == fake_tutor_notification.content


def test_notification_appt_accept(
    setup_test: FlaskClient,
    fake_tutor: User,
    fake_appointment: Appointment,
    find_unique_users_mock: MockType,
    update_appt_mock: MockType,
    create_notification_mock: MockType,
    fake_login,
):
    #  setup tutor with an unaccepted appointment
    client = setup_test

    fake_tutor.tutorInfo.appointments = [fake_appointment]

    fake_login("fake_tutor")

    update_appt_mock.return_value = fake_appointment
    fake_appointment.tutorAccepted = True

    client.put("/appointment/accept", json={"id": fake_appointment.id, "accept": True})
    find_unique_users_mock.assert_called()
    update_appt_mock.assert_called()
    create_notification_mock.assert_called()


def test_notification_appt_delete(
    setup_test: FlaskClient,
    fake_tutor: User,
    fake_appointment: Appointment,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    create_notification_mock: MockType,
    find_unique_appt_mock: MockType,
    fake_login,
):
    #  setup tutor with an accepted appointment
    client = setup_test
    fake_appointment.tutorAccepted = True
    fake_tutor.tutorInfo.appointments = [fake_appointment]

    # tutor logins and deletes appointment
    fake_login("fake_tutor")

    find_unique_appt_mock.return_value = fake_appointment
    delete_notification_mock = mocker.patch(
        "tests.conftest.NotificationActions.delete_many"
    )

    client.delete("/appointment/", json={"id": fake_appointment.id})
    find_unique_users_mock.assert_called()
    find_unique_appt_mock.assert_called()
    create_notification_mock.assert_called()
    delete_notification_mock.assert_called_with(
        where={"appointmentId": fake_appointment.id}
    )


def test_notification_apt_modify(
    setup_test: FlaskClient,
    fake_tutor: User,
    fake_appointment: Appointment,
    find_unique_users_mock: MockType,
    create_notification_mock: MockType,
    find_unique_appt_mock: MockType,
    update_appt_mock: MockType,
    fake_login,
):
    #  setup tutor with an accepted appointment
    client = setup_test
    fake_appointment.tutorAccepted = True
    fake_tutor.tutorInfo.appointments = [fake_appointment]

    # tutor logins and modifies appointment
    fake_login("fake_tutor")

    startTime = datetime.now() + timedelta(days=1)
    endTime = datetime.now() + timedelta(days=2)

    find_unique_appt_mock.return_value = fake_appointment
    fake_appointment.startTime = startTime
    fake_appointment.endTime = endTime

    client.put(
        "/appointment/",
        json={
            "id": fake_appointment.id,
            "startTime": startTime.isoformat(),
            "endTime": endTime.isoformat(),
        },
    )

    find_unique_users_mock.assert_called()
    find_unique_appt_mock.assert_called()
    update_appt_mock.assert_called()
    create_notification_mock.assert_called()
