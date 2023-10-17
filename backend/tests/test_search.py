import pytest
from flask.testing import FlaskClient
from prisma.models import Subject, User, Tutor
from uuid import uuid4
import datetime
import json


@pytest.fixture
def generate_tutors(generate_dummy_appointment) -> None:
    Subject.prisma().create(data={"name": "math"})
    Subject.prisma().create(data={"name": "science"})

    # * irrelevant information are left empty
    apt_id1 = generate_dummy_appointment[0]()
    User.prisma().create(
        data={
            "id": "tutorId1",
            "email": "mail@gmail.com",
            "hashedPassword": "12345678",
            "name": "James",
            "location": "Australia",
            "tutorInfo": {
                "create": {"id": "tutorId1"},
            },
        },
    )
    Tutor.prisma().update(
        where={
            "id": "tutorId1",
        },
        data={
            "appointments": {"connect": {"id": apt_id1}},
            "courseOfferings": {"connect": {"name": "math"}},
            "ratings": {
                "create": {
                    "id": str(uuid4()),
                    "score": 2,
                    "appointment": {"connect": {"id": apt_id1}},
                }
            },
        },
    )

    apt_id2 = generate_dummy_appointment[0]()
    User.prisma().create(
        data={
            "id": "tutorId2",
            "email": "mail2@gmail.com",
            "hashedPassword": "12345678",
            "name": "Jan",
            "location": "Tasmania",
            "tutorInfo": {"create": {"id": "tutorId2"}},
        },
    )
    Tutor.prisma().update(
        where={
            "id": "tutorId2",
        },
        data={
            "appointments": {"connect": {"id": apt_id2}},
            "courseOfferings": {"connect": {"name": "science"}},
            "timesAvailable": {
                "create": {
                    "id": "1",
                    "startTime": datetime.datetime.now()
                    + datetime.timedelta(days=4, hours=0),
                    "endTime": datetime.datetime.now()
                    + datetime.timedelta(days=4, hours=6),
                }
            },
            "ratings": {
                "create": {
                    "id": str(uuid4()),
                    "score": 4,
                    "appointment": {"connect": {"id": apt_id2}},
                }
            },
        },
    )

    f, dummy_tutor_id, _ = generate_dummy_appointment
    apt_id3 = f()
    User.prisma().create(
        data={
            "id": "tutorId3",
            "email": "mail3@gmail.com",
            "hashedPassword": "12345678",
            "name": "John",
            "location": "Tasmania",
            "tutorInfo": {"create": {"id": "tutorId3"}},
        },
    )
    Tutor.prisma().update(
        where={
            "id": "tutorId3",
        },
        data={
            "appointments": {"connect": {"id": apt_id3}},
            "courseOfferings": {"connect": [{"name": "science"}, {"name": "math"}]},
            "timesAvailable": {
                "create": {
                    "id": "2",
                    "startTime": datetime.datetime.now()
                    + datetime.timedelta(days=3, hours=0),
                    "endTime": datetime.datetime.now()
                    + datetime.timedelta(days=3, hours=6),
                }
            },
            "ratings": {
                "create": {
                    "id": str(uuid4()),
                    "score": 3,
                    "appointment": {"connect": {"id": apt_id3}},
                }
            },
        },
    )
    # removing the dummy tutor from the db so it doesn't impact
    # test results
    User.prisma().delete(where={"id": dummy_tutor_id})
    assert Tutor.prisma().count() == 3

    return None


def test_search_no_args(setup_test: FlaskClient, generate_tutors):
    client = setup_test
    resp = client.get("/searchtutor", query_string={})
    assert "tutorIds" in resp.json
    assert len(resp.json["tutorIds"]) == 3
    assert resp.status_code == 200

    assert all(
        id in ["tutorId1", "tutorId2", "tutorId3"] for id in resp.json["tutorIds"]
    )


def test_search_only_name(setup_test: FlaskClient, generate_tutors):
    client = setup_test
    # only name
    resp = client.get("/searchtutor", query_string={"name": "James"})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    assert resp.json["tutorIds"][0] == "tutorId1"


def test_search_only_location(setup_test: FlaskClient, generate_tutors):
    client = setup_test

    # only location
    resp = client.get("/searchtutor", query_string={"location": "Tasmania"})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    assert all(id in ["tutorId2", "tutorId3"] for id in resp.json["tutorIds"])
    resp = client.get("/searchtutor", query_string={"location": "Australia"})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    assert resp.json["tutorIds"][0] == "tutorId1"


def test_search_only_ratings(setup_test: FlaskClient, generate_tutors):
    client = setup_test

    # only rating
    resp = client.get("/searchtutor", query_string={"rating": 2})
    assert len(resp.json["tutorIds"]) == 3
    assert resp.status_code == 200
    assert all(
        id in ["tutorId1", "tutorId2", "tutorId3"] for id in resp.json["tutorIds"]
    )

    resp = client.get("/searchtutor", query_string={"rating": 3})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    resp = client.get("/searchtutor", query_string={"rating": 4})
    assert len(resp.json["tutorIds"]) == 1
    assert resp.status_code == 200
    assert resp.json["tutorIds"][0] == "tutorId2"


def test_search_only_course_offerings(setup_test: FlaskClient, generate_tutors):
    client = setup_test

    # only courseOfferings
    resp = client.get("/searchtutor", query_string={"courseOfferings": ["math"]})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    assert all(id in ["tutorId1", "tutorId3"] for id in resp.json["tutorIds"])
    resp = client.get("/searchtutor", query_string={"courseOfferings": ["science"]})
    assert len(resp.json["tutorIds"]) == 2
    assert resp.status_code == 200
    assert all(id in ["tutorId2", "tutorId3"] for id in resp.json["tutorIds"])
    resp = client.get(
        "/searchtutor", query_string={"courseOfferings": ["math", "science"]}
    )
    assert len(resp.json["tutorIds"]) == 3
    assert resp.status_code == 200
    assert all(
        id in ["tutorId1", "tutorId2", "tutorId3"] for id in resp.json["tutorIds"]
    )


def test_search_only_time_range(setup_test: FlaskClient, generate_tutors):
    client = setup_test

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
    assert all(id in ["tutorId2", "tutorId3"] for id in resp.json["tutorIds"])

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
    assert resp.json["tutorIds"][0] == "tutorId3"


def test_search_args(setup_test: FlaskClient, generate_tutors):
    client = setup_test

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
    assert resp.json["tutorIds"][0] == "tutorId3"
