from .validator import JSON, FORM, PATH, GET
from .exceptions import *


def demo_error_formatter(error: Union[InvalidRequestError, InvalidHeadersError, AfterParamError]) -> list:
    """
    Just demo. !!! not supported !!!
    """
    if isinstance(error, (InvalidHeadersError, AfterParamError)):
        return [str(error)]

    result = []
    errors_by_type = {FORM: error.form, GET: error.get, JSON: error.json, PATH: error.path}
    for err_type, errors in errors_by_type.items():  # type: str, dict
        if not errors:
            continue

        item = {'message': 'invalid {err_type} parameters'.format(err_type=err_type)}
        if isinstance(errors, list):
            sub_errors = []
            for json_er in errors:  # type: JsonError
                path_error = {'path': '|'.join(str(d) for d in json_er.depth)}
                if json_er.as_list:
                    path_error['list_items'] = dict()
                    for ix, field_errors in json_er.errors.items():
                        path_error['list_items'][ix] = dict()
                        if isinstance(field_errors, RulesError):
                            path_error['list_items'][ix] = str(field_errors)
                            continue
                        for sub_key, sub_node_er in field_errors.items():
                            path_error['list_items'][ix][sub_key] = str(sub_node_er)
                else:
                    for obj_key, child_errors in json_er.errors.items():
                        path_error.setdefault('keys', dict())
                        path_error['keys'][obj_key] = str(child_errors)

                sub_errors.append(path_error)
        else:
            sub_errors = {
                str(err_key): str(sub_error)
                for err_key, sub_error in errors.items()
            }

        item['errors'] = sub_errors
        result.append(item)

    return result
