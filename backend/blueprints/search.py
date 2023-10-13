import json
import re
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
    args = request.args

    # * Note: timesAvailable should never overlap and is assumed not to
    tutors = Tutor.prisma().find_many(
        include={
            "userInfo": True,
            "ratings": True,
            "courseOfferings": True,
            "timesAvailable": {"order_by": {"startTime": "asc"}},
        }
    )

    if len(args) == 0:
        return jsonify({"tutorIds": [tutor.id for tutor in tutors]}), 200

    valid_tutors = []
    for tutor in tutors:
        valid = True

        if "name" in args:
            valid &= (
                re.search(args["name"].lower().strip(), tutor.userInfo.name.lower())
                != None
            )

        # ? May need to change datetimes here to utc
        if "timeRange" in args and len(tutor.timesAvailable) != 0:
            try:
                timeRange = json.loads(args["timeRange"])
            except json.decoder.JSONDecodeError:
                raise ExpectedError("timeRange field must be valid JSON", 400)

            if "startTime" not in timeRange or "endTime" not in timeRange:
                raise ExpectedError("field(s) were missing in 'timeRange'", 400)

            try:
                st = datetime.fromisoformat(timeRange["startTime"])
                et = datetime.fromisoformat(timeRange["endTime"])
            except ValueError:
                raise ExpectedError("timeRange field(s) was malformed", 400)

            if st > et:
                raise ExpectedError("endTime cannot be less than startTime", 400)
            elif st < datetime.now():
                # ? May not be a necessary check
                raise ExpectedError("startTime must be in the future", 400)

            tutor_st = tutor.timesAvailable[0].startTime.replace(tzinfo=None)
            tutor_et = tutor.timesAvailable[-1].endTime.replace(tzinfo=None)
            valid &= et >= tutor_st and st <= tutor_et
        elif "timeRange" in args:
            continue

        if "location" in args and tutor.userInfo.location:
            tutor_location = tutor.userInfo.location.lower().strip()
            search_location = args["location"].lower().strip()
            valid &= re.search(search_location, tutor_location) != None
        elif "location" in args:
            continue

        if "rating" in args:
            valid &= rating_calc(tutor.ratings) >= float(args["rating"])

        if "courseOfferings" in args:
            args_offerings = [
                offerings.lower() for offerings in args.getlist("courseOfferings")
            ]
            valid &= any(
                offerings.name.lower() in args_offerings
                for offerings in tutor.courseOfferings
            )

        if valid:
            valid_tutors.append(tutor.id)

    return jsonify({"tutorIds": valid_tutors}), 200
