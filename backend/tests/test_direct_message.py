from datetime import datetime, timedelta
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.models import User, Message, DirectMessage
import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType


@pytest.fixture
def dm_find_many_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.DirectMessageActions.find_many")


@pytest.fixture
def dm_find_first_mock(mocker: MockerFixture):
    return mocker.patch("tests.conftest.DirectMessageActions.find_first")


def test_dm_all_invalid(setup_test: FlaskClient):
    client = setup_test

    # not logged in
    resp = client.get("directmessage/all")
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401


def test_dm_all_args(
    setup_test: FlaskClient,
    fake_login,
    dm_find_many_mock: MockType,
    fake_student,
    fake_tutor,
    fake_user,
):
    client = setup_test
    fake_login("fake_student")

    # no dms
    dm_find_many_mock.return_value = []

    resp = client.get("directmessage/all")
    dm_find_many_mock.assert_called()
    dm_find_many_mock.reset_mock()

    assert resp.json["otherIds"] == []
    assert resp.status_code == 200

    # one dm, no messages
    dm_find_many_mock.return_value = [
        DirectMessage(
            id=str(uuid4()),
            messages=[],
            fromUser=fake_student,
            fromUserId=fake_student.id,
            otherUser=fake_tutor,
            otherUserId=fake_tutor.id,
        )
    ]

    resp = client.get("directmessage/all")
    dm_find_many_mock.assert_called()
    dm_find_many_mock.reset_mock()

    assert resp.json["otherIds"] == [fake_tutor.id]
    assert resp.status_code == 200

    # two dms, no messages
    fake_tutor2: User = fake_user("email@email.com", "12345678", "tutor")
    dm_find_many_mock.return_value = [
        DirectMessage(
            id=str(uuid4()),
            messages=[],
            fromUser=fake_student,
            fromUserId=fake_student.id,
            otherUser=fake_tutor,
            otherUserId=fake_tutor.id,
        ),
        # checking for if route works irrelvant of from and other
        DirectMessage(
            id=str(uuid4()),
            messages=[],
            fromUser=fake_tutor2,
            fromUserId=fake_tutor2.id,
            otherUser=fake_student,
            otherUserId=fake_student.id,
        ),
    ]

    resp = client.get("directmessage/all")
    dm_find_many_mock.assert_called()
    dm_find_many_mock.reset_mock()

    # should be in order of added by
    assert resp.json["otherIds"] == [fake_tutor.id, fake_tutor2.id]
    assert resp.status_code == 200

    # two dms, one with message
    dm_find_many_mock.return_value = [
        DirectMessage(
            id=str(uuid4()),
            messages=[],
            fromUser=fake_student,
            fromUserId=fake_student.id,
            otherUser=fake_tutor,
            otherUserId=fake_tutor.id,
        ),
        # checking for if route works irrelvant of from and other
        DirectMessage(
            id=str(uuid4()),
            messages=[
                Message(
                    id=str(uuid4()),
                    sentTime=datetime.now(),
                    content="msg",
                    sentBy=fake_student,
                    sentById=fake_student.id,
                ),
            ],
            fromUser=fake_tutor2,
            fromUserId=fake_tutor2.id,
            otherUser=fake_student,
            otherUserId=fake_student.id,
        ),
    ]

    resp = client.get("directmessage/all")
    dm_find_many_mock.assert_called()
    dm_find_many_mock.reset_mock()

    # a DM without messages should be pushed to the back of the list
    assert resp.json["otherIds"] == [fake_tutor2.id, fake_tutor.id]
    assert resp.status_code == 200

    # two dms, both with messages
    dm_find_many_mock.return_value = [
        DirectMessage(
            id=str(uuid4()),
            messages=[
                Message(
                    id=str(uuid4()),
                    sentTime=datetime.now() - timedelta(days=1),
                    content="msg",
                    sentBy=fake_student,
                    sentById=fake_student.id,
                ),
            ],
            fromUser=fake_student,
            fromUserId=fake_student.id,
            otherUser=fake_tutor,
            otherUserId=fake_tutor.id,
        ),
        # checking for if route works irrelvant of from and other
        DirectMessage(
            id=str(uuid4()),
            messages=[
                Message(
                    id=str(uuid4()),
                    sentTime=datetime.now(),
                    content="msg",
                    sentBy=fake_student,
                    sentById=fake_student.id,
                ),
            ],
            fromUser=fake_tutor2,
            fromUserId=fake_tutor2.id,
            otherUser=fake_student,
            otherUserId=fake_student.id,
        ),
    ]

    resp = client.get("directmessage/all")
    dm_find_many_mock.assert_called()
    dm_find_many_mock.reset_mock()

    # the one with the most recently sent message should come first
    assert resp.json["otherIds"] == [fake_tutor2.id, fake_tutor.id]
    assert resp.status_code == 200


def test_dm_get_invalid(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    fake_login,
    dm_find_first_mock: MockType,
):
    client = setup_test

    mocker.patch("tests.conftest.NotificationActions.delete_many")

    # otherId was not provided in path params
    resp = client.get("directmessage/")
    assert resp.status_code == 405

    # not logged in
    resp = client.get("directmessage/invalidId")
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401

    fake_login("fake_student")

    # otherId is not associated with anyone
    dm_find_first_mock.return_value = None

    resp = client.get("directmessage/invalidId")
    dm_find_first_mock.assert_called()
    dm_find_first_mock.reset_mock()

    assert resp.json["messages"] == []
    assert resp.status_code == 200


def test_dm_get_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    fake_login,
    dm_find_first_mock: MockType,
    fake_student,
    fake_tutor,
):
    client = setup_test

    mocker.patch("tests.conftest.NotificationActions.delete_many")
    fake_login("fake_student")

    # dm with no messages
    dm_find_first_mock.return_value = DirectMessage(
        id="dm1",
        messages=[],
        fromUser=fake_student,
        fromUserId=fake_student.id,
        otherUser=fake_tutor,
        otherUserId=fake_tutor.id,
    )

    resp = client.get("directmessage/dm1")
    dm_find_first_mock.assert_called()

    assert resp.json["messages"] == []
    assert resp.status_code == 200

    # with messages
    message1 = Message(
        id=str(uuid4()),
        sentTime=datetime.now(),
        content="msg",
        sentBy=fake_student,
        sentById=fake_student.id,
    )

    message2 = Message(
        id=str(uuid4()),
        sentTime=datetime.now() + timedelta(days=1),
        content="another msg",
        sentBy=fake_tutor,
        sentById=fake_tutor.id,
    )

    dm_find_first_mock.return_value = DirectMessage(
        id="dm1",
        messages=[message2, message1],
        fromUser=fake_student,
        fromUserId=fake_student.id,
        otherUser=fake_tutor,
        otherUserId=fake_tutor.id,
    )

    resp = client.get("directmessage/dm1")
    dm_find_first_mock.assert_called()

    assert resp.json["messages"] == [
        {
            "id": message2.id,
            "sentBy": message2.sentById,
            "sentTime": message2.sentTime.isoformat(),
            "content": message2.content,
        },
        {
            "id": message1.id,
            "sentBy": message1.sentById,
            "sentTime": message1.sentTime.isoformat(),
            "content": message1.content,
        },
    ]
    assert resp.status_code == 200


def test_dm_post_invalid(
    setup_test: FlaskClient,
    fake_login,
    find_unique_users_mock: MockType,
):
    client = setup_test

    # No json body
    resp = client.post("directmessage/")
    assert resp.json["error"] == "content-type was not json or data was malformed"
    assert resp.status_code == 415

    # otherId was omitted
    resp = client.post("directmessage/", json={})
    assert resp.json["error"] == "'otherId' was missing from field(s)"
    assert resp.status_code == 400

    # message was omitted
    resp = client.post("directmessage/", json={"otherId": "someId"})
    assert resp.json["error"] == "'message' was missing from field(s)"
    assert resp.status_code == 400

    # not logged in
    resp = client.post(
        "directmessage/", json={"otherId": "someId", "message": "some message"}
    )
    assert resp.json["error"] == "No user is logged in"
    assert resp.status_code == 401

    fake_login("fake_student")

    # otherId does not correspond to a user
    find_unique_users_mock.return_value = None

    resp = client.post(
        "directmessage/", json={"otherId": "someId", "message": "some message"}
    )
    assert resp.json["error"] == "otherId does not correspond to an user"
    assert resp.status_code == 400


def test_dm_post_args(
    setup_test: FlaskClient,
    fake_login,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    dm_find_first_mock: MockType,
    fake_tutor,
):
    client = setup_test

    fake_login("fake_student")

    dm_find_first_mock.return_value = None
    dm_upsert_mock = mocker.patch("tests.conftest.DirectMessageActions.upsert")
    notification_create_mock = mocker.patch("tests.conftest.NotificationActions.create")

    # no users 'listening' for messages
    find_unique_users_mock.return_value = fake_tutor
    resp = client.post(
        "directmessage/", json={"otherId": fake_tutor.id, "message": "some message"}
    )
    dm_upsert_mock.assert_called()
    dm_upsert_mock.reset_mock()
    notification_create_mock.assert_called()
    notification_create_mock.reset_mock()

    # no way to really test these unfortunately
    assert "id" in resp.json
    assert "sentTime" in resp.json

    # a user is 'listening' for messages
    pusher_channel_info_mock = mocker.patch("tests.conftest.Pusher.channel_info")
    pusher_channel_info_mock.return_value = {"occupied": True, "subscription_count": 1}

    find_unique_users_mock.return_value = fake_tutor
    resp = client.post(
        "directmessage/", json={"otherId": fake_tutor.id, "message": "some message"}
    )
    dm_upsert_mock.assert_called()
    dm_upsert_mock.reset_mock()
    notification_create_mock.assert_not_called()
    pusher_channel_info_mock.assert_called()
    pusher_channel_info_mock.reset_mock()

    # no way to really test these unfortunately
    assert "id" in resp.json
    assert "sentTime" in resp.json
