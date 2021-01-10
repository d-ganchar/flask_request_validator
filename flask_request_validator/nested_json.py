from typing import Union, Dict, List, Tuple, Any

from .exceptions import NestedJsonError, RequiredJsonKeyError
from .rules import CompositeRule, AbstractRule


class JsonParam:
    """
    Nested json validation
    """
    def __init__(
        self,
        rules_map: Dict[str, Union[Dict, List, CompositeRule, 'JsonParam']],
        required: bool = True,
        as_list: bool = False,
    ) -> None:
        self.rules_map = rules_map
        self.required = required
        self.as_list = as_list

    def _validate_list(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam',
        depth: list,
        errors: List[NestedJsonError],
    ) -> Tuple[Union[Dict, List], List]:
        valid_value = value

        for ix, node in enumerate(value):  # type: int, dict
            valid_value, errors, dict_errors = self._validate_dict(node, nested, depth, errors)
            if dict_errors:
                self._collect_errors(depth + [ix], errors, dict_errors)

        return valid_value, errors

    def _collect_errors(self, depth: list, errors: list, nested_errors: list) -> list:
        if nested_errors:
            try:
                raise NestedJsonError(depth, nested_errors)
            except NestedJsonError as e:
                errors.append(e)
        return errors

    def _validate_dict(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam',
        depth: list,
        errors: List[NestedJsonError],
    ) -> Tuple[Union[Dict, List], List, List]:
        dict_errors = []
        valid_value = value
        for key, rules in nested.rules_map.items():
            if key not in value:
                continue
            elif isinstance(rules, JsonParam):
                valid_value, errors = self.validate(value[key], rules, depth + [key])
            elif isinstance(rules, list):
                for rule in rules:  # type: AbstractRule
                    valid_value, rules_errors = rule.validate(value[key])
                    dict_errors.extend(rules_errors)
            elif isinstance(rules, CompositeRule):
                valid_value, rules_errors = rules.validate(value[key])
                dict_errors.extend(rules_errors)

        return valid_value, errors, dict_errors

    def _check_required(self, key: str, value: dict, rule: Any):
        """
        :raises RequiredJsonKeyError
        """
        if isinstance(rule, JsonParam) and rule.required and key not in value:
            raise RequiredJsonKeyError(key)

    def validate(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam' = None,
        depth: list = None,
        errors: List[NestedJsonError] = None,
    ) -> Tuple[Union[Dict, List], List]:
        depth = depth or ['root']
        errors = errors or []
        node_errors = []
        nested = nested or self
        for key, rule in nested.rules_map.items():
            try:
                self._check_required(key, value, rule)
            except RequiredJsonKeyError as e:
                node_errors.append(e)

        if nested.as_list:
            valid_value, errors = self._validate_list(value, nested, depth, errors)
        else:
            valid_value, errors, nested_errors = self._validate_dict(value, nested, depth, errors)
            node_errors.extend(nested_errors)

        errors = self._collect_errors(depth, errors, node_errors)
        return valid_value, errors
