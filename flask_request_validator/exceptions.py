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
    def __init__(self, errors: Union[Dict]):
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
    def __init__(self, depth: List[str], errors: Dict[int, RequestError]):
        self.depth = depth
        self.errors = errors


class JsonListItemTypeError(RequestError):
    """
    Raises when invalid type of list item.
    Expected ['name'] but got [{'name': 'val'}] or [{'name': 'val'}] but got ['name']
    """
    def __init__(self, only_dict=True):
        """
        :param only_dict: str, int, float, bool types if False. see: JsonParam._check_list_item_type
        """
        self.only_dict = only_dict


class RequiredJsonKeyError(RequestError):
    def __init__(self, key: str):
        self.key = key


TooMuchArguments = TooManyArguments
"""backward compatibility for version 3.0.0"""
