from typing import List, Union, Dict, Any


class RequestError(Exception):
    """
    Base flask_request_validator exception
    """


class WrongUsageError(RequestError):
    pass


class JsonError(RequestError):
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


class RequiredValueError(RequestError):
    pass


class RequiredJsonKeyError(RequestError):
    def __init__(self, key: str):
        self.key = key


class TypeConversionError(RequestError):
    pass


class RuleError(RequestError):
    pass


class ValuePatternError(RuleError):
    def __init__(self, pattern: str):
        self.pattern = pattern


class ValueEnumError(RuleError):
    def __init__(self, *args: Any):
        self.allowed = args


class ValueMaxLengthError(RuleError):
    def __init__(self, length: int):
        self.length = length


class ValueMinLengthError(ValueMaxLengthError):
    pass


class ValueMaxError(RuleError):
    def __init__(self, value: Union[int, float], include_boundary: bool):
        self.value = value
        self.include_boundary = include_boundary


class ValueMinError(ValueMaxError):
    pass


class ValueEmptyError(RuleError):
    pass


class ValueDtIsoFormatError(RuleError):
    pass


class ValueEmailError(RuleError):
    pass


class ValueDatetimeError(RuleError):
    def __init__(self, dt_format: str) -> None:
        self.dt_format = dt_format


class ListRuleError(RuleError):
    def __init__(self, *errors: Any) -> None:
        self.errors = errors


class RulesError(RequestError):
    def __init__(self, *args: RuleError):
        self.errors = args


class InvalidHeadersError(RequestError):
    def __init__(self, errors: Dict[str, RulesError]):
        self.errors = errors


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
