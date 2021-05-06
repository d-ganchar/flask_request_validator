import re
import sys
import numbers
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable

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
            :raises RuleError:
        """
        pass


class CompositeRule(AbstractRule):
    def __init__(self, *rules: AbstractRule) -> None:
        self._rules = rules

    def __iter__(self):
        for rule in self._rules:
            yield rule

    def validate(self, value: Any) -> Any:
        """
        :raises RulesError:
        """
        errors = []
        new_value = value
        for rule in self._rules:
            try:
                new_value = rule.validate(value=value)
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
            raise NumberError
        return value
