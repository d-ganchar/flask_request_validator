from functools import wraps

from .exceptions import InvalidRequest, UndefinedParamType
from .rules import Type, Required, CompositeRule
from flask import request


GET = 'GET'
VIEW = 'VIEW'
POST = 'POST'
PARAM_TYPES = (GET, VIEW, POST)


class Param(object):

    def __init__(self, name, param_type, *rules):
        """

        :param tuple rules:
        :param str name: name of param
        :param str param_type: type of request param (GET OR POST)
        """

        self.name = name
        self.param_type = param_type
        self.rules = rules

    def convert_value(self, value):
        """
        :param mixed value:
        :return: mixed
        """

        for rule in self.rules:
            if isinstance(rule, Type) and value:
                value = rule.value_to_type(value)

                break

        return value


def validate_params(*params):
    """
    Validate route using json schema. Example:

    @app.route('/<int:level>')
    @validate_params(
        # POST param
        Param('param_name', POST, Type(str), Required()),
        # VIEW param
        Param('level', VIEW, Type(str), Required(), Pattern(r'^[a-zA-Z0-9-_.]{5,20}$')),
    )
    def example_route(level):
        ...

    Also you can to set additional settings for Param(such as required, pattern(regex) etc).
    See: rules

    :param tuple params: (Param(), Param(), ...)
    """

    def validate_request(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors = __get_errors(params)
            if errors[GET] or errors[POST] or errors[VIEW]:
                raise InvalidRequest(errors)

            return func(*args, **kwargs)

        return wrapper

    return validate_request


def __get_errors(params):
    """
    Returns errors of validation
    :param tuple params: (Param(), Param(), ...)
    :rtype: dict
    :return: {
        'GET': {'param_name': ['error1', 'error2', ...]},
        'VIEW': {'param_name': ['error1', 'error2', ...]},
        'POST': {'param_name': ['error1', 'error2', ...]}
    }
    """

    errors = {
        GET: {},
        VIEW: {},
        POST: {},
    }

    for param in params:
        param_name = param.name
        param_type = param.param_type
        value = get_request_value(param_type, param_name)
        for rule in param.rules:
            if isinstance(rule, (Type, CompositeRule)) and value:
                value = rule.value_to_type(value)

                break

        for rule in param.rules:
            if isinstance(rule, Required) or value:
                rule_errors = rule.validate(value)
                if rule_errors:
                    errors[param_type].setdefault(param_name, [])

                    errors[param_type][param_name].extend(rule_errors)

    return errors


def get_request_value(value_type, name):
    """
    :param str value_type: POST, GET or VIEW
    :param str name:
    :raise: UndefinedParamType
    :return: mixed
    """
    if value_type == POST:
        value = request.form.get(name)
    elif value_type == GET:
        value = request.args.get(name)
    elif value_type == VIEW:
        value = request.view_args.get(name)
    else:
        raise UndefinedParamType('Undefined param type %s' % name)

    return value
