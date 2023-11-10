############################## MESSAGES TESTS ##################################


def test_messages_args(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock,
    fake_student: User,
    fake_message: Message,
    fake_message2: Message,
    fake_appointment_msg: Appointment,
):
    client = setup_test

    # No JSON Body
    resp = client.get("/appointment/messages")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415

    # Missing id
    resp = client.get("/appointment/messages", json={})
    assert resp.json == {"error": "'id' was missing from field(s)"}
    assert resp.status_code == 400

    # Missing message field
    resp = client.get("/appointment/messages", json={"id": "123"})
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

    # Invalid appointment id
    resp = client.get("/appointment/messages", json={"id": "123"})
    assert resp.json == {"error": "Appointment does not exist"}
    assert resp.status_code == 400

    appointment_find_unique_mock = mocker.patch(
        "tests.conftest.AppointmentActions.find_unique"
    )
    appointment_find_unique_mock.return_value = fake_appointment_msg
    msg_find = mocker.patch("tests.conftest.MessageActions.find_many")
    msg_find.return_value = [fake_message2, fake_message]

    # successful message on an appointment
    resp = client.get(
        "/appointment/messages",
        json={
            "id": fake_appointment_msg.id,
        },
    )
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
