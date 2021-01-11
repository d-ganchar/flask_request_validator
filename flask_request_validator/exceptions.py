import json


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

    def __init__(self, errors):
        """
        :param dict errors: {'get': dict_with_errors, 'post': dict_with_errors}
        """
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


class ParameterNameIsNotUnique(RequestError):
    """
    Got same parameter name more than once. Example:

    @validate_params(
        Param('user', PATH, str),
        Param('user', JSON, str),
    )
    """


class TooManyArguments(RequestError):
    """
    Got more arguments in request then expected
    """

    def __init__(self, msg):
        self.message = msg


TooMuchArguments = TooManyArguments
"""backward compatibility for version 3.0.0"""
