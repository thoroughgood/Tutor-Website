import pytest
from flask.testing import FlaskClient
from prisma.models import Tutor, Subject
from uuid import uuid4
import datetime
import json


@pytest.fixture
def generate_tutors() -> None:
    Subject.prisma().create(data={"name": "math"})
    Subject.prisma().create(data={"name": "science"})

    # * irrelevant information are left empty
    Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "mail@gmail.com",
            "hashedPassword": "12345678",
            "name": "James",
            "bio": "",
            "rating": {"create": {"id": str(uuid4()), "score": 2, "createdById": ""}},
            "location": "Australia",
            "courseOfferings": {"connect": {"name": "math"}},
        },
    )
    Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "mail2@gmail.com",
            "hashedPassword": "12345678",
            "name": "Jan",
            "bio": "",
            "rating": {"create": {"id": str(uuid4()), "score": 4, "createdById": ""}},
            "location": "Tasmania",
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
        },
    )
    Tutor.prisma().create(
        data={
            "id": str(uuid4()),
            "email": "mail3@gmail.com",
            "hashedPassword": "12345678",
            "name": "John",
            "bio": "",
            "rating": {"create": {"id": str(uuid4()), "score": 3, "createdById": ""}},
            "location": "Tasmania",
            "courseOfferings": {"connect": [{"name": "science"}, {"name": "math"}]},
            "timesAvailable": {
                "create": {
                    "id": "2",
                    "startTime": datetime.datetime.utcnow()
                    + datetime.timedelta(days=3, hours=0),
                    "endTime": datetime.datetime.utcnow()
                    + datetime.timedelta(days=3, hours=6),
                }
            },
        },
    )
    return None


def test_search_no_args(setup_test: FlaskClient, generate_tutors):
    client = setup_test
    resp = client.get("/searchtutor", query_string={})
    assert "tutorIds" in resp.json
    assert len(resp.json["tutorIds"]) == 3
    assert resp.status_code == 200

    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    tutor3 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][2]})
    assert set([tutor1.name, tutor2.name, tutor3.name]) == set(["James", "Jan", "John"])


def test_search_args(setup_test: FlaskClient, generate_tutors):
    client = setup_test

    # only name
    resp = client.get("/searchtutor", query_string={"name": "James"})
    assert len(resp.json["tutorIds"]) == 1
    assert (
        Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]}).name
        == "James"
    )
    assert resp.status_code == 200

    # only location
    resp = client.get("/searchtutor", query_string={"location": "Tasmania"})
    assert len(resp.json["tutorIds"]) == 2
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])
    assert resp.status_code == 200
    resp = client.get("/searchtutor", query_string={"location": "Australia"})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    assert tutor1.name == "James"

    # only rating
    resp = client.get("/searchtutor", query_string={"rating": 2})
    assert len(resp.json["tutorIds"]) == 3
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    tutor3 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][2]})
    assert set([tutor1.name, tutor2.name, tutor3.name]) == set(["James", "Jan", "John"])
    assert resp.status_code == 200
    resp = client.get("/searchtutor", query_string={"rating": 3})
    assert len(resp.json["tutorIds"]) == 2
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])
    assert resp.status_code == 200
    resp = client.get("/searchtutor", query_string={"rating": 4})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    assert tutor1.name == "Jan"

    # only courseOfferings
    resp = client.get("/searchtutor", query_string={"courseOfferings": ["math"]})
    assert len(resp.json["tutorIds"]) == 1
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    assert tutor1.name == "James"
    assert resp.status_code == 200
    resp = client.get("/searchtutor", query_string={"courseOfferings": ["science"]})
    assert len(resp.json["tutorIds"]) == 1
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    assert tutor1.name == "Jan"
    assert resp.status_code == 200
    resp = client.get(
        "/searchtutor", query_string={"courseOfferings": ["math", "science"]}
    )
    assert len(resp.json["tutorIds"]) == 3
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    tutor1.name == "John"
    assert resp.status_code == 200

    # only timeRange
    resp = client.get(
        "/searchtutor",
        query_string={
            "timeRange": json.dumps(
                {
                    "startTime": (
                        datetime.datetime.now() + datetime.timedelta(hours=1)
                    ).isoformat(),
                    "endTime": (
                        datetime.datetime.now() + datetime.timedelta(days=10)
                    ).isoformat(),
                }
            )
        },
    )
    assert len(resp.json["tutorIds"]) == 2
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])
    assert resp.status_code == 200

    resp = client.get(
        "/searchtutor",
        query_string={
            "timeRange": json.dumps(
                {
                    "startTime": (
                        datetime.datetime.now() + datetime.timedelta(hours=1)
                    ).isoformat(),
                    "endTime": (
                        datetime.datetime.now() + datetime.timedelta(days=3, hours=10)
                    ).isoformat(),
                }
            )
        },
    )
    assert len(resp.json["tutorIds"]) == 1
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    assert tutor1.name == "John"
    assert resp.status_code == 200

    # all excluding name
    resp = client.get(
        "/searchtutor",
        query_string={
            "rating": 3,
            "location": "Tasmania",
            "courseOfferings": ["science", "math"],
            "timeRange": json.dumps(
                {
                    "startTime": (
                        datetime.datetime.now() + datetime.timedelta(hours=1)
                    ).isoformat(),
                    "endTime": (
                        datetime.datetime.now() + datetime.timedelta(days=3, hours=10)
                    ).isoformat(),
                }
            ),
        },
    )
    assert len(resp.json["tutorIds"]) == 1
    tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    assert tutor1.name == "John"
    assert resp.status_code == 200
