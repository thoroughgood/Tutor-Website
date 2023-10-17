from hashlib import sha256
from uuid import uuid4
from flask.testing import FlaskClient
import pytest
from prisma.cli import prisma
import prisma.models as models
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Little hack to allow easy importing from parent
# Courtesy of https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder/28712742#28712742
# ? Probably more idiomatic/less hacky way of doing this
sys.path.insert(0, "..")
from app import app

# basic testing utils


@pytest.fixture
def setup_test():
    # to reset the test_db and update test schema if necessary
    prisma.run(["db", "push", "--force-reset"], check=True)
    yield app.test_client()


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield None
    # check is probably unnecssary, but better to be safe than sorry
    if Path.cwd().parts[-1] == "tests" and (Path.cwd() / "flask_session").is_dir():
        subprocess.run(["rm", "-rf", "flask_session"])


def test_setup_test_db(setup_test):
    try:
        # check that all tables are empty
        assert models.Admin.prisma().count() == 0
        assert models.Student.prisma().count() == 0
        assert models.Tutor.prisma().count() == 0
        assert models.Subject.prisma().count() == 0
        assert models.TutorAvailability.prisma().count() == 0
        assert models.Rating.prisma().count() == 0
        assert models.Appointment.prisma().count() == 0
    except prisma.errors.ClientNotRegisteredError:
        assert False, "Model Based Access is not functional"


def test_setup_test_client(setup_test: FlaskClient):
    client = setup_test
    response = client.get("/")
    assert response.data == b"Hello world!"
    assert response.status_code == 200


# dummy data generation


@pytest.fixture
def generate_dummy_tutor() -> str:
    id = str(uuid4())
    tutor = models.User.prisma().create(
        data={
            "id": id,
            "email": "dummytutor@mail.com",
            "name": "dummy",
            "hashedPassword": sha256("dfknsdkjd".encode()).hexdigest(),
            "bio": "",
            "location": None,
            "profilePicture": None,
            "phoneNumber": None,
            "tutorInfo": {"create": {"id": id}},
        }
    )

    return tutor.id


@pytest.fixture
def generate_dummy_student() -> str:
    id = str(uuid4())
    models.User.prisma().create(
        data={
            "id": id,
            "email": "dummystudent@mail.com",
            "name": "dummy",
            "hashedPassword": sha256("dwadwawfgaw".encode()).hexdigest(),
            "bio": "",
            "location": None,
            "profilePicture": None,
            "phoneNumber": None,
            "studentInfo": {"create": {"id": id}},
        }
    )

    return id


# Caution: this factory function has the side effect of generating a new tutor
# and student once and shares them with every generation of an appointment
# i.e. all apppointments generated are connected to the same student and tutor
# For convenience, the value of the ids of these users are returned
# alongside the factory function in a tuple.
@pytest.fixture
def generate_dummy_appointment(generate_dummy_tutor, generate_dummy_student):
    def __generate_dummy_appointment() -> str:
        id = str(uuid4())
        models.Appointment.prisma().create(
            data={
                "id": id,
                "startTime": datetime.now(),
                "endTime": datetime.now(),
                "student": {"connect": {"id": generate_dummy_student}},
                "tutor": {"connect": {"id": generate_dummy_tutor}},
            }
        )

        return id

    return (
        __generate_dummy_appointment,  # factory function
        generate_dummy_tutor,  # tutor_id
        generate_dummy_student,  # student_id
    )
