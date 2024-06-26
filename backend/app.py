from hashlib import sha256
from uuid import uuid4
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from prisma import Prisma
from pusher import Pusher
import logging
import os

from blueprints.auth import auth
from blueprints.tutor import tutor
from blueprints.student import student
from blueprints.search import search_tutor
from blueprints.appointment import appointment
from blueprints.appointments import appointments
from blueprints.admin import admin
from blueprints.document import document
from blueprints.direct_message import direct_message
from blueprints.tutorial import tutorial
from blueprints.notifications import notifications
from blueprints.utils import utils
from helpers.my_request import MyRequest


Flask.request_class = MyRequest
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", default="secret")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

# Extensions
server_session = Session(app)
cors = CORS(app, supports_credentials=True)

# We'll just say these external clients are 'extensions' of flask
# Note: definitely not idiomatic!
# Prisma
prisma = Prisma(auto_register=True)
prisma.connect()
app.extensions["prisma"] = prisma
# Pusher
app.extensions["pusher"] = Pusher(
    app_id=os.getenv("PUSHER_APP_ID"),
    key=os.getenv("PUSHER_KEY"),
    secret=os.getenv("PUSHER_SECRET"),
    cluster=os.getenv("PUSHER_CLUSTER"),
)

# add a 'super admin' if one isn't already added
if (
    prisma.admin.count() == 0
    and prisma.admin.find_first(where={"userInfo": {"is": {"name": "SuperAdmin"}}})
    is None
):
    id = str(uuid4())
    prisma.user.create(
        data={
            "id": id,
            "name": "SuperAdmin",
            # ? Maybe have this correspond to an actual email later
            "email": "admin@email.com",
            # ? Some way to generate a new password each run?
            "hashedPassword": sha256("password".encode()).hexdigest(),
            "adminInfo": {"create": {"id": id}},
        }
    )

# blueprints
app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(tutor, url_prefix="/tutor")
app.register_blueprint(student, url_prefix="/student")
app.register_blueprint(search_tutor, url_prefix="/")
app.register_blueprint(appointment, url_prefix="/appointment")
app.register_blueprint(appointments, url_prefix="/appointments")
app.register_blueprint(utils, url_prefix="/utils")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(notifications, url_prefix="/notifications")
app.register_blueprint(document, url_prefix="/document")
app.register_blueprint(direct_message, url_prefix="/directmessage")
app.register_blueprint(tutorial, url_prefix="/tutorial")


# default route
@app.route("/")
def hello_world():
    return "Hello world!", 200


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=8000), host="0.0.0.0")
    prisma.disconnect()
else:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
