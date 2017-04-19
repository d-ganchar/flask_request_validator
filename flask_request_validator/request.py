from flask import Request


class FlaskRequest(Request):
    def __init__(self, environ, populate_request=True, shallow=False):
        super(FlaskRequest, self).__init__(environ, populate_request, shallow)

        self.valid_params = None
        """
        :type: ImmutableDict
        """

    def get_valid_param(self, param_type, name):
        """
        Returns value with described type after validation
        :param str param_type: GET, VIEW, POST
        :param str name:
        :return: mixed
        """
        return self.valid_params[param_type].get(name)
