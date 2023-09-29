from flask import Blueprint
from prisma.models import Admin

example = Blueprint("example", __name__)

@example.route('/', methods=['GET'])
def index():
    admin = Admin.prisma().find_first()
    return dict(admin), 200