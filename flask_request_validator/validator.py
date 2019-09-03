import types
from functools import wraps

from flask import request

from .exceptions import (
    NotAllowedType,
    UndefinedParamType,
    InvalidRequest
)
from .rules import CompositeRule, ALLOWED_TYPES

# request params. see: __get_request_value()
GET = 'GET'
PATH = 'PATH'
FORM = 'FORM'
JSON = 'JSON'
PARAM_TYPES = (GET, PATH, JSON, FORM)


class Param(object):

    def __init__(self, name, param_type, value_type=None,
                 required=True, default=None, rules=None):
        """
        :param mixed default:
        :param bool required:
        :param type value_type: type of value (int, list, etc)
        :param list|CompositeRule rules:
        :param str name: name of param
        :param str param_type: type of request param (see: PARAM_TYPES)
        :raises: UndefinedParamType, NotAllowedType
        """

        if param_type not in PARAM_TYPES:
            raise UndefinedParamType('Undefined param type "%s"' % param_type)

        if value_type and value_type not in ALLOWED_TYPES:
            raise NotAllowedType('Value type "%s" is not allowed' % value_type)

        self.value_type = value_type
        self.default = default
        self.required = required
        self.name = name
        self.param_type = param_type
        self.rules = rules or []

    def value_to_type(self, value):
        """
        :param mixed value:
        :return: mixed
        """
        if self.param_type != JSON:
            if self.value_type == bool:
                low_val = value.lower()

                if low_val in ('true', '1'):
                    value = True
                elif low_val in ('false', '0'):
                    value = False
            elif self.value_type == list:
                value = [item.strip() for item in value.split(',')]
            elif self.value_type == dict:
                value = {
                    item.split(':')[0].strip(): item.partition(':')[-1].strip()
                    for item in value.split(',')
                }

        if self.value_type:
            value = self.value_type(value)

        return value


def validate_params(*params):
    """
    Validate route of request. Example:

    @app.route('/<int:level>')
    @validate_params(
        # FORM param(request.form)
        Param('param_name', FROM, ...),
        # PATH param(part of route - request.view_args)
        Param('level', PATH, rules=[Pattern(r'^[a-zA-Z0-9-_.]{5,20}$')]),
    )
    def example_route(level):
        ...
    """

    def validate_request(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors, endpoint_args = __get_errors(params)
            if errors:
                raise InvalidRequest(errors)

            if args:
                endpoint_args = (args[0], ) + tuple(endpoint_args)

            return func(*endpoint_args)

        return wrapper

    return validate_request


def __get_errors(params):
    """
    Returns errors of validation and valid values
    :param tuple params: (Param(), Param(), ...)
    :rtype: list
    :return:
        {{'param_name': ['error1', 'error2', ...], ...},
        [value1, value2, value3, ...]
    """

    errors = {}
    valid_values = []

    for param in params:
        param_name = param.name
        param_type = param.param_type
        value = __get_request_value(param_type, param_name)

        if value is None:
            if param.required:
                errors[param_name] = ['Value is required']

                continue
            else:
                if param.default is not None:
                    if isinstance(param.default, types.LambdaType):
                        value = param.default()
                    else:
                        value = param.default

                valid_values.append(value)

                continue
        else:
            if param.value_type:
                try:
                    value = param.value_to_type(value)
                except (ValueError, TypeError):
                    errors[param_name] = [
                        'Error of conversion value "%s" to type %s' %
                        (value, param.value_type)
                    ]

                    continue

                if param.value_type != type(value):
                    errors[param_name] = [
                        'Error of conversion value "%s" to type %s' %
                        (value, param.value_type)
                    ]

                    continue

            rules_errors = []
            for rule in param.rules:
                rules_errors.extend(rule.validate(value))

            if rules_errors:
                errors[param_name] = rules_errors
            else:
                valid_values.append(value)

    return errors, valid_values


def __get_request_value(value_type, name):
    """
    :param str value_type: POST, GET or VIEW
    :param str name:
    :raise: UndefinedParamType
    :return: mixed
    """
    if value_type == FORM:
        return request.form.get(name)
    elif value_type == GET:
        return ",".join(request.args.getlist(name))
    elif value_type == PATH:
        return request.view_args.get(name)
    elif value_type == JSON:
        json_ = request.get_json()
        return json_.get(name) if json_ else json_
    else:
        raise UndefinedParamType('Undefined param type %s' % name)
