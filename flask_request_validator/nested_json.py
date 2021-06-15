from typing import Union, Dict, List, Tuple, Any

from .exceptions import (
    JsonError,
    RequiredJsonKeyError,
    JsonListItemTypeError,
    RulesError, JsonListExpectedError, JsonDictExpectedError,
)
from .rules import CompositeRule, AbstractRule


class JsonParam:
    """
    Nested json validation
    """
    def __init__(
        self,
        rules_map: Union[
            Dict[str, Union[Dict, List, CompositeRule, 'JsonParam']],
            Union[CompositeRule, List[AbstractRule]],
        ],
        required: bool = True,
        as_list: bool = False,
    ) -> None:
        if isinstance(rules_map, list):
            self.rules_map = CompositeRule(*rules_map)
        else:
            for k, rules in rules_map.items():
                if isinstance(rules, list):
                    rules_map[k] = CompositeRule(*rules)
            self.rules_map = rules_map

        self.required = required
        self.as_list = as_list  # JsonParam is list or dict

    def _check_list_item_type(self, nested: 'JsonParam', value: Any):
        """
        :raises JsonListItemTypeError
        """
        if isinstance(nested.rules_map, CompositeRule):
            if value is None:
                return
            if not isinstance(value, (str, int, float, bool,)):
                raise JsonListItemTypeError(False)
            return
        if isinstance(nested.rules_map, dict) and not isinstance(value, dict):
            raise JsonListItemTypeError()

    def _validate_list(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam',
        depth: list,
        errors: List[JsonError],
    ) -> Tuple[Union[Dict, List], List]:
        n_err = {}
        for ix, node in enumerate(value):  # type: int, dict or list
            try:
                self._check_list_item_type(nested, node)
            except JsonListItemTypeError as e:
                n_err[ix] = e
                continue

            if isinstance(node, dict):
                item_value, errors, rules_err = self._validate_dict(node, nested, depth, errors)
                if rules_err:
                    n_err[ix] = rules_err
                else:
                    value[ix] = item_value
                continue

            try:
                new_val = nested.rules_map.validate(value[ix])
                value[ix] = new_val
            except RulesError as e:
                n_err[ix] = e

        if n_err:
            errors = self._collect_errors(depth, errors, n_err, nested.as_list)
        return value, errors

    def _collect_errors(
        self,
        depth: list,
        errors: list,
        nested_errors: dict,
        as_list: bool = False,
    ) -> list:
        if nested_errors:
            try:
                raise JsonError(depth, nested_errors, as_list)
            except JsonError as e:
                errors.append(e)
        return errors

    def _validate_dict(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam',
        depth: list,
        errors: List[JsonError],
    ) -> Tuple[Any, List[JsonError], Dict[str, RulesError]]:
        err = dict()
        for key, rules in nested.rules_map.items():
            if key not in value:
                continue
            elif isinstance(rules, JsonParam):
                new_val, errors = self.validate(value[key], rules, depth + [key], errors)
                continue

            try:
                new_val = rules.validate(value[key])
                value[key] = new_val
            except RulesError as e:
                err[key] = e

        return value, errors, err

    def _check_required(self, key: str, value: dict, rule: Any):
        """
        :raises RequiredJsonKeyError
        """
        if isinstance(rule, JsonParam) and rule.required and key not in value:
            raise RequiredJsonKeyError(key)

    def _check_as_list_value(self, nested: 'JsonParam', value: Any, depth: list):
        if nested.as_list and not isinstance(value, list):
            raise JsonListExpectedError(depth)
        if not nested.as_list and not isinstance(value, dict):
            raise JsonListExpectedError(depth)

    def validate(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam' = None,
        depth: list = None,
        errors: List[JsonError] = None,
    ) -> Tuple[Union[Dict, List], List]:
        depth = depth or ['root']
        errors = errors or []
        node_errors = dict()
        nested = nested or self

        try:
            self._check_as_list_value(nested, value, depth)
        except (JsonListExpectedError, JsonDictExpectedError) as e:
            errors.append(e)
            return value, errors

        if nested.as_list:
            value, errors = self._validate_list(value, nested, depth, errors)
            return value, errors

        if isinstance(nested.rules_map, dict):
            for key, rule in nested.rules_map.items():
                try:
                    self._check_required(key, value, rule)
                except RequiredJsonKeyError as e:
                    node_errors[key] = e

        value, errors, nested_errors = self._validate_dict(value, nested, depth, errors)
        node_errors.update(nested_errors)
        errors = self._collect_errors(depth, errors, node_errors)
        return value, errors
