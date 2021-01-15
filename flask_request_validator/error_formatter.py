from .validator import JSON, FORM, PATH, GET
from .exceptions import *


def demo_error_formatter(error: Union[InvalidRequestError, InvalidHeadersError]) -> list:
    if isinstance(error, InvalidHeadersError):
        return [str(error)]

    result = []
    errors_by_type = {FORM: error.form, GET: error.get, JSON: error.json, PATH: error.path}
    for err_type, errors in errors_by_type.items():  # type: str, dict
        if not errors:
            continue

        item = {'message': 'invalid {err_type} parameters'.format(err_type=err_type)}
        if isinstance(errors, list):
            # nested json
            sub_errors = []
            for json_er in errors:  # type: JsonError
                node_error = {'path': '|'.join(str(d) for d in json_er.depth)}
                for obj_key, child_errors in json_er.errors.items():
                    if isinstance(child_errors, RulesError):
                        node_error.setdefault('keys', dict())
                        node_error['keys'][obj_key] = str(child_errors)
                        continue

                    node_error.setdefault('objects', dict())
                    for ix, field_errors in child_errors.items():
                        node_error['objects'][obj_key] = {ix: str(field_errors)}
                sub_errors.append(node_error)
        else:
            sub_errors = {
                str(err_key): str(sub_error)
                for err_key, sub_error in errors.items()
            }

        item['errors'] = sub_errors
        result.append(item)

    return result
