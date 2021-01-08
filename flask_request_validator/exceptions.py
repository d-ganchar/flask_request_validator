import json


class RequestException(Exception):
    """
    flask_request_validator base exception
    """


class UndefinedParamType(RequestException):
    """
    Not allowed type of param(GET, POST )
    """


class NotAllowedType(RequestException):
    """
    Not allowed type. See: rules.ALLOWED_TYPES
    """


class InvalidRequest(RequestException):
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


class InvalidHeader(InvalidRequest):
    """
    request header data is invalid
    """


class TooManyArguments(RequestException):
    """
    Got more arguments in request then expected
    """

    def __init__(self, msg):
        self.message = msg
