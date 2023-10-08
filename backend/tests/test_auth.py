import pytest
from flask.testing import FlaskClient
from prisma.models import Tutor, Student


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
