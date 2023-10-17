from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import Subject, User, Tutor
from datetime import datetime, timedelta


@pytest.fixture
def generate_tutor(generate_dummy_appointment) -> str:
    Subject.prisma().create(data={"name": "science"})
    appointment_id = generate_dummy_appointment[0]()

    id = str(uuid4())
    tutor = User.prisma().create(
        data={
            "id": id,
            "email": "validemail@mail.com",
            "hashedPassword": sha256("12345678".encode()).hexdigest(),
            "name": "Terry",
            "bio": "band 1 at HSC Maths",
            "location": "Australia",
            "profilePicture": None,
            "phoneNumber": "0411123901",
            "tutorInfo": {"create": {"id": id}},
        }
    )

    # separated to keep queries small
    Tutor.prisma().update(
        where={
            "id": id,
        },
        data={
            "appointments": {"connect": {"id": appointment_id}},
            "courseOfferings": {"connect": {"name": "science"}},
            #"timesAvailable": {
                #create": {
                #    "id": "1",
                #   "startTime": datetime.fromisoformat(
                #        "2023-10-14T15:48:26.297000+00:00"
                #    ),
                #    "endTime": datetime.fromisoformat(
                #        "2023-10-14T21:48:26.297000+00:00"
                #    ),
                #}
            #},
            "ratings": {
                "create": {
                    "id": str(uuid4()),
                    "score": 2,
                    "appointment": {
                        "connect": {
                            "id": appointment_id,
                        }
                    },
                }
            },
        },
    )

    return tutor.id

@pytest.fixture
def generate_admin() -> str:
    id = str(uuid4())
    admin = User.prisma().create(
        data={
            "id": id,
            "email":"validemail2@mail.com",
            "hashedPassword": sha256("23456789".encode()).hexdigest(),
            "name": "Admin",
            "adminInfo": {"create": {"id": id}},
        }
    )
    return admin.id


# Get Tutor Profile Tests



def test_get_missing_id(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/tutor/profile/")
    # assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 405


def test_get_nonexisting_profile(setup_test: FlaskClient):
    client = setup_test
    resp = client.get("/tutor/profile/1")
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

def test_get_valid(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutor_id = generate_tutor

    resp = client.get(f"/tutor/profile/{tutor_id}")

    assert resp.status_code == 200
    assert resp.json["id"] == tutor_id
    assert resp.json["email"] == "validemail@mail.com"
    assert resp.json["name"] == "Terry"
    assert resp.json["bio"] == "band 1 at HSC Maths"
    assert resp.json["rating"] == 2
    assert resp.json["location"] == "Australia"
    assert resp.json["profilePicture"] == None
    assert resp.json["phoneNumber"] == "0411123901"
    assert "science" in resp.json["courseOfferings"]
    assert resp.json["timesAvailable"] == []


# Modify Tutor Profile Tests


def test_modify_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.put("/tutor/profile/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


def test_modify_invalid_args(
    setup_test: FlaskClient, generate_tutor: str, generate_admin: str):
    client = setup_test

    tutor_Id = generate_tutor

    # No user logged in
    resp = client.put("/tutor/profile/", json={})
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

    # Non admin user tries modifying other user
    resp = client.put("/tutor/profile/", json={"id": tutor_Id})
    assert resp.json == {"error": "id field should not be supplied by a non admin user"}
    assert resp.status_code == 403

    resp = client.post("/logout")
    assert resp.status_code == 200

    # admin logs in

    generate_admin

    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "23456789",
            "accountType": "admin",
        }
    )
    assert resp.status_code == 200

    # admin tries to modify with giving id param
    resp = client.put("/tutor/profile/", json={})
    assert resp.json == {"error": "id field was missing"}
    assert resp.status_code == 400

    # admin modifies profile that doesnt exist
    resp = client.put("/tutor/profile/", json={"id": "1"})
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404

def test_modify_invalid_email(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test
    tutor_id = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    resp = client.put(
        "/tutor/profile/",
        json={
            "email": "validemailmail.com",
        },
    )
    
    assert resp.status_code == 400
    assert resp.json == {"error": "New email is invalid"}


def test_modify_missing_args(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutor_id = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )

    # missing fields
    resp = client.put("/tutor/profile/", json={})
    assert resp.status_code == 200

    resp = client.get(f"/tutor/profile/{tutor_id}")
    assert resp.status_code == 200
    assert resp.json["id"] == tutor_id
    assert resp.json["email"] == "validemail@mail.com"
    assert resp.json["name"] == "Terry"
    assert resp.json["bio"] == "band 1 at HSC Maths"
    assert resp.json["rating"] == 2
    assert resp.json["location"] == "Australia"
    assert resp.json["profilePicture"] == None
    assert resp.json["phoneNumber"] == "0411123901"
    assert "science" in resp.json["courseOfferings"]
    assert resp.json["timesAvailable"] == []

def test_modify_same_values(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutor_id = generate_tutor

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
            "name": "Terry",
            "bio": "band 1 at HSC Maths",
            "email": "validemail@mail.com",
            "profilePicture": None,
            "location": "Australia",
            "phoneNumber": "0411123901",
            "courseOfferings": ["science"],
            "timesAvailable": []
        },
    )
    assert resp.status_code == 200

    resp = client.get(f"/tutor/profile/{tutor_id}")

    assert resp.status_code == 200
    assert resp.json["id"] == tutor_id
    assert resp.json["email"] == "validemail@mail.com"
    assert resp.json["name"] == "Terry"
    assert resp.json["bio"] == "band 1 at HSC Maths"
    assert resp.json["rating"] == 2
    assert resp.json["location"] == "Australia"
    assert resp.json["profilePicture"] == None
    assert resp.json["phoneNumber"] == "0411123901"
    assert "science" in resp.json["courseOfferings"]
    assert resp.json["timesAvailable"] == []


def test_modify_different_values(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutor_id = generate_tutor

    start_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    end_time = (datetime.utcnow() + timedelta(days=2)).isoformat()

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
            "name": "Juan",
            "bio": "band 6 at HSC Maths",
            "email": "valid@mail.com",
            "profilePicture": "",
            "location": "Sydney",
            "phoneNumber": "0411123888",
            "courseOfferings": ["science", "math"],
            "timesAvailable": [{"startTime": start_time, "endTime": end_time}],
        },
    )
    assert resp.status_code == 200

    resp = client.get(f"/tutor/profile/{tutor_id}")
    assert resp.status_code == 200

    assert resp.json["id"] == tutor_id
    assert resp.json["email"] == "valid@mail.com"
    assert resp.json["name"] == "Juan"
    assert resp.json["bio"] == "band 6 at HSC Maths"
    assert resp.json["rating"] == 2
    assert resp.json["location"] == "Sydney"
    assert resp.json["profilePicture"] == ""
    assert resp.json["phoneNumber"] == "0411123888"
    assert (
        "science" in resp.json["courseOfferings"]
        and "math" in resp.json["courseOfferings"]
    )
    assert len(resp.json["timesAvailable"]) == 1

    print(resp.json["timesAvailable"][0]["startTime"])

    response = datetime.fromisoformat(resp.json["timesAvailable"][0]["startTime"]).replace(tzinfo=None, minute=0, second=0, microsecond=0)
    expected = datetime.fromisoformat(start_time).replace(minute=0, second=0, microsecond=0)
    assert response == expected

    response = datetime.fromisoformat(resp.json["timesAvailable"][0]["endTime"]).replace(tzinfo=None, minute=0, second=0, microsecond=0)
    expected = datetime.fromisoformat(end_time).replace(minute=0, second=0, microsecond=0)
    assert response == expected

# Delete Profile Tests


def test_delete_not_json(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/tutor/")
    assert resp.json == {"error": "content-type was not json or data was malformed"}
    assert resp.status_code == 415


def test_delete_no_user(setup_test: FlaskClient):
    client = setup_test
    resp = client.delete("/tutor/", json={})
    assert resp.json == {"error": "No user is logged in"}
    assert resp.status_code == 400


def test_delete_permission(
    setup_test: FlaskClient, generate_tutor: str):

    tutor_id = generate_tutor
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

    resp = client.delete("/tutor/", json={"id": tutor_id})

    assert resp.json == {"error": "id field should not be supplied by a non admin user"}
    assert resp.status_code == 403

def test_delete_nonexisting_profile(
        setup_test: FlaskClient, generate_admin: str):
    
    client = setup_test
    admin_id = generate_admin

    resp = client.post(
        "/login",
        json={
            "email": "validemail2@mail.com",
            "password": "23456789",
            "accountType": "admin",
        }
    )
    assert resp.status_code == 200

    resp = client.delete("/tutor/", json={"id": "1"})
    assert resp.status_code == 404
    assert resp.json == {"error": "Profile does not exist"}
    


def test_delete_valid(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test

    tutor_id = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200

    resp = client.delete("/tutor/", json={})
    assert resp.status_code == 200

    resp = client.get(f"/tutor/profile/{tutor_id}")
    assert resp.json == {"error": "Profile does not exist"}
    assert resp.status_code == 404


def test_modify_time_available(setup_test: FlaskClient, generate_tutor: str):
    client = setup_test
    tutor_id = generate_tutor

    resp = client.post(
        "/login",
        json={
            "email": "validemail@mail.com",
            "password": "12345678",
            "accountType": "tutor",
        },
    )
    assert resp.status_code == 200
    # valid modification
    resp = client.put(
        "/tutor/profile/",
        json={
            "timesAvailable": [
                {
                    "startTime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "endTime": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                },
                {
                    "startTime": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                    "endTime": (datetime.utcnow() + timedelta(days=4)).isoformat(),
                },
            ],
        },
    )
    assert resp.status_code == 200

    # overlapping time availabilities
    resp = client.put(
        "/tutor/profile/",
        json={
            "timesAvailable": [
                {
                    "startTime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "endTime": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                },
                {
                    "startTime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "endTime": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                },
            ],
        },
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "Time availabilities should not overlap"

    resp = client.get(f"/tutor/profile/{tutor_id}")
    assert resp.status_code == 200
    assert len(resp.json["timesAvailable"]) == 2
