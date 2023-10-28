from prisma.models import User


# ! Note: requires a user with all fields INCLUDED
# e.g. User.prisma().find_unique(..., include={"adminInfo": True, "tutorInfo": True, "studentInfo": True})
def check_type(user: User) -> str:
    if user.adminInfo is not None:
        return "admin"
    elif user.tutorInfo is not None:
        return "tutor"
    elif user.studentInfo is not None:
        return "student"

    return "N/A"
