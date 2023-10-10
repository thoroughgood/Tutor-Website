import pytest
from flask.testing import FlaskClient
from prisma.models import Tutor, Subject, User
from uuid import uuid4
import datetime
import json


@pytest.fixture
def generate_tutors() -> None:
    Subject.prisma().create(data={"name": "math"})
    Subject.prisma().create(data={"name": "science"})

    # * irrelevant information are left empty
    tutorId1 = str(uuid4())
    User.prisma().create(
        data={
            "id": tutorId1,
            "email": "mail@gmail.com",
            "hashedPassword": "12345678",
            "name": "James",
            "location": "Australia",
            "tutorInfo": {
                "create": {
                    "id": tutorId1,
                    "rating": {
                        "create": {"id": str(uuid4()), "score": 2, "createdById": ""}
                    },
                    "courseOfferings": {"connect": {"name": "math"}},
                }
            },
        },
    )
    tutorId2 = str(uuid4())
    User.prisma().create(
        data={
            "id": tutorId2,
            "email": "mail2@gmail.com",
            "hashedPassword": "12345678",
            "name": "Jan",
            "location": "Tasmania",
            "tutorInfo": {
                "create": {
                    "id": tutorId2,
                    "rating": {
                        "create": {"id": str(uuid4()), "score": 4, "createdById": ""}
                    },
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
            },
        },
    )
    tutorId3 = str(uuid4())
    User.prisma().create(
        data={
            "id": tutorId3,
            "email": "mail3@gmail.com",
            "hashedPassword": "12345678",
            "name": "John",
            "location": "Tasmania",
            "tutorInfo": {
                "create": {
                    "id": tutorId3,
                    "rating": {
                        "create": {"id": str(uuid4()), "score": 3, "createdById": ""}
                    },
                    "courseOfferings": {
                        "connect": [{"name": "science"}, {"name": "math"}]
                    },
                    "timesAvailable": {
                        "create": {
                            "id": "2",
                            "startTime": datetime.datetime.utcnow()
                            + datetime.timedelta(days=3, hours=0),
                            "endTime": datetime.datetime.utcnow()
                            + datetime.timedelta(days=3, hours=6),
                        }
                    },
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

    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # tutor3 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][2]})
    # assert set([tutor1.name, tutor2.name, tutor3.name]) == set(["James", "Jan", "John"])


def test_search_args(setup_test: FlaskClient, generate_tutors):
    client = setup_test

    # only name
    resp = client.get("/searchtutor", query_string={"name": "James"})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    # assert (
    #     Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]}).name
    #     == "James"
    # )

    # only location
    resp = client.get("/searchtutor", query_string={"location": "Tasmania"})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])
    resp = client.get("/searchtutor", query_string={"location": "Australia"})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # assert tutor1.name == "James"

    # only rating
    resp = client.get("/searchtutor", query_string={"rating": 2})
    assert len(resp.json["tutorIds"]) == 3
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # tutor3 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][2]})
    # assert set([tutor1.name, tutor2.name, tutor3.name]) == set(["James", "Jan", "John"])
    resp = client.get("/searchtutor", query_string={"rating": 3})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])
    resp = client.get("/searchtutor", query_string={"rating": 4})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # assert tutor1.name == "Jan"

    # only courseOfferings
    resp = client.get("/searchtutor", query_string={"courseOfferings": ["math"]})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # assert set([tutor1.name, tutor2.name]) == set(["James", "John"])
    resp = client.get("/searchtutor", query_string={"courseOfferings": ["science"]})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])
    resp = client.get(
        "/searchtutor", query_string={"courseOfferings": ["math", "science"]}
    )
    assert len(resp.json["tutorIds"]) == 3
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # tutor3 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][2]})
    # assert set([tutor1.name, tutor2.name, tutor3.name]) == set(["James", "Jan", "John"])

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
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # tutor2 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][1]})
    # assert set([tutor1.name, tutor2.name]) == set(["Jan", "John"])

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
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # assert tutor1.name == "John"

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
    assert resp.status_code == 200
    # tutor1 = Tutor.prisma().find_first(where={"id": resp.json["tutorIds"][0]})
    # assert tutor1.name == "John"
