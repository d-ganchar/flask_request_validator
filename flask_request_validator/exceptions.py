import json
from typing import List, Union, Dict


class RequestError(Exception):
    """
    Base flask_request_validator exception
    """


class UndefinedParamType(RequestError):
    """
    Not allowed type of param(GET, POST )
    """


class NotAllowedType(RequestError):
    """
    Not allowed type. See: rules.ALLOWED_TYPES
    """


class InvalidRequest(RequestError):
    """
    GET or POST data is invalid
    """
    def __init__(self, errors: Union[List, Dict]):
        self.errors = errors
        self.message = str(self)

    def __str__(self):
        return 'Invalid request data. ' + json.dumps(self.errors)


class InvalidHeader(RequestError):
    """
    request header data is invalid
    """

    def __init__(self, errors):
        """
        :param dict errors: {'get': dict_with_errors, 'post': dict_with_errors}
        """
        self.errors = errors
        self.message = str(self)

    def __str__(self):
        return 'Invalid request header. ' + json.dumps(self.errors)


class TooManyArguments(RequestError):
    """
    Got more arguments in request then expected
    """

    def __init__(self, msg):
        self.message = msg


class NestedJsonError(RequestError):
    def __init__(self, depth: List[str], errors: List[RequestError]):
        self.depth = depth
        self.errors = errors


class RequiredJsonKeyError(RequestError):
    def __init__(self, key: str) -> None:
        self.key = key


TooMuchArguments = TooManyArguments
"""backward compatibility for version 3.0.0"""
