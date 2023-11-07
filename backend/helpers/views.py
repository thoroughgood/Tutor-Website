from typing import List
from prisma.models import (
    User,
    Appointment,
    Subject,
    Rating,
    TutorAvailability,
    Document,
    Message,
    DirectMessage,
    Notification,
)


class UserView:
    id: str
    email: str
    hashed_password: str
    name: str
    bio: str | None
    profile_picture: str | None
    location: str | None
    phone_number: str | None
    messages: List[Message] | None
    from_direct_message: List[DirectMessage] | None
    to_direct_message: List[DirectMessage] | None
    tutorial_state: bool
    notifications: List[Notification] | None

    def __init__(
        self,
        id: str,
        email: str,
        hashed_password: str,
        name: str,
        bio: str | None,
        profile_picture: str | None,
        location: str | None,
        phone_number: str | None,
        messages: List[Message] | None,
        from_direct_message: List[DirectMessage] | None,
        to_direct_message: List[DirectMessage] | None,
        tutorial_state: bool,
        notifications: List[Notification] | None,
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.name = name
        self.bio = bio
        self.profile_picture = profile_picture
        self.location = location
        self.phone_number = phone_number
        self.messages = messages
        self.from_direct_message = from_direct_message
        self.to_direct_message = to_direct_message
        self.tutorial_state = tutorial_state
        self.notifications = notifications


class StudentView(UserView):
    appointments: List[Appointment] | None

    def __init__(
        self,
        id: str,
        email: str,
        hashed_password: str,
        name: str,
        bio: str | None,
        profile_picture: str | None,
        location: str | None,
        phone_number: str | None,
        appointments: List[Appointment] | None,
        messages: List[Message] | None,
        from_direct_message: List[DirectMessage] | None,
        to_direct_message: List[DirectMessage] | None,
        tutorial_state: bool,
        notifications: List[Notification] | None,
    ):
        super().__init__(
            id,
            email,
            hashed_password,
            name,
            bio,
            profile_picture,
            location,
            phone_number,
            messages,
            from_direct_message,
            to_direct_message,
            tutorial_state,
            notifications,
        )
        self.appointments = appointments


class TutorView(UserView):
    ratings: List[Rating] | None
    appointments: List[Appointment] | None
    course_offerings: List[Subject] | None
    times_available: List[TutorAvailability] | None
    documents: List[Document] | None

    def __init__(
        self,
        id: str,
        email: str,
        hashed_password: str,
        name: str,
        bio: str | None,
        profile_picture: str | None,
        location: str | None,
        phone_number: str | None,
        ratings: List[Rating] | None,
        appointments: List[Appointment] | None,
        course_offerings: List[Subject] | None,
        times_available: List[TutorAvailability] | None,
        documents: List[Document] | None,
        messages: List[Message] | None,
        from_direct_message: List[DirectMessage] | None,
        to_direct_message: List[DirectMessage] | None,
        tutorial_state: bool,
        notifications: List[Notification] | None,
    ):
        super().__init__(
            id,
            email,
            hashed_password,
            name,
            bio,
            profile_picture,
            location,
            phone_number,
            messages,
            from_direct_message,
            to_direct_message,
            tutorial_state,
            notifications,
        )
        self.appointments = appointments
        self.course_offerings = course_offerings
        self.ratings = ratings
        self.times_available = times_available
        self.documents = documents


class AdminView(UserView):
    def __init__(
        self,
        id: str,
        email: str,
        hashed_password: str,
        name: str,
        bio: str | None,
        profile_picture: str | None,
        location: str | None,
        phone_number: str | None,
        messages: List[Message] | None,
        from_direct_message: List[DirectMessage] | None,
        to_direct_message: List[DirectMessage] | None,
        tutorial_state: bool,
        notifications: List[Notification] | None,
    ):
        super().__init__(
            id,
            email,
            hashed_password,
            name,
            bio,
            profile_picture,
            location,
            phone_number,
            messages,
            from_direct_message,
            to_direct_message,
            tutorial_state,
            notifications,
        )


def user_view(id: str = None, email: str = None) -> UserView | None:
    if id is None and email is None:
        return None
    elif id and email:
        raise ValueError("You cannot filter on both id and email")

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
        include={
            "messages": True,
            "fromDirectMessages": True,
            "toDirectMessages": True,
            "notifications": True,
        },
    )

    return (
        UserView(
            user.id,
            user.email,
            user.hashedPassword,
            user.name,
            user.bio,
            user.profilePicture,
            user.location,
            user.phoneNumber,
            user.messages,
            user.fromDirectMessages,
            user.toDirectMessages,
            user.tutorialState,
            user.notifications,
        )
        if user is not None
        else None
    )


def student_view(id: str = None, email: str = None) -> StudentView | None:
    if id is None and email is None:
        return None
    elif id and email:
        raise ValueError("You cannot filter on both id and email")

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
        include={
            "studentInfo": {"include": {"appointments": True}},
            "messages": True,
            "fromDirectMessages": True,
            "toDirectMessages": True,
            "notifications": True,
        },
    )

    return (
        StudentView(
            user.id,
            user.email,
            user.hashedPassword,
            user.name,
            user.bio,
            user.profilePicture,
            user.location,
            user.phoneNumber,
            user.studentInfo.appointments,
            user.messages,
            user.fromDirectMessages,
            user.toDirectMessages,
            user.tutorialState,
            user.notifications,
        )
        if user is not None and user.studentInfo is not None
        else None
    )


def tutor_view(id: str = None, email: str = None) -> TutorView | None:
    if id is None and email is None:
        return None
    elif id and email:
        raise ValueError("You cannot filter on both id and email")

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
        include={
            "tutorInfo": {
                "include": {
                    "ratings": True,
                    "appointments": True,
                    "courseOfferings": True,
                    "timesAvailable": True,
                    "documents": True,
                }
            },
            "messages": True,
            "fromDirectMessages": True,
            "toDirectMessages": True,
            "notifications": True,
        },
    )
    return (
        TutorView(
            user.id,
            user.email,
            user.hashedPassword,
            user.name,
            user.bio,
            user.profilePicture,
            user.location,
            user.phoneNumber,
            user.tutorInfo.ratings,
            user.tutorInfo.appointments,
            user.tutorInfo.courseOfferings,
            user.tutorInfo.timesAvailable,
            user.tutorInfo.documents,
            user.messages,
            user.fromDirectMessages,
            user.toDirectMessages,
            user.tutorialState,
            user.notifications,
        )
        if user is not None and user.tutorInfo is not None
        else None
    )


def admin_view(id: str = None, email: str = None) -> AdminView | None:
    if id is None and email is None:
        return None
    elif id and email:
        raise ValueError("You cannot filter on both id and email")

    search_by = {"id": id} if id else {"email": email}
    user = User.prisma().find_unique(
        where=search_by,
        include={
            "adminInfo": True,
            "messages": True,
            "fromDirectMessages": True,
            "toDirectMessages": True,
            "notifications": True,
        },
    )
    return (
        AdminView(
            user.id,
            user.email,
            user.hashedPassword,
            user.name,
            user.bio,
            user.profilePicture,
            user.location,
            user.phoneNumber,
            user.messages,
            user.fromDirectMessages,
            user.toDirectMessages,
            user.tutorialState,
            user.notifications,
        )
        if user is not None and user.adminInfo is not None
        else None
    )
