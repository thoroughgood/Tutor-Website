from hashlib import sha256
from uuid import uuid4
import pytest
from flask.testing import FlaskClient
from prisma.models import Tutor, Subject
import datetime


@pytest.fixture
def generate_tutor() -> str:
    Subject.prisma().create(data={"name": "science"})
    Subject.prisma().create(data={"name": "math"})

    tutor = Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "validemail@mail.com",
            "hashedPassword": "12345678",
            "name": "Terry",
            "bio": "band 1 at HSC Maths",
            "location": "Australia",
            # "rating": {"create": {"id": str(uuid4()), "score": 2, "createdById": ""}},
            "profilePicture": "",
            "phoneNumber": "0411123901",
            "courseOfferings": {"connect": {"name": "science"}},
            "timesAvailable": {
                "create": {
                    "id": "1",
                    "startTime": datetime.datetime.utcnow()
                    + datetime.timedelta(days=4, hours=0),
                    "endTime": datetime.datetime.utcnow()
                    + datetime.timedelta(days=4, hours=6),
                }
            },
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

    tutor = Tutor.prisma().find_unique(
        where={"id": tutorId},
        include={
            "courseOfferings": {"include": {"tutorsTeaching": True}},
            "timesAvailable": True,
        },
    )

    assert resp.status_code == 200

    print(resp.json["id"])

    assert resp.json["id"] == tutor.id
    assert resp.json["name"] == tutor.name
    assert resp.json["bio"] == tutor.bio
    assert resp.json["email"] == tutor.email
    assert resp.json["rating"] == tutor.rating
    assert resp.json["profilePicture"] == tutor.profilePicture
    assert resp.json["location"] == tutor.location
    assert resp.json["phoneNumber"] == tutor.phoneNumber
    assert resp.json["courseOfferings"] == list(
        map(formatCourseOfferings, tutor.courseOfferings)
    )
    assert resp.json["timesAvailable"] == list(
        map(formatTimesAvailable, tutor.timesAvailable)
    )


def formatCourseOfferings(subject):
    return subject.name


def formatTimesAvailable(timeBlock):
    return {
        "startTime": timeBlock.startTime.isoformat(),
        "endTime": timeBlock.endTime.isoformat(),
    }
