import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from flask.testing import FlaskClient
from prisma.models import Appointment, User, Rating, Message
from prisma.errors import RecordNotFoundError

########################### APPOINTMENT ACCEPT TESTS ###########################


@pytest.fixture
def create_notification_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.NotificationActions.create")


@pytest.fixture
def appointment_update_mock(mocker: MockerFixture, fake_tutor, fake_appointment):
    apt = fake_appointment

    def mocked_appointment_update(**kwargs):
        if (
            "id_tutorId" in kwargs["where"]
            and (
                "tutorId" in kwargs["where"]["id_tutorId"]
                and kwargs["where"]["id_tutorId"]["tutorId"] == fake_tutor.id
            )
            and (
                "id" in kwargs["where"]["id_tutorId"]
                and kwargs["where"]["id_tutorId"]["id"] == apt.id
            )
        ):
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


def test_appointment_accept_student_login(setup_test: FlaskClient, fake_login):
    client = setup_test

    # login as student
    fake_login("fake_student")

    resp = client.put("/appointment/accept", json={"id": "id", "accept": True})
    assert resp.json["error"] == "Must be a tutor to modify appointments"
    assert resp.status_code == 403


def test_appointment_accept_invalid_id(
    setup_test: FlaskClient, appointment_update_mock: MockType, fake_login
):
    client = setup_test

    # login as tutor
    fake_login("fake_tutor")

    resp = client.put("/appointment/accept", json={"id": "id", "accept": True})
    appointment_update_mock.assert_called()

    assert (
        resp.json["error"]
        == "Appointment corresponding to id does not exist or, appointment does not involve tutor"
    )
    assert resp.status_code == 400


def test_appointment_accept(
    setup_test: FlaskClient,
    appointment_update_mock: MockType,
    create_notification_mock: MockType,
    fake_appointment,
    fake_login,
):
    client = setup_test
    apt = fake_appointment

    # login as tutor
    fake_login("fake_tutor")

    resp = client.put(
        "/appointment/accept", json={"id": fake_appointment.id, "accept": True}
    )
    appointment_update_mock.assert_called()
    create_notification_mock.assert_called()

    assert resp.status_code == 200
    assert resp.json["id"] == apt.id
    assert resp.json["startTime"] == apt.startTime.isoformat()
    assert resp.json["endTime"] == apt.endTime.isoformat()
    assert resp.json["studentId"] == apt.studentId
    assert resp.json["tutorId"] == apt.tutorId
    assert resp.json["tutorAccepted"] == True


############################### GET TESTS ######################################


def test_appointment_get_invalid(setup_test: FlaskClient):
    client = setup_test

    # no appointment id given
    resp = client.get("/appointment/")
    assert resp.status_code == 405

    # invalid appointment id given
    resp = client.get("/appointment/notvalid")
    assert resp.status_code == 404
    assert resp.json["error"] == "Given id does not correspond to an appointment"


def test_appointment_get(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    fake_appointment,
    fake_tutor,
    fake_login,
):
    client = setup_test

    appointment_find_unique_mock = mocker.patch(
        "tests.conftest.AppointmentActions.find_unique"
    )
    appointment_find_unique_mock.return_value = fake_appointment

    # not logged in
    resp = client.get(f"/appointment/{fake_appointment.id}")
    appointment_find_unique_mock.assert_called_with(
        where={"id": fake_appointment.id}, include={"rating": True}
    )

    assert resp.json["id"] == fake_appointment.id
    assert resp.json["startTime"] == fake_appointment.startTime.isoformat()
    assert resp.json["endTime"] == fake_appointment.endTime.isoformat()
    assert resp.json["tutorId"] == fake_appointment.tutorId
    assert resp.json["tutorAccepted"] == fake_appointment.tutorAccepted
    assert "studentId" not in resp.json
    assert resp.status_code == 200

    # logged in, but appointment not related to current user
    client.post(
        "/login",
        json={
            "email": "validemail4@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": "validemail4@mail.com"}, include=mocker.ANY
    )

    resp = client.get(f"/appointment/{fake_appointment.id}")
    appointment_find_unique_mock.assert_called_with(
        where={"id": fake_appointment.id}, include={"rating": True}
    )

    assert resp.json["id"] == fake_appointment.id
    assert resp.json["startTime"] == fake_appointment.startTime.isoformat()
    assert resp.json["endTime"] == fake_appointment.endTime.isoformat()
    assert resp.json["tutorId"] == fake_appointment.tutorId
    assert resp.json["tutorAccepted"] == fake_appointment.tutorAccepted
    assert "studentId" not in resp.json
    assert resp.status_code == 200

    # logged in, and appointment is related to current user
    fake_login("fake_tutor")

    find_unique_users_mock.assert_called_with(
        where={"email": fake_tutor.email}, include=mocker.ANY
    )

    resp = client.get(f"/appointment/{fake_appointment.id}")
    appointment_find_unique_mock.assert_called_with(
        where={"id": fake_appointment.id}, include={"rating": True}
    )

    assert resp.json["id"] == fake_appointment.id
    assert resp.json["startTime"] == fake_appointment.startTime.isoformat()
    assert resp.json["endTime"] == fake_appointment.endTime.isoformat()
    assert resp.json["tutorId"] == fake_appointment.tutorId
    assert resp.json["tutorAccepted"] == fake_appointment.tutorAccepted
    assert resp.json["studentId"] == fake_appointment.studentId
    assert resp.status_code == 200


############################## REQUEST TESTS ###################################


def test_request_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    fake_student: User,
    fake_tutor: User,
    fake_appointment: Appointment,
    fake_login,
):
    client = setup_test

    # No JSON Body
    resp = client.post("/appointment/request")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # Missing start time
    resp = client.post("/appointment/request", json={})
    assert resp.json == {"error": "'startTime' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing end time
    resp = client.post(
        "/appointment/request", json={"startTime": "2023-10-20T00:00:00+00:00"}
    )
    assert resp.json == {"error": "'endTime' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing tutor id
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2024-10-20T01:00:00+00:00",
        },
    )
    assert resp.json == {"error": "'tutorId' was missing from field(s)"}
    assert resp.status_code == 400

    # No logged in user
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2024-10-20T01:00:00+00:00",
            "tutorId": fake_tutor.id,
        },
    )
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

    # Invalid time (invalid start time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2023",
            "endTime": "2024-10-20T01:00:00+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "startTime and/or endTime field(s) was malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid end time format)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2023",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "startTime and/or endTime field(s) was malformed"}
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
    assert resp.json == {"error": "startTime and/or endTime field(s) was malformed"}
    assert resp.status_code == 400

    # Invalid end time (et < st)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T01:00:00+00:00",
            "endTime": "2024-10-20T00:00:00+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "endTime cannot be less than startTime"}
    assert resp.status_code == 400

    # Invalid tutor id
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-11-20T00:00:00+00:00",
            "endTime": "2024-11-20T01:00:00+00:00",
            "tutorId": "1",
        },
    )
    assert resp.json == {"error": "Tutor profile does not exist"}
    assert resp.status_code == 400

    fake_login("fake_tutor")

    # Invalid user (tutor is logged in)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2024-10-20T01:00:00+00:00",
            "tutorId": fake_tutor.id,
        },
    )
    assert resp.json == {"error": "Profile is not a student"}
    assert resp.status_code == 400

    client.post("/logout")
    fake_login("fake_admin")

    # Invalid user (admin is logged in)
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2024-10-20T01:00:00+00:00",
            "tutorId": fake_tutor.id,
        },
    )
    assert resp.json == {"error": "Profile is not a student"}
    assert resp.status_code == 400

    client.post("/logout")
    fake_login("fake_student")

    create_mock = mocker.patch("tests.conftest.AppointmentActions.create")
    create_mock.return_value = fake_appointment

    # Valid Input
    resp = client.post(
        "/appointment/request",
        json={
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2024-10-21T00:00:00+00:00",
            "tutorId": fake_tutor.id,
        },
    )

    assert resp.status_code == 200
    assert resp.json["startTime"] == "2024-10-20T00:00:00+00:00"
    assert resp.json["endTime"] == "2024-10-21T00:00:00+00:00"
    assert resp.json["studentId"] == fake_student.id
    assert resp.json["tutorId"] == fake_tutor.id
    assert resp.json["tutorAccepted"] == False


############################### DELETE TESTS ###################################


def test_delete_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock,
    fake_tutor2: User,
    fake_appointment: Appointment,
    create_notification_mock: MockType,
):
    client = setup_test

    # No JSON Body
    resp = client.delete("/appointment/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # Missing id
    resp = client.delete("/appointment/", json={})
    assert resp.json == {"error": "'id' was missing from field(s)"}
    assert resp.status_code == 400

    # No logged in user
    resp = client.delete("/appointment/", json={"id": fake_appointment.id})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    client.post(
        "/login",
        json={
            "email": fake_tutor2.email,
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": fake_tutor2.email}, include=mocker.ANY
    )

    resp = client.delete("/appointment/", json={"id": "123"})
    assert resp.json == {"error": "Appointment does not exist"}
    assert resp.status_code == 404

    find = mocker.patch("tests.conftest.AppointmentActions.find_unique")
    find.return_value = fake_appointment

    delete_notification_mock = mocker.patch(
        "tests.conftest.NotificationActions.delete_many"
    )

    delete = mocker.patch("tests.conftest.AppointmentActions.delete")
    resp = client.delete("/appointment/", json={"id": fake_appointment.id})
    delete.assert_called()
    create_notification_mock.assert_called()
    delete_notification_mock.assert_called()

    assert resp.status_code == 200
    assert resp.json["success"] == True


############################### MODIFY TESTS ###################################


def test_modify_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock,
    fake_tutor2: User,
    fake_appointment: Appointment,
    create_notification_mock: MockType,
):
    client = setup_test

    # No JSON Body
    resp = client.put("/appointment/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # Missing id
    resp = client.put("/appointment/", json={})
    assert resp.json == {"error": "'id' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing start time
    resp = client.put("/appointment/", json={"id": "123"})
    assert resp.json == {"error": "'startTime' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing end time
    resp = client.put(
        "/appointment/", json={"id": "123", "startTime": "2023-10-20T00:00:00+00:00"}
    )
    assert resp.json == {"error": "'endTime' was missing from field(s)"}
    assert resp.status_code == 400

    # No logged in user
    resp = client.put(
        "/appointment/",
        json={
            "id": "123",
            "startTime": "2023-10-20T00:00:00+00:00",
            "endTime": "2024-10-20T01:00:00+00:00",
        },
    )
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    client.post(
        "/login",
        json={
            "email": fake_tutor2.email,
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    find_unique_users_mock.assert_called_with(
        where={"email": fake_tutor2.email}, include=mocker.ANY
    )

    # Invalid time (invalid start time format)
    resp = client.put(
        "/appointment/",
        json={
            "id": "123",
            "startTime": "2023",
            "endTime": "2024-10-20T01:00:00+00:00",
        },
    )
    assert resp.json == {"error": "startTime and/or endTime field(s) was malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid end time format)
    resp = client.put(
        "/appointment/",
        json={
            "id": "123",
            "startTime": "2024-10-20T00:00:00+00:00",
            "endTime": "2023",
        },
    )
    assert resp.json == {"error": "startTime and/or endTime field(s) was malformed"}
    assert resp.status_code == 400

    # Invalid time (invalid both time format)
    resp = client.put(
        "/appointment/",
        json={
            "id": "123",
            "startTime": "2023",
            "endTime": "2024",
        },
    )
    assert resp.json == {"error": "startTime and/or endTime field(s) was malformed"}
    assert resp.status_code == 400

    # Invalid end time (et < st)
    resp = client.put(
        "/appointment/",
        json={
            "id": "123",
            "startTime": "2024-10-20T01:00:00+00:00",
            "endTime": "2024-10-20T00:00:00+00:00",
        },
    )
    assert resp.json == {"error": "endTime cannot be less than startTime"}
    assert resp.status_code == 400

    # Invalid tutor id
    resp = client.put(
        "/appointment/",
        json={
            "id": "123",
            "startTime": "2024-11-20T00:00:00+00:00",
            "endTime": "2024-11-20T01:00:00+00:00",
        },
    )
    assert resp.json == {"error": "Appointment does not exist"}
    assert resp.status_code == 404

    find = mocker.patch("tests.conftest.AppointmentActions.find_unique")
    find.return_value = fake_appointment

    update = mocker.patch("tests.conftest.AppointmentActions.update")
    resp = client.put(
        "/appointment/",
        json={
            "id": fake_appointment.id,
            "startTime": "2024-11-20T00:00:00+00:00",
            "endTime": "2024-11-20T01:00:00+00:00",
        },
    )
    update.assert_called()
    create_notification_mock.assert_called()
    assert resp.json == {"success": True}
    assert resp.status_code == 200


############################### RATING TESTS ###################################


def test_rating_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    fake_appointment_fin: Appointment,
    fake_rating: Rating,
    fake_login,
):
    client = setup_test

    # No JSON Body
    resp = client.post("/appointment/rating")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # Missing id
    resp = client.post("/appointment/rating", json={})
    assert resp.json == {"error": "'id' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing rating field
    resp = client.post("/appointment/rating", json={"id": "123"})
    assert resp.json == {"error": "'rating' was missing from field(s)"}
    assert resp.status_code == 400

    resp = client.post(
        "/appointment/rating", json={"id": fake_appointment_fin.id, "rating": 10}
    )
    assert resp.json == {"error": "rating must be between 1 to 5, inclusive"}
    assert resp.status_code == 400

    # No logged in user
    resp = client.post(
        "/appointment/rating", json={"id": fake_appointment_fin.id, "rating": 5}
    )
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_student")

    # Invalid appointment id
    resp = client.post("/appointment/rating", json={"id": "123", "rating": 5})
    assert resp.json == {"error": "Appointment does not exist"}
    assert resp.status_code == 400

    appointment_find_unique_mock = mocker.patch(
        "tests.conftest.AppointmentActions.find_unique"
    )
    appointment_find_unique_mock.return_value = fake_appointment_fin
    rating_upsert_mock = mocker.patch("tests.conftest.RatingActions.upsert")
    rating_upsert_mock.return_value = fake_rating

    # successful rating on an appointment
    resp = client.post(
        "/appointment/rating", json={"id": fake_appointment_fin.id, "rating": 5}
    )
    appointment_find_unique_mock.assert_called()
    appointment_find_unique_mock.reset_mock()
    rating_upsert_mock.assert_called()
    rating_upsert_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["success"] == True

    # rating an appointment again
    rating = Rating(
        id="id",
        score=5,
        appointment=fake_appointment_fin,
        appointmentId=fake_appointment_fin.id,
        createdFor=fake_appointment_fin.tutor,
        tutorId=fake_appointment_fin.tutorId,
    )
    fake_appointment_fin.rating = rating
    rating_upsert_mock.return_value = rating

    resp = client.post(
        "/appointment/rating", json={"id": fake_appointment_fin.id, "rating": 5}
    )
    appointment_find_unique_mock.assert_called()
    appointment_find_unique_mock.reset_mock()
    rating_upsert_mock.assert_called()
    rating_upsert_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["success"] == True


############################### MESSAGE TESTS ##################################


def test_message_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    fake_appointment: Appointment,
    fake_message: Message,
    fake_login,
):
    client = setup_test

    # No JSON Body
    resp = client.post("/appointment/message")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # Missing id
    resp = client.post("/appointment/message", json={})
    assert resp.json == {"error": "'id' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing message field
    resp = client.post("/appointment/message", json={"id": "123"})
    assert resp.json == {"error": "'message' was missing from field(s)"}
    assert resp.status_code == 400

    resp = client.post(
        "/appointment/message", json={"id": fake_appointment.id, "message": "hi"}
    )
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_student")

    # Invalid appointment id
    resp = client.post("/appointment/message", json={"id": "123", "message": "hi"})
    assert resp.json == {"error": "Appointment does not exist"}
    assert resp.status_code == 400

    appointment_find_unique_mock = mocker.patch(
        "tests.conftest.AppointmentActions.find_unique"
    )
    appointment_find_unique_mock.return_value = fake_appointment
    message_create_mock = mocker.patch("tests.conftest.MessageActions.create")
    message_create_mock.return_value = fake_message
    pusher_channel_info_mock = mocker.patch("tests.conftest.Pusher.channel_info")
    pusher_channel_info_mock.return_value = {"occupied": True}
    notif_mock = mocker.patch("tests.conftest.NotificationActions.create")
    appointment_update_mock = mocker.patch("tests.conftest.AppointmentActions.update")

    # successful message on an appointment
    resp = client.post(
        "/appointment/message", json={"id": fake_appointment.id, "message": "hi"}
    )
    message_create_mock.assert_called()
    message_create_mock.reset_mock()
    appointment_update_mock.assert_called()
    appointment_update_mock.reset_mock()
    notif_mock.assert_not_called()
    pusher_channel_info_mock.assert_called()
    pusher_channel_info_mock.reset_mock()
    assert resp.status_code == 200
    assert "id" in resp.json
    assert "sentTime" in resp.json

    pusher_channel_info_mock.return_value = {"occupied": False}
    resp = client.post(
        "/appointment/message", json={"id": fake_appointment.id, "message": "hi"}
    )
    message_create_mock.assert_called()
    message_create_mock.reset_mock()
    appointment_update_mock.assert_called()
    appointment_update_mock.reset_mock()
    notif_mock.assert_called()
    pusher_channel_info_mock.assert_called()
    pusher_channel_info_mock.reset_mock()
    assert resp.status_code == 200
    assert "id" in resp.json
    assert "sentTime" in resp.json


############################## MESSAGES TESTS ##################################


def test_messages_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    fake_message: Message,
    fake_message2: Message,
    fake_appointment_msg: Appointment,
    fake_login,
):
    client = setup_test

    # Missing id, defaults to appointment/<appointment_id> route
    resp = client.get("/appointment/messages")
    assert resp.status_code == 404

    # Missing not logged in
    resp = client.get("/appointment/123/messages")
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 401

    fake_login("fake_student")

    # Invalid appointment id
    resp = client.get("/appointment/123/messages")
    assert resp.json == {"error": "Appointment does not exist"}
    assert resp.status_code == 400

    appointment_find_unique_mock = mocker.patch(
        "tests.conftest.AppointmentActions.find_unique"
    )
    appointment_find_unique_mock.return_value = fake_appointment_msg
    fake_appointment_msg.messages = [fake_message2, fake_message]

    # successful message on an appointment
    resp = client.get(f"/appointment/{fake_appointment_msg.id}/messages")
    assert resp.status_code == 200
    assert resp.json["messages"] == [
        {
            "id": fake_message2.id,
            "sentBy": fake_message2.sentById,
            "sentTime": fake_message2.sentTime.isoformat(),
            "content": fake_message2.content,
        },
        {
            "id": fake_message.id,
            "sentBy": fake_message.sentById,
            "sentTime": fake_message.sentTime.isoformat(),
            "content": fake_message.content,
        },
    ]
