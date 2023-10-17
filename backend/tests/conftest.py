import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from hashlib import sha256
from uuid import uuid4
from flask.testing import FlaskClient
from prisma.cli import prisma
import prisma.models as models
import subprocess
import sys
import os
from pathlib import Path

# unused import for mocking purposes during tests
from prisma.actions import UserActions, TutorActions, SubjectActions

# hack to import a root level file and be able to run pytest from any dir
# source: https://www.geeksforgeeks.org/python-import-from-parent-directory/
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from app import app

# basic testing utils ##########################################################


@pytest.fixture
def setup_test():
    return app.test_client()


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield None
    # check is probably unnecssary, but better to be safe than sorry
    if Path.cwd().parts[-1] == "tests" and (Path.cwd() / "flask_session").is_dir():
        subprocess.run(["rm", "-rf", "flask_session"])


# ? Probably no longer necessary due to additional of mocking
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


# mocks / fake data ############################################################


@pytest.fixture
def find_unique_users_mock(mocker: MockerFixture) -> MockType:
    return mocker.patch("tests.conftest.UserActions.find_unique")


@pytest.fixture
def find_many_tutors_mock(mocker: MockerFixture) -> MockType:
    return mocker.patch("tests.conftest.TutorActions.find_many")


@pytest.fixture
def fake_user():
    def __fake_user(email: str, pword: str, type: str) -> models.User:
        id = str(uuid4())
        match type.lower():
            case "student":
                user = models.User(
                    id=id,
                    name="name",
                    email=email,
                    hashedPassword=sha256(pword.encode()).hexdigest(),
                    studentInfo=models.Student(id=id, userInfoId=id),
                )
                return user
            case "tutor":
                return models.User(
                    id=id,
                    name="name",
                    email=email,
                    hashedPassword=sha256(pword.encode()).hexdigest(),
                    tutorInfo=models.Tutor(id=id, userInfoId=id),
                )
            case "admin":
                return models.User(
                    id=id,
                    name="name",
                    email=email,
                    hashedPassword=sha256(pword.encode()).hexdigest(),
                    adminInfo=models.Admin(id=id, userInfoId=id),
                )
            case _:
                return models.User(
                    id=id, name="name", email=email, hashedPassword=pword
                )

    return __fake_user


@pytest.fixture
def fake_student(fake_user) -> models.User:
    return fake_user("validemail@mail.com", "12345678", "student")


@pytest.fixture
def fake_tutor(fake_user) -> models.User:
    return fake_user("validemail2@mail.com", "12345678", "tutor")


@pytest.fixture
def fake_admin(fake_user) -> models.User:
    return fake_user("validemail3@mail.com", "12345678", "admin")
