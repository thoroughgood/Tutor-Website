from flask.testing import FlaskClient
import pytest
from prisma.cli import prisma
from prisma import Prisma
import prisma.models as models
import sys
import subprocess
from pathlib import Path

# Little hack to allow easy importing from parent
# Courtesy of https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder/28712742#28712742
# ? Probably more idiomatic/less hacky way of doing this
sys.path.insert(0, "..")
from backend.app import app


@pytest.fixture
def setup_test():
    # to reset the test_db and update test schema if necessary
    prisma.run(["db", "push", "--force-reset"], check=True)
    # * The below is needed if app is not imported
    # db = Prisma(auto_register=True)
    # db.connect()
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
