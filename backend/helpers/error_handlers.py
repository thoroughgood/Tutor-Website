from typing import Tuple, Callable, Any
from flask import Response, jsonify, logging


class ExpectedError(Exception):
    pass


def expected_error_wrapper(error: str, status_code: int):
    raise ExpectedError(error, status_code)


def error_generator(error: str, status_code: int) -> Tuple[Response, int]:
    return jsonify({"error": error}), status_code


def error_decorator(f):
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ExpectedError as e:
            msg, code = e.args
            return error_generator(msg, code)
        except:
            # todo: configure logging
            return error_generator("Internal Server Error", 500)

    return wrapped
