import json
from unittest import TestCase

import flask
from flask.ext.request_validator.exceptions import InvalidRequest

from flask_request_validator import (
    Enum,
    GET,
    POST,
    Param,
    Pattern,
    Required,
    validate_params
)


app = flask.Flask(__name__)
app.testing = True


@app.route('/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', GET, Enum('key1', 'key2')),
    Param('uuid', GET, Pattern(r'^[a-z-_.]{8,10}$')),
    Param('sys', POST, Required(), Pattern(r'^[a-z.]{3,6}$')),
    Param('type', POST, Enum('type1', 'type2')),
)
def route(key, uuid):
    return json.dumps({'key': key, 'uuid': uuid})


class TestValidator(TestCase):

    def test_invalid_route(self):
        with app.test_client() as client:
            try:
                client.post('/key5/te$t')
            except InvalidRequest as e:
                expected = dict(
                    post=dict(
                        sys=[
                            'Value is required',
                            'Value None does not match pattern ^[a-z.]{3,6}$'
                        ],
                        type=[
                            "Incorrect value None. Allowed values: ('type1', 'type2')"
                        ]
                    ),
                    get=dict(
                        uuid=[
                            'Value te$t does not match pattern ^[a-z-_.]{8,10}$'
                        ],
                        key=[
                            "Incorrect value key5. Allowed values: ('key1', 'key2')"
                        ]
                    )
                )

                self.assertDictEqual(expected, e.errors)

    def test_valid_route(self):
        with app.test_client() as client:
            client.post('/key1/test_test', data=dict(sys='key.a', type='type1'))
