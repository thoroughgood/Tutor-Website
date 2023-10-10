from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import Tutor, Subject, Admin
from datetime import datetime


@pytest.fixture
def generate_tutor() -> str:
    Subject.prisma().create(data={"name": "science"})
    Subject.prisma().create(data={"name": "math"})

    tutor = Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Terry",
            "bio": "band 1 at HSC Maths",
            "location": "Australia",
            "rating": {"create": {"id": str(uuid4()), "score": 2, "createdById": ""}},
            "profilePicture": None,
            "phoneNumber": "0411123901",
            "courseOfferings": {"connect": {"name": "science"}},
            "timesAvailable": {
                "create": {
                    "id": "1",
                    "startTime": datetime.fromisoformat(
                        "2023-10-14T15:48:26.297000+00:00"
                    ),
                    "endTime": datetime.fromisoformat(
                        "2023-10-14T21:48:26.297000+00:00"
                    ),
                }
            },
        }
    )

    return tutor.id


@pytest.fixture
def generate_dummy_tutor() -> str:
    tutor = Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "dummy@mail.com",
            "name": "dummy",
            "hashedPassword": sha256("dfknsdkjd".encode()).hexdigest(),
            "bio": "",
            "location": None,
            "profilePicture": None,
            "phoneNumber": None,
            "courseOfferings": {},
            "timesAvailable": {},
        }
    )

    return tutor.id


# Get Tutor Profile Tests


def test_get_no_query(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/tutor/profile/")
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400


def test_get_nonexisting_profile(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/tutor/profile/", query_string={"id": "1"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404


def test_get_empty_id(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/tutor/profile/", query_string={"id": ""})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400


def test_get_valid(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutorId = generate_tutor
    resp = client.get("/tutor/profile/", query_string={"id": tutorId})

    assert resp.status_code == 200

    assert resp.json == {
        "id": tutorId,
        "email": "validemail@mail.com",
        "name": "Terry",
        "bio": "band 1 at HSC Maths",
        "rating": [2],
        "location": "Australia",
        "profilePicture": None,
        "phoneNumber": "0411123901",
        "courseOfferings": ["science"],
        "timesAvailable": [
            {
                "startTime": "2023-10-14T15:48:26.297000+00:00",
                "endTime": "2023-10-14T21:48:26.297000+00:00",
            }
        ],
    }


# Modify Tutor Profile Tests


def test_modify_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.put("/tutor/profile/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


def test_modify_invalid_args(
    setup_test: FlaskClient, generate_tutor: str, generate_dummy_tutor: str
):
    client = setup_test

    tutorId = generate_tutor

    # No user logged in
    resp = client.put("/tutor/profile/", json={"id": tutorId})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 400

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    assert resp.status_code == 200

    # User doesnt have permission to modify profile
    resp = client.put("/tutor/profile/", json={"id": generate_dummy_tutor})
    assert resp.json == {"error": "Insufficient permission to modify this profile"}
    assert resp.status_code == 403

    # need admin implemented
    # profile doesnt exist
    # resp = client.put("/tutor/profile/", json={"id": "1"})
    # assert resp.json == {"error": "Profile does not exist"}
    # assert resp.status_code == 404


def test_modify_missing_args(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutorId = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    # missing fields
    resp = client.put("/tutor/profile/", json={"id": tutorId})
    assert resp.status_code == 200

    resp = client.get("/tutor/profile/", query_string={"id": tutorId})
    assert resp.status_code == 200
    assert resp.json == {
        "id": tutorId,
        "email": "validemail@mail.com",
        "name": "Terry",
        "bio": "band 1 at HSC Maths",
        "rating": [2],
        "location": "Australia",
        "profilePicture": None,
        "phoneNumber": "0411123901",
        "courseOfferings": ["science"],
        "timesAvailable": [
            {
                "startTime": "2023-10-14T15:48:26.297000+00:00",
                "endTime": "2023-10-14T21:48:26.297000+00:00",
            }
        ],
    }


def test_modify_same_values(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutorId = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    assert resp.status_code == 200

    # same values in fields
    resp = client.put(
        "/tutor/profile/",
        json={
            "id": tutorId,
            "name": "Terry",
            "bio": "band 1 at HSC Maths",
            "email": "validemail@mail.com",
            "profilePicture": None,
            "location": "Australia",
            "phoneNumber": "0411123901",
            "courseOfferings": ["science"],
            "timesAvailable": [
                {
                    "startTime": "2023-10-14T15:48:26.297000+00:00",
                    "endTime": "2023-10-14T21:48:26.297000+00:00",
                }
            ],
        },
    )

    assert resp.status_code == 200

    resp = client.get("/tutor/profile/", query_string={"id": tutorId})

    assert resp.status_code == 200

    assert resp.json == {
        "id": tutorId,
        "email": "validemail@mail.com",
        "name": "Terry",
        "bio": "band 1 at HSC Maths",
        "rating": [2],
        "location": "Australia",
        "profilePicture": None,
        "phoneNumber": "0411123901",
        "courseOfferings": ["science"],
        "timesAvailable": [
            {
                "startTime": "2023-10-14T15:48:26.297000+00:00",
                "endTime": "2023-10-14T21:48:26.297000+00:00",
            }
        ],
    }


def test_modify_different_values(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutorId = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    assert resp.status_code == 200

    resp = client.put(
        "/tutor/profile/",
        json={
            "id": tutorId,
            "name": "Juan",
            "bio": "band 6 at HSC Maths",
            "email": "valid@mail.com",
            "profilePicture": "",
            "location": "Sydney",
            "phoneNumber": "0411123888",
            "courseOfferings": ["science", "math"],
            "timesAvailable": [],
        },
    )
    assert resp.status_code == 200

    resp = client.get("/tutor/profile/", query_string={"id": tutorId})
    assert resp.status_code == 200

    assert resp.json == {
        "id": tutorId,
        "name": "Juan",
        "bio": "band 6 at HSC Maths",
        "email": "valid@mail.com",
        "rating": [2],
        "profilePicture": "",
        "location": "Sydney",
        "phoneNumber": "0411123888",
        "courseOfferings": ["science", "math"],
        "timesAvailable": [],
    }


# Delete Profile Tests


def test_delete_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/tutor/profile/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


def test_delete_no_user(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/tutor/profile/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 400


def test_delete_invalid_arg(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200

    resp = client.delete("/tutor/profile/", json={"id": ""})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400


def test_delete_permission(
    setup_test: FlaskClient, generate_dummy_tutor: str, generate_tutor: str
):
    client = setup_test

    dummyId = generate_dummy_tutor
    tutorId = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200

    resp = client.delete("/tutor/profile/", json={"id": generate_dummy_tutor})

    assert resp.json == {"error": "Insufficient permission to delete this profile"}
    assert resp.status_code == 403


def test_delete_valid(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutorId = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200

    resp = client.delete("/tutor/profile/", json={"id": tutorId})
    assert resp.status_code == 200

    resp = client.get("/tutor/profile/", query_string={"id": tutorId})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404
