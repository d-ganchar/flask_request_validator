import re
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Union

ALLOWED_TYPES = (str, bool, int, float, dict, list)
REGEX_EMAIL = r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$"


class AbstractRule(ABC):
    @abstractmethod
    def validate(self, value: Any) -> List[str]:
        """
            Validate value and return a list of errors.
            The error list should be empty if value is valid.
        """


class CompositeRule(AbstractRule):
    def __init__(self, *rules: AbstractRule) -> None:
        self._rules = rules

    def __iter__(self):
        for rule in self._rules:
            yield rule

    def validate(self, value: Any) -> List[str]:
        errors = []
        for rule in self._rules:
            errors.extend(rule.validate(value=value))
        return errors


class Pattern(AbstractRule):

    def __init__(self, pattern: str) -> None:
        self._pattern = re.compile(pattern)

    def validate(self, value: str) -> List[str]:
        errors = []

        if not self._pattern.search(string=str(value)):
            errors.append(f'Value "{value}" does not match pattern {self._pattern.pattern}')

        return errors


class Enum(AbstractRule):

    def __init__(self, *allowed_values: List[Any]) -> None:
        self._allowed_values = allowed_values

    def validate(self, value: Any) -> List[str]:
        errors = []

        if value not in self._allowed_values:
            errors.append(f'Incorrect value "{value}". Allowed values: {self._allowed_values}')

        return errors


class MaxLength(AbstractRule):

    def __init__(self, length: int) -> None:
        self._length = length

    def validate(self, value: Union[Iterable, str]) -> List[str]:
        errors = []

        if len(value) > self._length:
            errors.append(f'Invalid length for value "{value}". Max length = {self._length}')

        return errors


class MinLength(AbstractRule):

    def __init__(self, length: int) -> None:
        self._length = length

    def validate(self, value: Union[Iterable, str]) -> List[str]:
        errors = []

        if len(value) < self._length:
            errors.append(f'Invalid length for value "{value}". Min length = {self._length}')

        return errors


class NotEmpty(AbstractRule):
    def validate(self, value: str) -> List[str]:
        errors = []
        value = value.strip()

        if value == '':
            errors.append('Got empty String which is invalid')

        return errors


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

    def validate(self, value: Union[int, float]) -> List[str]:
        errors = []

        if value > self._value and self._include_boundary:
            errors.append(f'greater then allowed: {value} is not <= {self._value}')
        elif value >= self._value and not self._include_boundary:
            errors.append(f'greater then allowed: {value} is not < {self._value}')

        return errors


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

    def validate(self, value: Union[int, float]) -> List[str]:
        errors = []

        if value < self._value and self._include_boundary:
            errors.append(f'smaller then allowed: {value} is not >= {self._value}')
        elif value <= self._value and not self._include_boundary:
            errors.append(f'smaller then allowed: {value} is not > {self._value}')

        return errors


class IsEmail(AbstractRule):

    def validate(self, value: str) -> List[str]:
        errors = []

        if not re.fullmatch(pattern=REGEX_EMAIL, string=value):
            errors.append(f'invalid email address: {value}')

        return errors
