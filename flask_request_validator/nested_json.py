from typing import Union, Dict, List, Tuple, Any

from .exceptions import (
    NestedJsonError,
    RequiredJsonKeyError,
    JsonListItemTypeError,
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
        self.rules_map = rules_map
        self.required = required
        self.as_list = as_list  # JsonParam is list or dict

    def _check_list_item_type(self, nested: 'JsonParam', value: Any):
        """
        :raises JsonListItemTypeError
        """
        if isinstance(nested.rules_map, list):
            if value is None:
                return
            if not isinstance(value, (str, int, float, bool,)):
                raise JsonListItemTypeError(False)
        if isinstance(nested.rules_map, dict) and not isinstance(value, dict):
            raise JsonListItemTypeError()

    def _validate_list(
        self,
        value: Union[Dict, List],
        nested: 'JsonParam',
        depth: list,
        errors: List[NestedJsonError],
    ) -> Tuple[Union[Dict, List], List]:
        n_err = {}
        for ix, node in enumerate(value):  # type: int, dict or list
            try:
                self._check_list_item_type(nested, node)
            except JsonListItemTypeError as e:
                n_err = self._append_node_error(ix, n_err, e)
                continue

            if isinstance(node, dict):
                new_val, errors, sub_err = self._validate_dict(node, nested, depth, errors)
                value, sub_err = self._extend_node_errors(ix, n_err, sub_err, value, new_val)
            else:
                if isinstance(nested.rules_map, list):
                    for rule in nested.rules_map:  # type: AbstractRule
                        new_val, sub_err = rule.validate(node)
                        value, sub_err = self._extend_node_errors(
                            key=ix,
                            errors=n_err,
                            node_errors=sub_err,
                            value=value,
                            new_value=new_val,
                        )
                elif isinstance(nested.rules_map, CompositeRule):
                    new_val, sub_err = nested.rules_map.validate(value)
                    value, sub_err = self._extend_node_errors(ix, n_err, sub_err, value, new_val)

        if n_err:
            errors = self._collect_errors(depth, errors, n_err)
        return value, errors

    def _append_node_error(
        self,
        key: str or int,
        errors: Dict[str, List[BaseException]],
        error: BaseException
    ) -> Dict[str, List[BaseException]]:
        errors.setdefault(key, [])
        errors[key].append(error)
        return errors

    def _extend_node_errors(
        self,
        key: str or int,
        errors: Dict[str, List[BaseException]],
        node_errors: List[BaseException],
        value: Any,
        new_value: Any,
    ) -> Tuple[Any, Dict[str, List[BaseException]]]:
        if node_errors:
            errors.setdefault(key, [])
            errors[key].extend(node_errors)
            return value, errors
        else:
            value[key] = new_value
        return value, errors

    def _collect_errors(
        self,
        depth: list,
        errors: list,
        nested_errors: dict,
    ) -> list:
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
    ) -> Tuple[Any, List[BaseException], List[BaseException]]:
        err = dict()
        for key, rules in nested.rules_map.items():
            if key not in value:
                continue
            elif isinstance(rules, JsonParam):
                new_val, errors = self.validate(value[key], rules, depth + [key], errors)
            elif isinstance(rules, list):
                for rule in rules:  # type: AbstractRule
                    new_val, sub_err = rule.validate(value[key])
                    value, sub_err = self._extend_node_errors(key, err, sub_err, value, new_val)
            elif isinstance(rules, CompositeRule):
                new_val, sub_err = rules.validate(value[key])
                value, err = self._extend_node_errors(key, err, sub_err, value, new_val)

        return value, errors, err

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
        node_errors = dict()
        nested = nested or self
        if isinstance(nested.rules_map, dict) and not nested.as_list:
            for key, rule in nested.rules_map.items():
                try:
                    self._check_required(key, value, rule)
                except RequiredJsonKeyError as e:
                    node_errors = self._append_node_error(key, node_errors, e)

        if nested.as_list:
            value, errors = self._validate_list(value, nested, depth, errors)
        else:
            value, errors, nested_errors = self._validate_dict(value, nested, depth, errors)
            node_errors.update(nested_errors)

        errors = self._collect_errors(depth, errors, node_errors)
        return value, errors
