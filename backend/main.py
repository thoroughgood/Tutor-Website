from flask import Flask
from flask_session import Session
from flask_cors import CORS
from prisma import Prisma
import os

from blueprints.example import example
from blueprints.auth import auth, register, login, logout
from helpers.my_request import MyRequest

prisma = Prisma(auto_register=True)
prisma.connect()

Flask.request_class = MyRequest
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", default="not very secret")
# ? Consider moving to redis in the future?
app.config["SESSION_TYPE"] = "filesystem"
server_session = Session(app)
# todo: figure cors
cors = CORS(app)

# blueprints
app.register_blueprint(example, url_prefix="/example")
app.register_blueprint(auth, url_prefix="/")


# default route
@app.route("/")
def hello_world():
    return "Hello world!", 200
@app.route("/register", methods=['POST'])
def app_register():
    return register()
@app.route("/login", methods=['POST'])
def app_login():
    return login()
@app.route("/logout", methods=['POST'])
def app_logout():
    return logout()




if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000), host="0.0.0.0")
    prisma.disconnect()
