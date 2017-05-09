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
