from flask import Request
import typing as t
from helpers.error_handlers import error_generator, ExpectedError


class MyRequest(Request):
    def on_json_loading_failed(self, _: ValueError | None) -> t.Any:
        raise ExpectedError("content-type was not json or data was malformed", 415)
