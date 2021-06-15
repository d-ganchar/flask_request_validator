from typing import List, Union, Dict, Any


class RequestError(Exception):
    """
    Base flask_request_validator exception
    """


class AfterParamError(RequestError):
    pass


class WrongUsageError(RequestError):
    pass


class JsonError(RequestError):
    def __init__(self, depth: List[str], errors: Dict[int, RequestError], as_list: bool):
        self.depth = depth
        self.errors = errors
        self.as_list = as_list


class JsonListExpectedError(JsonError):
    def __init__(self, depth: List[str]):
        self.depth = depth

    def __str__(self) -> str:
        return 'list type expected'


class JsonDictExpectedError(JsonListExpectedError):
    def __str__(self) -> str:
        return 'dict type expected'


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

    def __str__(self) -> str:
        if self.only_dict:
            return 'invalid type, expected object'
        return 'invalid type expected string or number'


class RequiredValueError(RequestError):
    def __str__(self) -> str:
        return 'value is required'


class RequiredJsonKeyError(RequestError):
    def __init__(self, key: str):
        self.key = key

    def __str__(self) -> str:
        return f'json key "{self.key}" is required'


class TypeConversionError(RequestError):
    def __str__(self) -> str:
        return 'invalid type'


class RuleError(RequestError):
    pass


class ValuePatternError(RuleError):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def __str__(self) -> str:
        return f'value does not match pattern {self.pattern}'


class ValueEnumError(RuleError):
    def __init__(self, allowed: Any):
        self.allowed = allowed

    def __str__(self) -> str:
        return 'not allowed, allowed values: ' + '|'.join(self.allowed)


class ValueMaxLengthError(RuleError):
    def __init__(self, length: int):
        self.length = length

    def __str__(self) -> str:
        return f'invalid length, max length = {self.length}'


class ValueMinLengthError(ValueMaxLengthError):
    def __str__(self) -> str:
        return f'invalid length, min length = {self.length}'


class ValueMaxError(RuleError):
    def __init__(self, value: Union[int, float], include_boundary: bool):
        self.value = value
        self.include_boundary = include_boundary

    def __str__(self) -> str:
        if self.include_boundary:
            return f'greater then allowed: value is not <= {self.value}'
        return f'greater then allowed: value is not < {self.value}'


class ValueMinError(ValueMaxError):
    def __str__(self) -> str:
        if self.include_boundary:
            return f'smaller then allowed: value is not >= {self.value}'
        return f'smaller then allowed: value is not > {self.value}'


class ValueEmptyError(RuleError):
    def __str__(self) -> str:
        return 'empty string not allowed'


class ValueDtIsoFormatError(RuleError):
    def __str__(self) -> str:
        return f'expected a datetime in ISO format'


class ValueEmailError(RuleError):
    def __str__(self) -> str:
        return 'invalid email address'


class NumberError(RuleError):
    def __str__(self) -> str:
        return 'expected number'


class ValueDatetimeError(RuleError):
    def __init__(self, dt_format: str) -> None:
        self.dt_format = dt_format

    def __str__(self) -> str:
        return f'expected a datetime in {self.dt_format} format'


class ListRuleError(RuleError):
    def __init__(self, errors: List[Any]) -> None:
        self.errors = errors


class RulesError(RequestError):
    def __init__(self, *args: RuleError):
        self.errors = args

    def __str__(self) -> str:
        return '. '.join([str(e) for e in self.errors])


class InvalidHeadersError(RequestError):
    def __init__(self, errors: Dict[str, RulesError]):
        self.errors = errors

    def __str__(self) -> str:
        formatted = []
        for name, rules_errors in self.errors.items():
            formatted.append(f'invalid header {name}. {rules_errors}')
        return '. '.join(formatted)


class InvalidRequestError(RequestError):
    def __init__(
        self,
        get: Dict[str, RulesError],
        form: Dict[str, RulesError],
        path: Dict[str, RulesError],
        json: Union[List[JsonError], Dict[str, RulesError]],
    ):
        self.json = json  # list when nested json validation
        self.path = path
        self.get = get
        self.form = form
