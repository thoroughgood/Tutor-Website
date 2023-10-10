from prisma.models import User


def user(id: str) -> User | None:
    user = User.prisma().find_unique(where={"id", id})
    return user if user != None else None


def student(id: str) -> User | None:
    user = User.prisma().find_unique(
        where={"id": id}, include={"studentInfo": {"include": {"appointments": True}}}
    )
    return user if user != None and user.studentInfo != None else None


def tutor(id: str) -> User | None:
    user = User.prisma().find_unique(
        where={"id": id},
        include={
            "tutorInfo": {
                "include": {
                    "appointments": True,
                    "courseOfferings": True,
                    "timesAvailable": True,
                }
            }
        },
    )
    return user if user != None and user.tutorInfo != None else None


def admin(id: str) -> User | None:
    user = User.prisma().find_unique(
        where={"id": id},
        include={"adminInfo": True},
    )
    return user if user != None and user.adminInfo != None else None
