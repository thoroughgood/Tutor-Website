import json
import re
from flask import Blueprint, jsonify
from prisma.models import Tutor
from jsonschemas.tutor_search_schema import tutor_search_schema
from helpers.process_time_block import process_time_block
from helpers.rating_calc import rating_calc
from helpers.error_handlers import (
    validate_decorator,
    ExpectedError,
    error_decorator,
)

search_tutor = Blueprint("search_tutor", __name__)


@search_tutor.route("/searchtutor", methods=["GET"])
@error_decorator
@validate_decorator("query_string", tutor_search_schema)
def tutor_search(args):
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
                is not None
            )

        if "timeRange" in args and len(tutor.timesAvailable) != 0:
            try:
                time_range = json.loads(args["timeRange"])
            except json.decoder.JSONDecodeError:
                raise ExpectedError("timeRange field must be valid JSON", 400)

            if "startTime" not in time_range or "endTime" not in time_range:
                raise ExpectedError("field(s) were missing in 'timeRange'", 400)

            data = process_time_block(time_range)
            st = data["startTime"]
            et = data["endTime"]

            # Note: datetimes extracted from the db are default UTC
            valid &= any(
                et >= times_available.startTime and st <= times_available.endTime
                for times_available in tutor.timesAvailable
            )
        elif "timeRange" in args:
            continue

        if "location" in args and tutor.userInfo.location:
            tutor_location = tutor.userInfo.location.lower().strip()
            search_location = args["location"].lower().strip()
            valid &= re.search(search_location, tutor_location) != None
        elif "location" in args:
            continue

        if "rating" in args:
            # conversion required as rating is passed in a query string
            valid &= rating_calc(tutor.ratings) >= float(args["rating"])

        if "courseOfferings" in args:
            # Although flask has a `get_list` method on request.args,
            # due to how the current frontend is setup, this is more acceptable
            try:
                course_offerings = json.loads(args["courseOfferings"])
            except json.decoder.JSONDecodeError:
                raise ExpectedError("courseOfferings field must be valid JSON", 400)

            args_offerings = [offerings.lower() for offerings in course_offerings]
            valid &= any(
                offerings.name.lower() in args_offerings
                for offerings in tutor.courseOfferings
            )

        if valid:
            valid_tutors.append(tutor.id)

    return jsonify({"tutorIds": valid_tutors}), 200
