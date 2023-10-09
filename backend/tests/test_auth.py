from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import Admin, Tutor, Student


def test_register_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.post("/register")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


def test_register_args(setup_test: FlaskClient):
    assert Student.prisma().count() == 0
    assert Tutor.prisma().count() == 0

    client = setup_test
    resp = client.post("/register", json={})
    assert resp.json == {"error": "name field was missing"}
    assert resp.status_code == 400

    resp = client.post("/register", json={"name": "name"})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    resp = client.post("/register", json={"name": "name", "email": "notvalidemail"})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    resp = client.post(
        "/register", json={"name": "name", "email": "validemail@mail.com"}
    )
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    resp = client.post(
        "/register",
        json={"name": "name", "email": "validemail@mail.com", "password": "1234567"},
    )
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    resp = client.post(
        "/register",
        json={"name": "name", "email": "validemail@mail.com", "password": "12345678"},
    )
    assert resp.json == {"error": "accountType field missing"}
    assert resp.status_code == 400

    resp = client.post(
        "/register",
        json={
            "name": "name",
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "notvalid",
        },
    )
    assert resp.json == {"error": "accountType must be 'student' or 'tutor'"}
    assert resp.status_code == 400

    # successfully signup (student)
    resp = client.post(
        "/register",
        json={
            "name": "name",
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    assert "id" in resp.json
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]

    resp = client.post(
        "/register",
        json={
            "name": "name",
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    assert resp.json == {"error": "user already exists with this email"}
    assert resp.status_code == 400

    resp = client.post(
        "/register",
        json={
            "name": "name",
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.json == {"error": "user already exists with this email"}
    assert resp.status_code == 400

    # successfully signup (tutor)
    resp = client.post(
        "/register",
        json={
            "name": "name",
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert "id" in resp.json
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]

    assert Student.prisma().count() == 1
    assert Tutor.prisma().count() == 1


################################# LOGIN TESTS ##################################


def test_login_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.post("/login")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


@pytest.fixture
def initialise_student() -> str:
    student = Student.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name1",
            "bio": "",
            "location": "Australia",
        },
    )
    return student.id


@pytest.fixture
def initialise_tutor() -> str:
    tutor = Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail2@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Name2",
            "bio": "",
            "location": "Australia",
        },
    )
    return tutor.id


@pytest.fixture
def initialise_admin() -> str:
    admin = Admin.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail3@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Admean",
        }
    )
    return admin.id


def test_login_args(setup_test: FlaskClient, initialise_student: str):
    client = setup_test
    # Missing email
    resp = client.post("/login", json={})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Invalid Email
    resp = client.post("/login", json={"email": "notvalidemail"})
    assert resp.json == {"error": "email field is invalid"}
    assert resp.status_code == 400

    # Missing password
    resp = client.post("/login", json={"email": "validemail@mail.com"})
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    # Invalid password
    resp = client.post(
        "/login", json={"email": "validemail@mail.com", "password": "ab12"}
    )
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    # Missing accountType
    resp = client.post(
        "/login",
        json={"email": "validemail@mail.com", "password": "12345678"},
    )
    assert resp.json == {"error": "accountType must be 'student' or 'tutor' or 'admin'"}
    assert resp.status_code == 400

    # Invalid accountType
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "notvalid",
        },
    )
    assert resp.json == {"error": "accountType must be 'student' or 'tutor' or 'admin'"}
    assert resp.status_code == 400

    # Invalid login attempt (wrong password)
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345677",
            "accountType": "student",
        },
    )
    assert resp.json == {"error": "Invalid login attempt"}
    assert resp.status_code == 401

    # Successful login attempt (student)
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]


# Successful login attempt (tutor)
def test_tutor_login(setup_test: FlaskClient, initialise_tutor: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]


# Successful login attempt (admin)
def test_admin_login(setup_test: FlaskClient, initialise_admin: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]


################################# LOGOUT TESTS #################################


def test_logout_no_user(setup_test: FlaskClient):
    client = setup_test
    with client.session_transaction() as session:
        assert ("user_id" not in session) == True
    resp = client.post("/logout")
    assert resp.json == {"success": True}
    assert resp.status_code == 200


def test_logout_student(setup_test: FlaskClient, initialise_student: str):
    client = setup_test
    resp1 = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )

    with client.session_transaction() as session:
        assert session["user_id"] == resp1.json["id"]

    resp2 = client.post("/logout")
    with client.session_transaction() as session:
        assert ("user_id" not in session) == True
    assert resp2.status_code == 200
    assert resp2.json["success"] == True


def test_logout_tutor(setup_test: FlaskClient, initialise_tutor: str):
    client = setup_test
    resp1 = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    with client.session_transaction() as session:
        assert session["user_id"] == resp1.json["id"]

    resp = client.post("/logout", json={})
    with client.session_transaction() as session:
        assert ("user_id" not in session) == True
    assert resp.status_code == 200
    assert resp.json["success"] == True


def test_logout_admin(setup_test: FlaskClient, initialise_admin: str):
    client = setup_test
    resp1 = client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    with client.session_transaction() as session:
        assert session["user_id"] == resp1.json["id"]

    resp = client.post("/logout", json={})
    with client.session_transaction() as session:
        assert ("user_id" not in session) == True
    assert resp.status_code == 200
    assert resp.json["success"] == True


########################## RESET PASSWORD TESTS ################################


# Not correct json input
def test_resetpassword_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.put("/resetpassword")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


# No user logged in
def test_resetpassword_no_user(setup_test: FlaskClient):
    client = setup_test
    with client.session_transaction() as session:
        assert ("user_id" not in session) == True
    resp = client.put("/resetpassword", json={})
    assert resp.status_code == 400
    assert resp.json == {"error": "No user is logged in"}


# No user logged in
def test_resetpassword_student_login(setup_test: FlaskClient, initialise_student: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    resp = client.put("/resetpassword", json={})
    assert resp.json == {"error": "Insufficient permission to modify this profile"}
    assert resp.status_code == 403


# Student logged in
def test_resetpassword_student_login(setup_test: FlaskClient, initialise_student: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    resp = client.put("/resetpassword", json={})
    assert resp.json == {"error": "Insufficient permission to modify this profile"}
    assert resp.status_code == 403


# Tutor logged in
def test_resetpassword_tutor_login(setup_test: FlaskClient, initialise_tutor: str):
    client = setup_test
    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    resp = client.put("/resetpassword", json={})
    assert resp.json == {"error": "Insufficient permission to modify this profile"}
    assert resp.status_code == 403


# Admin logged in Reset Password Tests
def test_resetpassword_student(
    setup_test: FlaskClient, initialise_admin: str, initialise_student: str
):
    client = setup_test
    client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    # Missing id
    resp = client.put("/resetpassword", json={})
    assert resp.json == {"error": "id field is missing"}
    assert resp.status_code == 400

    # Invalid id
    resp = client.put("/resetpassword", json={"id": "notvalid"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

    # Missing newPassword
    resp = client.put("/resetpassword", json={"id": initialise_student})
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    # Invalid newPassword
    resp = client.put(
        "/resetpassword", json={"id": initialise_student, "newPassword": "1234567"}
    )
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    # New password cannot be the same as the old password
    resp = client.put(
        "/resetpassword", json={"id": initialise_student, "newPassword": "12345678"}
    )
    assert resp.json == {"error": "New password cannot be the same as the old password"}
    assert resp.status_code == 400

    # Successful reset password
    resp = client.put(
        "/resetpassword",
        json={"id": initialise_student, "newPassword": "123456789"},
    )
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    # Test login with new password
    client.post("/logout", json={})
    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "student",
        },
    )
    assert resp.json == {"error": "Invalid login attempt"}

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "123456789",
            "accountType": "student",
        },
    )
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]


# Admin logged in Tutor Reset Password Tests
def test_resetpassword_tutor(
    setup_test: FlaskClient, initialise_admin: str, initialise_tutor: str
):
    client = setup_test
    client.post(
        "/login",
        json={
            "email": "validemail3@mail.com",
            "password": "12345678",
            "accountType": "admin",
        },
    )

    # Missing newPassword
    resp = client.put("/resetpassword", json={"id": initialise_tutor})
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    # Invalid newPassword
    resp = client.put(
        "/resetpassword", json={"id": initialise_tutor, "newPassword": "1234567"}
    )
    assert resp.json == {"error": "password field must be at least 8 characters long"}
    assert resp.status_code == 400

    # New password cannot be the same as the old password
    resp = client.put(
        "/resetpassword", json={"id": initialise_tutor, "newPassword": "12345678"}
    )
    assert resp.json == {"error": "New password cannot be the same as the old password"}
    assert resp.status_code == 400

    # Successful reset password
    resp = client.put(
        "/resetpassword",
        json={"id": initialise_tutor, "newPassword": "123456789"},
    )
    assert resp.json == {"success": True}
    assert resp.status_code == 200

    # Test login with new password
    client.post("/logout", json={})
    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.json == {"error": "Invalid login attempt"}

    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "123456789",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200
    with client.session_transaction() as session:
        assert session["user_id"] == resp.json["id"]
