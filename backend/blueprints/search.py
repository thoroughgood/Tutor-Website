from flask import Blueprint, request, jsonify
from prisma.models import Tutor
from datetime import datetime
from helpers.rating_calc import rating_calc
from helpers.error_handlers import (
    ExpectedError,
    error_decorator,
)

search_tutor = Blueprint("search_tutor", __name__)


@search_tutor.route("/searchtutor", methods=["GET"])
@error_decorator
def search():
    args = request.get_json()
    # * Note: timesAvailable should never overlap and is assumed not to
    tutors = Tutor.prisma().find_many(
        include={
            "rating": True,
            "courseOfferings": True,
            "timesAvailable": {"order_by": {"startTime": "asc"}},
        }
    )

    if len(args) == 0:
        return jsonify({"tutorIds": [tutor.id for tutor in tutors]}), 200

    valid_tutors = []
    for tutor in tutors:
        valid = True

        # ? May need to change datetimes here to utc
        if "timeRange" in args:
            if (
                "startTime" not in args["timeRange"]
                or "endTime" not in args["timeRange"]
            ):
                raise ExpectedError("field(s) were missing in 'timeRange'", 400)

            try:
                st = datetime.fromisoformat(args["timeRange"]["startTime"])
                et = datetime.fromisoformat(args["timeRange"]["endTime"])
            except:
                raise ExpectedError("timeRange field(s) were malformed", 400)

            if st > et:
                raise ExpectedError("endTime cannot be less than startTime", 400)
            elif st < datetime.now():
                # ? May not be a necessary check
                raise ExpectedError("startTime must be in the future", 400)

            if len(tutor.timesAvailable) != 0:
                tutor_st = tutor.timesAvailable[0].startTime.replace(tzinfo=None)
                tutor_et = tutor.timesAvailable[-1].endTime.replace(tzinfo=None)
                valid &= et >= tutor_st and st <= tutor_et
            else:
                valid &= False

        if "location" in args:
            # ? naive impl, probably change at some point
            valid &= tutor.location and (
                tutor.location.lower() == args["location"].lower()
            )

        if "rating" in args:
            valid &= rating_calc(tutor.rating) >= float(args["rating"])

        if "courseOfferings" in args:
            args_offerings = [
                offerings.lower() for offerings in args["courseOfferings"]
            ]
            valid &= all(
                offerings.name.lower() in args_offerings
                for offerings in tutor.courseOfferings
            )

        if valid:
            valid_tutors.append(tutor.id)

    return jsonify({"tutorIds": valid_tutors}), 200