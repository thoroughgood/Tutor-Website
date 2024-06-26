from flask.testing import FlaskClient
from prisma.models import User
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType


def test_admin_search_not_login(setup_test: FlaskClient):
    client = setup_test

    resp = client.get("/admin/search")
    assert resp.status_code == 401
    assert resp.json["error"] == "No user is logged in"


def test_admin_search_student_login(setup_test: FlaskClient, fake_login):
    client = setup_test

    # login as student
    fake_login("fake_student")

    resp = client.get("/admin/search")
    assert resp.status_code == 403
    assert resp.json["error"] == "Insufficient permission to search for users"


def test_admin_search_tutor_login(setup_test: FlaskClient, fake_login):
    client = setup_test

    # login as tutor
    fake_login("fake_tutor")

    resp = client.get("/admin/search")
    assert resp.status_code == 403
    assert resp.json["error"] == "Insufficient permission to search for users"


def test_admin_search_no_args(
    setup_test: FlaskClient,
    find_many_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    find_many_users_mock.return_value = [fake_student, fake_tutor, fake_admin]

    resp = client.get("/admin/search")
    find_many_users_mock.assert_called()

    assert resp.status_code == 200
    assert all(
        d
        in [
            {"id": fake_student.id, "accountType": "student"},
            {"id": fake_tutor.id, "accountType": "tutor"},
            {"id": fake_admin.id, "accountType": "admin"},
        ]
        for d in resp.json["userInfos"]
    )


def test_admin_search_id(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_unique_users_mock: MockType,
    find_many_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # id belongs to no one
    find_many_users_mock.return_value = []

    resp = client.get("/admin/search", query_string={"id": "nonexist"})
    find_unique_users_mock.assert_called_with(
        where={"id": "nonexist"}, include=mocker.ANY
    )
    find_unique_users_mock.reset_mock()

    assert resp.status_code == 200
    assert len(resp.json["userInfos"]) == 0

    # student
    resp = client.get("/admin/search", query_string={"id": fake_student.id})
    find_unique_users_mock.assert_called_with(
        where={"id": fake_student.id}, include=mocker.ANY
    )
    find_unique_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_student.id, "accountType": "student"}]

    # tutor
    resp = client.get("/admin/search", query_string={"id": fake_tutor.id})
    find_unique_users_mock.assert_called_with(
        where={"id": fake_tutor.id}, include=mocker.ANY
    )
    find_unique_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_tutor.id, "accountType": "tutor"}]

    # admin
    resp = client.get("/admin/search", query_string={"id": fake_admin.id})
    find_unique_users_mock.assert_called_with(
        where={"id": fake_admin.id}, include=mocker.ANY
    )
    find_unique_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_admin.id, "accountType": "admin"}]


def test_admin_search_name(
    setup_test: FlaskClient,
    find_many_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # invalid name
    resp = client.get("/admin/search", query_string={"name": ""})

    assert resp.status_code == 400
    assert resp.json["error"] == "name field must be at least 1 character(s)"

    # name belongs to no one
    find_many_users_mock.return_value = []

    resp = client.get("/admin/search", query_string={"name": "nonexist"})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert len(resp.json["userInfos"]) == 0

    # student
    find_many_users_mock.return_value = [fake_student]

    resp = client.get("/admin/search", query_string={"name": fake_student.name})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_student.id, "accountType": "student"}]

    # tutor
    find_many_users_mock.return_value = [fake_tutor]

    resp = client.get("/admin/search", query_string={"name": fake_tutor.name})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_tutor.id, "accountType": "tutor"}]

    # admin
    find_many_users_mock.return_value = [fake_admin]

    resp = client.get("/admin/search", query_string={"name": fake_admin.name})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_admin.id, "accountType": "admin"}]


def test_admin_search_email(
    setup_test: FlaskClient,
    find_many_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # invalid email
    resp = client.get("/admin/search", query_string={"email": "invalidmail"})

    assert resp.status_code == 400
    assert resp.json["error"] == "email field is invalid"

    # email belongs to no one
    find_many_users_mock.return_value = []

    resp = client.get("/admin/search", query_string={"email": "nonexist@mail.com"})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert len(resp.json["userInfos"]) == 0

    # student
    find_many_users_mock.return_value = [fake_student]

    resp = client.get("/admin/search", query_string={"email": fake_student.email})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_student.id, "accountType": "student"}]

    # tutor
    find_many_users_mock.return_value = [fake_tutor]

    resp = client.get("/admin/search", query_string={"email": fake_tutor.email})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_tutor.id, "accountType": "tutor"}]

    # admin
    find_many_users_mock.return_value = [fake_admin]

    resp = client.get("/admin/search", query_string={"email": fake_admin.email})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_admin.id, "accountType": "admin"}]


def test_admin_search_phone_number(
    setup_test: FlaskClient,
    find_many_users_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # phone number belongs to no one
    find_many_users_mock.return_value = []

    resp = client.get("/admin/search", query_string={"phoneNumber": "0400000000"})
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert len(resp.json["userInfos"]) == 0

    # student
    find_many_users_mock.return_value = [fake_student]

    resp = client.get(
        "/admin/search", query_string={"phoneNumber": fake_student.phoneNumber}
    )
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_student.id, "accountType": "student"}]

    # tutor
    find_many_users_mock.return_value = [fake_tutor]

    resp = client.get(
        "/admin/search", query_string={"phoneNumber": fake_tutor.phoneNumber}
    )
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_tutor.id, "accountType": "tutor"}]

    # admin
    find_many_users_mock.return_value = [fake_admin]

    resp = client.get(
        "/admin/search", query_string={"phoneNumber": fake_admin.phoneNumber}
    )
    find_many_users_mock.assert_called_once()
    find_many_users_mock.reset_mock()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_admin.id, "accountType": "admin"}]


def test_admin_search_account_type(
    setup_test: FlaskClient,
    find_many_tutors_mock: MockType,
    find_many_students_mock: MockType,
    find_many_admins_mock: MockType,
    fake_student,
    fake_tutor,
    fake_admin,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # invalid account type
    resp = client.get("/admin/search", query_string={"accountType": "invalid"})

    assert resp.status_code == 400
    assert resp.json["error"] == "accountType must match student|tutor|admin"

    # student
    find_many_students_mock.return_value = [fake_student.studentInfo]

    resp = client.get("/admin/search", query_string={"accountType": "student"})
    find_many_students_mock.assert_called_once()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_student.id, "accountType": "student"}]

    # tutor
    find_many_tutors_mock.return_value = [fake_tutor.tutorInfo]

    resp = client.get("/admin/search", query_string={"accountType": "tutor"})
    find_many_tutors_mock.assert_called_once()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_tutor.id, "accountType": "tutor"}]

    # admin
    find_many_admins_mock.return_value = [fake_admin.adminInfo]

    resp = client.get("/admin/search", query_string={"accountType": "admin"})
    find_many_admins_mock.assert_called_once()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_admin.id, "accountType": "admin"}]


def test_admin_search_args(
    setup_test: FlaskClient,
    find_many_students_mock: MockType,
    fake_student,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # excluding id given it's a unique attribute
    find_many_students_mock.return_value = [fake_student.studentInfo]

    resp = client.get(
        "/admin/search",
        query_string={
            "name": fake_student.name,
            "email": fake_student.email,
            "phoneNumber": fake_student.phoneNumber,
            "accountType": "student",
        },
    )
    find_many_students_mock.assert_called_once()

    assert resp.status_code == 200
    assert resp.json["userInfos"] == [{"id": fake_student.id, "accountType": "student"}]


def test_admin_create_not_login(setup_test: FlaskClient):
    client = setup_test

    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "email@email.com",
            "password": "12345678",
        },
    )
    assert resp.status_code == 401
    assert resp.json["error"] == "No user is logged in"


def test_admin_create_student_login(setup_test: FlaskClient, fake_login):
    client = setup_test

    # login as student
    fake_login("fake_student")

    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "email@email.com",
            "password": "12345678",
        },
    )
    assert resp.status_code == 403
    assert resp.json["error"] == "Insufficient permission to create a new admin account"


def test_admin_create_tutor_login(setup_test: FlaskClient, fake_login):
    client = setup_test

    # login as tutor
    fake_login("fake_tutor")

    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "email@email.com",
            "password": "12345678",
        },
    )
    assert resp.status_code == 403
    assert resp.json["error"] == "Insufficient permission to create a new admin account"


def test_admin_create_invalid_args(setup_test: FlaskClient, fake_login):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    # omitted name
    resp = client.post(
        "admin/create",
        json={
            "email": "email@email.com",
            "password": "12345678",
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "'name' was missing from field(s)"

    # omitted email
    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "password": "12345678",
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "'email' was missing from field(s)"

    # omitted password
    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "email@email.com",
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "'password' was missing from field(s)"

    # invalid email
    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "notvalid",
            "password": "12345678",
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "email field is invalid"

    # invalid name
    resp = client.post(
        "admin/create",
        json={
            "name": "",
            "email": "mail@gmail.com",
            "password": "12345678",
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "name field must be at least 1 character(s)"

    # invalid password
    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "mail@gmail.com",
            "password": "1234567",
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "password field must be at least 8 character(s)"


def test_create_admin_valid(
    setup_test: FlaskClient,
    mocker: MockerFixture,
    find_many_admins_mock: MockType,
    fake_admin,
    fake_user,
    fake_login,
):
    client = setup_test

    # login as admin
    fake_login("fake_admin")

    user_create_mock = mocker.patch("tests.conftest.UserActions.create")
    resp = client.post(
        "admin/create",
        json={
            "name": "newAdmin",
            "email": "email@email.com",
            "password": "12345678",
        },
    )
    user_create_mock.assert_called()
    assert resp.status_code == 200

    # go 'find' new admin
    new_fake_admin: User = fake_user("email@email.com", "12345678", "admin")
    new_fake_admin.name = "newAdmin"
    new_fake_admin.id = resp.json["id"]

    find_many_admins_mock.return_value = [
        fake_admin.adminInfo,
        new_fake_admin.adminInfo,
    ]

    resp = client.get("/admin/search", query_string={"accountType": "admin"})
    find_many_admins_mock.assert_called_once()

    assert resp.status_code == 200
    assert all(
        d
        in [
            {"id": new_fake_admin.id, "accountType": "admin"},
            {"id": fake_admin.id, "accountType": "admin"},
        ]
        for d in resp.json["userInfos"]
    )
