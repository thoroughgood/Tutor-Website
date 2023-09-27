from flask import Blueprint
from prisma.models import User

example = Blueprint("example", __name__)

@example.route('/', methods=['GET'])
async def index():
    user = User.prisma().find_first()
    return dict(user)