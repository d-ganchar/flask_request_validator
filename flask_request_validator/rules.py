import numbers
import re
import sys
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime

from .dt_utils import dt_from_iso
from .exceptions import *

REGEX_EMAIL = r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$"


class AbstractRule(ABC):
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """
        The returned value does not have to match the input value.
        Feel free to implement conversion logic.

        :param Any value:
        :raises:
            TypeConversionError: when a value type is incorrect. skips logical checks
            RuleError: if TypeConversionError was not raised but logic restrictions
        """
        pass


class CompositeRule(AbstractRule):
    def __init__(self, *rules: AbstractRule) -> None:
        type_checkers = (Number, BoolRule, IntRule, FloatRule)
        rules_by_priority = sorted(rules, key=lambda x: 0 if isinstance(x, type_checkers) else 1)
        if len(rules_by_priority) > 1 and isinstance(rules_by_priority[1], type_checkers):
            raise WrongUsageError(f'You can use only 1 type. '
                                  f'Choose one of: {", ".join([t.__name__ for t in type_checkers])}')

        self._rules = rules_by_priority

    def __iter__(self):
        for rule in self._rules:
            yield rule

    def validate(self, value: Any) -> Any:
        """
        :raises RulesError:
        """
        errors = []
        new_value = deepcopy(value)
        for rule in self._rules:
            try:
                new_value = rule.validate(value=new_value)
            except TypeConversionError as e:
                errors.append(e)
                break
            except RuleError as e:
                errors.append(e)

        if errors:
            raise RulesError(*errors)
        return new_value


class Pattern(AbstractRule):
    def __init__(self, pattern: str) -> None:
        self._pattern = re.compile(pattern)

    def validate(self, value: str) -> str:
        if not self._pattern.search(string=str(value)):
            raise ValuePatternError(self._pattern.pattern)
        return value


class Enum(AbstractRule):
    def __init__(self, *allowed_values: Any) -> None:
        self._allowed_values = allowed_values

    def validate(self, value: Any) -> Any:
        if value not in self._allowed_values:
            raise ValueEnumError(self._allowed_values)
        return value


class MaxLength(AbstractRule):
    def __init__(self, length: int) -> None:
        self._length = length

    def validate(self, value: Union[Iterable, str]) -> Any:
        if len(value) > self._length:
            raise ValueMaxLengthError(self._length)
        return value


class MinLength(AbstractRule):
    def __init__(self, length: int) -> None:
        self._length = length

    def validate(self, value: Union[Iterable, str]) -> Any:
        if len(value) < self._length:
            raise ValueMinLengthError(self._length)
        return value


class NotEmpty(AbstractRule):
    def validate(self, value: str) -> str:
        value = value.strip()
        if value == '':
            raise ValueEmptyError()
        return value


class Max(AbstractRule):
    def __init__(self, value: Union[int, float], include_boundary: bool = True) -> None:
        """
            >>> Max(7, True).validate(7)
            True
            >>> Max(7, False).validate(7)
            False
            >>> Max(7, False).validate(6.999)
            True
        """
        self._value = value
        self._include_boundary = include_boundary

    def validate(self, value: Union[int, float]) -> Union[int, float]:
        if value > self._value and self._include_boundary:
            raise ValueMaxError(self._value, self._include_boundary)
        elif value >= self._value and not self._include_boundary:
            raise ValueMaxError(self._value, self._include_boundary)

        return value


class Min(AbstractRule):
    def __init__(self, value: Union[int, float], include_boundary: bool = True) -> None:
        """
            >>> Min(7, True).validate(7)
            True
            >>> Min(7, False).validate(7)
            False
            >>> Min(7, False).validate(7.001)
            True
        """
        self._value = value
        self._include_boundary = include_boundary

    def validate(self, value: Union[int, float]) -> Union[int, float]:
        if value < self._value and self._include_boundary:
            raise ValueMinError(self._value, self._include_boundary)
        elif value <= self._value and not self._include_boundary:
            raise ValueMinError(self._value, self._include_boundary)
        return value


class IsDatetimeIsoFormat(AbstractRule):
    def validate(self, value: str) -> datetime:
        try:
            if sys.version_info >= (3, 7):
                value = datetime.fromisoformat(value[:-1] if value.endswith('Z') else value)
            else:
                value = dt_from_iso(value[:-1] if value.endswith('Z') else value)
        except (TypeError, ValueError, AttributeError):
            raise ValueDtIsoFormatError()
        return value


class IsEmail(AbstractRule):
    def validate(self, value: str) -> str:
        if not re.fullmatch(pattern=REGEX_EMAIL, string=value):
            raise ValueEmailError()
        return value


class Datetime(AbstractRule):
    def __init__(self, dt_format: str) -> None:
        self._dt_format = dt_format

    def validate(self, value: str) -> datetime:
        try:
            return datetime.strptime(value, self._dt_format)
        except ValueError:
            raise ValueDatetimeError(self._dt_format)


class Number(AbstractRule):
    def validate(self, value: Any) -> Any:
        if not isinstance(value, numbers.Number):
            raise NumberError()
        return value


class IntRule(AbstractRule):
    """
    >>> IntRule().validate(7)
    7
    >>> IntRule().validate('7')
    7   # int
    """
    def __init__(self, str_to_int: bool = True) -> None:
        self._str_to_int = str_to_int

    def validate(self, value: Any) -> Any:
        if isinstance(value, int):
            return value

        if isinstance(value, str) and self._str_to_int:
            try:
                return int(value)
            except ValueError:
                pass

        raise TypeConversionError()


class FloatRule(AbstractRule):
    """
    >>> FloatRule().validate(9.99)
    9.99
    >>> FloatRule({','}).validate('9.99')
    9.99   # float
    """
    def __init__(self, delimiters: set = None) -> None:
        self._delimiters = delimiters or {}

    def validate(self, value: Any) -> Any:
        if isinstance(value, float):
            return value

        if isinstance(value, str):
            for char in self._delimiters:
                try:
                    return float(value.replace(char, '.', 1))
                except ValueError:
                    pass

        raise TypeConversionError()


class BoolRule(AbstractRule):
    """
    >>> BoolRule().validate(True)
    True
    >>> BoolRule().validate(False)
    False
    >>> BoolRule(yes={'plus'}).validate('PluS')
    True  # bool
    >>> BoolRule(yes={1}).validate(1)
    True  # bool
    >>> BoolRule(no={'no'}).validate('No')
    False  # bool
    >>> BoolRule(no={0}).validate(0)
    False  # bool
    """
    def __init__(self, yes: set = None, no: set = None) -> None:
        self._yes = yes or set()
        self._no = no or set()

    def validate(self, value: Any) -> Any:
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            for yes in self._yes:
                if yes == value:
                    return True

            for no in self._no:
                if no == value:
                    return False

        if isinstance(value, str):
            low_val = value.lower()
            for yes in self._yes:
                if yes == low_val:
                    return True

            for no in self._no:
                if no == low_val:
                    return False

        raise TypeConversionError()
