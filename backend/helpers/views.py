from prisma.models import User


def user_view(id: str = None, email: str = None) -> User | None:
    if id == None and email == None:
        return None

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(where=search_by)

    return user if user != None else None


def student_view(id: str = None, email: str = None) -> User | None:
    if id == None and email == None:
        return None

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
        include={"studentInfo": {"include": {"appointments": True}}},
    )

    return user if user != None and user.studentInfo != None else None


def tutor_view(id: str = None, email: str = None) -> User | None:
    if id == None and email == None:
        return None

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
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


def admin_view(id: str = None, email: str = None) -> User | None:
    if id == None and email == None:
        return None

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
        include={"adminInfo": True},
    )
    return user if user != None and user.adminInfo != None else None
