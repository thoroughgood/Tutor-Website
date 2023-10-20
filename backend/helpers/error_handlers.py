from typing import Tuple
from flask import Response, jsonify, current_app
from re import search
from jsonschema import ValidationError
import traceback


class ExpectedError(Exception):
    def __init__(self, error_msg: str, status_code: int):
        self.args = error_msg, status_code


def error_generator(error_msg: str, status_code: int) -> Tuple[Response, int]:
    return jsonify({"error": error_msg}), status_code


def validation_pattern_match(error: ValidationError) -> Response:
    match error.absolute_schema_path:
        # The `*_` syntax just means 'ignore everything before if there is something'
        # omitted field when specified required
        case [*validators, "required"]:
            field = search(r"'(.*?)'", error.message).group(0)
            if len(validators) > 1:
                # we'll just return the 'parent' validator as information
                return error_generator(f"{field} was missing from {validators[1]}", 400)
            else:
                return error_generator(f"{field} was missing from field(s)", 400)
        # field is of wrong type
        case [*_, "properties", field, "type"]:
            return error_generator(
                f"field '{field}' must be of type {error.validator_value}", 400
            )
        # field specific validation
        case [*_, "properties", "email", "pattern"]:
            return error_generator("email field is invalid", 400)
        case [*_, "properties", field, "minLength"]:
            return error_generator(
                f"{field} field must be at least {error.validator_value} character(s)",
                400,
            )
        case [*_, "properties", "accountType", "pattern"]:
            return error_generator(
                f"accountType must match {error.validator_value}", 400
            )
        case [*_, "properties", "rating", "minimum"] | [
            *_,
            "properties",
            "rating",
            "maximum",
        ] | [*_, "properties", "rating", "pattern"]:
            # Error may need to be changed if the boundaries of rating ever change
            return error_generator("rating must be between 1 to 5, inclusive.", 400)


def error_decorator(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ExpectedError as e:
            msg, code = e.args
            return error_generator(msg, code)
        except ValidationError as e:
            return validation_pattern_match(e)
        except:
            current_app.logger.error("\n" + traceback.format_exc() + "\n")
            return error_generator("Internal Server Error", 500)

    wrapper.__name__ = f.__name__
    return wrapper
