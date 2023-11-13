from typing import Tuple
from jsonschema import validate
from flask import Response, jsonify, current_app, request
from re import search
from jsonschema import ValidationError
from functools import wraps
import traceback


class ExpectedError(Exception):
    def __init__(self, error_msg: str, status_code: int):
        self.args = error_msg, status_code


def error_generator(error_msg: str, status_code: int) -> Tuple[Response, int]:
    return jsonify({"error": error_msg}), status_code


def validation_pattern_match(error: ValidationError) -> Tuple[Response, int]:
    # You may want to read up on 'structural pattern matching' to understand
    # the syntax here.
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
            # Error will need to be changed if the boundaries of rating ever change
            return error_generator("rating must be between 1 to 5, inclusive", 400)
        case [*_, "properties", "sortBy", "pattern"]:
            return error_generator(
                "When specified, 'sortBy' must be equal to 'messageSent'", 400
            )


def error_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ExpectedError as e:
            msg, code = e.args
            return error_generator(msg, code)
        except ValidationError as e:
            return validation_pattern_match(e)
        except:
            current_app.logger.critical("\n" + traceback.format_exc() + "\n")
            return error_generator("Internal Server Error", 500)

    return wrapper


def validate_decorator(request_type: str, schema, format_checker=None):
    def _validate_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            match request_type:
                case "json":
                    instance = request.get_json()
                case "query_string":
                    instance = request.args
                case _:
                    raise ValueError("request_type must be either json or query_string")
            if format_checker:
                validate(instance, schema, format_checker=format_checker)
            else:
                validate(instance, schema)
            kwargs["args"] = instance
            return f(*args, **kwargs)

        return wrapper

    return _validate_decorator
