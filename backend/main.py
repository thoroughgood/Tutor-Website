from flask import Flask
from prisma import Prisma
from blueprints.example import example

prisma = Prisma(auto_register=True)
prisma.connect()

app = Flask(__name__)

# default route
app.route("/")
def index():
    return "Hello World"

# blueprints
app.register_blueprint(example, url_prefix='/example')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')


    