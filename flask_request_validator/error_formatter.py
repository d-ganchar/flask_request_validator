from .validator import JSON, FORM, PATH, GET
from .exceptions import *


def _rules_error_to_text(error: RulesError) -> List[str]:
    errors = []
    for rule_error in error.errors:
        if isinstance(rule_error, ValueEmailError):
            errors.append('invalid email format')
        elif isinstance(rule_error, ValueDtIsoFormatError):
            errors.append('invalid datetime iso format')
        elif isinstance(rule_error, ValueEmptyError):
            errors.append('value cannot be empty')
        elif isinstance(rule_error, (ValueMinError, ValueMaxError)):
            errors.append('{val} allowed value is {val2}. include boundary: {val3}'.format(
                val='minimum' if isinstance(rule_error, ValueMinError) else 'maximum',
                val2=rule_error.value,
                val3='yes' if rule_error.include_boundary else 'no'
            ))
        elif isinstance(rule_error, (ValueMinLengthError, ValueMaxLengthError)):
            errors.append('{val} allowed length is {val2}'.format(
                val='minimum' if isinstance(rule_error, ValueMinLengthError) else 'maximum',
                val2=rule_error.length,
            ))
        elif isinstance(rule_error, ValueEnumError):
            errors.append('allowed values: {val}'.format(val=rule_error.allowed))
        elif isinstance(rule_error, ValuePatternError):
            errors.append('value does not match pattern {p}'.format(p=rule_error.pattern))
        elif isinstance(rule_error, TypeConversionError):
            errors.append('invalid type')
        elif isinstance(rule_error, RequiredValueError):
            errors.append('value is required')
        elif isinstance(rule_error, RequiredJsonKeyError):
            errors.append('json key "{key}" is required'.format(key=rule_error.key))
        elif isinstance(rule_error, JsonListItemTypeError):
            errors.append('list items must only include {val}'.format(
                val='objects' if rule_error.only_dict else 'strings or numbers',
            ))
    return errors


def demo_error_formatter(error: Union[InvalidRequestError, InvalidHeadersError]) -> list:
    result = []
    if isinstance(error, InvalidHeadersError):
        for name, rules_errors in error.errors.items():
            result.append({
                'message': 'invalid request headers {h}'.format(h=name),
                'errors': _rules_error_to_text(rules_errors),
            })
        return result

    errors_by_type = {FORM: error.form, GET: error.get, JSON: error.json, PATH: error.path}
    for err_type, errors in errors_by_type.items():
        if not errors:
            continue
        if err_type == JSON and isinstance(errors, list):
            json_errors = []
            for json_error in errors:  # type: JsonError
                keys = dict()

                for key, rules_errors in json_error.errors.items():
                    if isinstance(rules_errors, dict):  # list of nested objects
                        for ix, nested_errors in rules_errors.items():
                            keys[ix] = _rules_error_to_text(nested_errors)
                            continue
                        continue

                    keys[key] = _rules_error_to_text(rules_errors)
                json_errors.append({
                    'depth': '|'.join([str(i) for i in json_error.depth]),
                    'keys': keys,
                })

            result.append({
                'message': 'invalid {err_type} parameters'.format(err_type=err_type),
                'errors': json_errors
            })

            continue

        result.append({
            'message': 'invalid {err_type} parameters'.format(err_type=err_type),
            'errors': {
                key: _rules_error_to_text(rules_errors)
                for key, rules_errors in errors.items()
            }
        })

    return result
