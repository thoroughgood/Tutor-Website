from uuid import uuid4
import pytest
from datetime import datetime
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from flask.testing import FlaskClient
from prisma.models import Appointment


@pytest.fixture
def generate_appointment(fake_tutor, fake_student):
    apt = Appointment(
        id=str(uuid4()),
        startTime=datetime.now(),
        endTime=datetime.now(),
        tutorAccepted=False,
        tutor=fake_tutor.tutorInfo,
        tutorId=fake_tutor.id,
        student=fake_student.studentInfo,
        studentId=fake_student.id,
    )

    return apt


########################### APPOINTMENT ACCEPT TESTS ###########################


def test_appointment_accept_no_user_login(setup_test: FlaskClient):
    pass
