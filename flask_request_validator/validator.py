import types
from functools import wraps
from typing import Tuple

from flask import request

from .after_param import AbstractAfterParam
from .exceptions import *
from .rules import CompositeRule
from .valid_request import ValidRequest
from .nested_json import JsonParam


GET = 'GET'
PATH = 'PATH'
FORM = 'FORM'
HEADER = 'HEADER'
JSON = 'JSON'
PARAM_TYPES = (GET, PATH, FORM, JSON, HEADER)
_ALLOWED_TYPES = (str, bool, int, float, dict, list)


class _ValidRequest(ValidRequest):
    def __init__(self) -> None:
        self._valid_data = dict()

    def set_value(self, param_type: str, key: str, value: Any):
        self._valid_data.setdefault(param_type, dict())
        self._valid_data[param_type][key] = value

    def set_json(self, value: dict):
        self._valid_data[JSON] = value

    def get_form(self) -> Dict[str, Any]:
        return self._valid_data.get(FORM, dict())

    def get_headers(self) -> Dict[str, Any]:
        return self._valid_data.get(HEADER, dict())

    def get_json(self) -> Dict[str, Any]:
        return self._valid_data.get(JSON, dict())

    def get_params(self) -> Dict[str, Any]:
        return self._valid_data.get(GET, dict())

    def get_path_params(self) -> Dict[str, Any]:
        return self._valid_data.get(PATH, dict())


class Param:
    def __init__(self, name, param_type, value_type=None,
                 required=True, default=None, rules=None):
        """
        :param mixed default:
        :param bool required:
        :param type value_type: type of value (int, list, etc)
        :param list|CompositeRule rules:
        :param str name: name of param
        :param str param_type: type of request param (see: PARAM_TYPES)
        :raises: UndefinedParamType, NotAllowedType, WrongUsageError
        """
        if param_type not in PARAM_TYPES:
            raise WrongUsageError(
                'Param.name = "%s". '
                'invalid Param.value_type "%s". allowed: %s' % (name, param_type, PARAM_TYPES))
        if value_type and value_type not in _ALLOWED_TYPES:
            raise WrongUsageError(
                'Param.name = "%s". '
                'invalid Param.value_type "%s". allowed: %s' % (name, value_type, _ALLOWED_TYPES))
        if required and default:
            raise WrongUsageError(
                'Param.name = "%s". '
                'defaults are only allowed when required=False' % (name, ))

        self.value_type = value_type
        self.default = default
        self.required = required
        self.name = name
        self.param_type = param_type
        if isinstance(rules, CompositeRule):
            self.rules = rules
        else:
            self.rules = CompositeRule(*rules or [])

    def value_to_type(self, value: Any) -> Any:
        """
        :raises TypeConversionError:
        """
        if self.value_type == bool:
            if isinstance(value, str):
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

        try:
            if self.value_type:
                value = self.value_type(value)
        except (ValueError, TypeError):
            raise TypeConversionError()

        if self.value_type != type(value):
            raise TypeConversionError()
        return value

    def get_value_from_request(self) -> Any:
        """
        :raises RequiredValueError:
        """
        value = None
        if self.param_type == FORM:
            value = request.form.get(self.name)
        elif self.param_type == GET:
            value = request.args.getlist(self.name)
            value = ",".join(value) if value else None
        elif self.param_type == PATH:
            value = request.view_args.get(self.name)
        elif self.param_type == JSON:
            json_ = request.get_json()
            value = json_.get(self.name) if json_ else None
        elif self.param_type == HEADER:
            value = request.headers.get(self.name)

        if value is None and self.required:
            raise RequiredValueError()
        return value


def validate_params(*params: Union[JsonParam, Param, AbstractAfterParam]):
    """
    :raises InvalidHeadersError:
        When found invalid headers. Raises before other params validation
    :raises InvalidRequestError:
        Raises after headers validation if errors found
    """
    def validate_request(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            header_params, other_params, after_params = (), (), ()
            for param in params:
                if isinstance(param, Param) and param.param_type == HEADER:
                    header_params += (param, )
                elif isinstance(param, AbstractAfterParam):
                    after_params += (param, )
                else:
                    other_params += (param, )

            valid = _ValidRequest()
            valid, errors = __get_request_errors(header_params, valid)
            if errors.get(HEADER):
                raise InvalidHeadersError(errors[HEADER])

            valid, errors = __get_request_errors(other_params, valid)
            for type_errors in errors.values():
                if type_errors:
                    raise InvalidRequestError(errors[GET], errors[FORM],
                                              errors[PATH], errors[JSON])
            for param in after_params:
                param.validate(valid)

            args += (valid, )
            return func(*args, **kwargs)
        return wrapper
    return validate_request


def __get_request_errors(
    params: Tuple[Union[Param, JsonParam], ...],
    valid: _ValidRequest
) -> Tuple[_ValidRequest, Dict[str, Union[Dict[str, RulesError], List[JsonError]]]]:
    errors = {GET: dict(), FORM: dict(), JSON: dict(), HEADER: dict(), PATH: dict()}
    for param in params:
        if isinstance(param, JsonParam):
            value, json_errors = param.validate(request.get_json())
            if json_errors:
                errors[JSON] = json_errors
            else:
                valid.set_json(value)
            continue

        try:
            value = param.get_value_from_request()
            if value is not None:
                value = param.value_to_type(value)
                value = param.rules.validate(value)
                valid.set_value(param.param_type, param.name, value)
                continue

            if param.default is not None:
                if isinstance(param.default, types.LambdaType):
                    valid.set_value(param.param_type, param.name, param.default())
                else:
                    valid.set_value(param.param_type, param.name, param.default)
        except (RequiredValueError, TypeConversionError, RulesError) as error:
            errors[param.param_type][param.name] = error
            continue

    return valid, errors
