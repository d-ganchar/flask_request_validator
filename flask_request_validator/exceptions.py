import json


class UndefinedParamType(Exception):
    """
    Not allowed type of param(GET, POST )
    """


class NotAllowedType(Exception):
    """
    Not allowed type. See: rules.ALLOWED_TYPES
    """


class InvalidRequest(Exception):
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


class InvalidHeader(Exception):
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


class TooManyArguments(Exception):
    """
    Got more arguments in request then expected
    """

    def __init__(self, msg):
        self.message = msg


TooMuchArguments = TooManyArguments
"""backward compatibility for version 3.0.0"""
