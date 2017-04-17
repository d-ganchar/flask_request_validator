from functools import wraps

from .exceptions import InvalidRequest, UndefinedParamType
from .rules import Type, Required
from flask import request


GET = 'get'
POST = 'post'


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


def validate_params(*params):
    """
    Validate route using json schema. Example:

    @app.route('/<int:level>')
    @validate_params(
        # POST param
        Param('param_name', POST, Type(str), Required()),
        # GET param
        Param('level', GET, Type(str), Required(), Pattern(r'^[a-zA-Z0-9-_.]{5,20}$')),
    )
    def example_route(level):
        ...

    Also you can to set additional settings for Param(such as required, pattern(regex) etc).
    See: rules

    :param tuple params: (Param(), Param(), ...)
    :raise: InvalidRequest
    """

    def validate_request(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors = __get_errors(params)
            if errors[GET] or errors[POST]:
                raise InvalidRequest(errors)

            return func(*args, **kwargs)

        return wrapper

    return validate_request


def __get_errors(params):
    """
    Returns errors of validation
    :param tuple params: (Param(), Param(), ...)
    :raise: UndefinedParamType
    :rtype: dict
    :return: {
        'get': {'param_name': ['error1', 'error2', ...]},
        'post': {'param_name': ['error1', 'error2', ...]}
    }
    """

    errors = dict(get=dict(), post=dict())

    for param in params:
        param_name = param.name
        param_type = param.param_type

        if param_type not in (POST, GET):
            raise UndefinedParamType('Undefined param type %s' % param_type)

        value_type = None
        for rule in param.rules:
            if isinstance(rule, Type):
                value_type = rule.value_type

                break

        if param_type == POST:
            value = request.form.get(param_name, value_type)
        else:
            value = request.view_args.get(param_name, value_type)

        for rule in param.rules:
            if isinstance(rule, Required) or value:
                rule_errors = rule.validate(value)
                if rule_errors:
                    errors[param_type].setdefault(param_name, [])

                    errors[param_type][param_name].extend(rule_errors)

    return errors
