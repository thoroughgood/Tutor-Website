from flask import Flask
from prisma import Prisma
from blueprints.example import example
import os

prisma = Prisma(auto_register=True)
prisma.connect()

app = Flask(__name__)

# blueprints
app.register_blueprint(example, url_prefix='/example')

# default route
@app.route('/')
def hello_world():
    return 'Hello world!', 200

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000), host="0.0.0.0")
    prisma.disconnect()