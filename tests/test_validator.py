import json
from unittest import TestCase

import flask
from flask.ext.request_validator.exceptions import InvalidRequest

from flask_request_validator import CompositeRule
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


type_composite = CompositeRule(Required(), Enum('type1', 'type2'))


@app.route('/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', GET, Enum('key1', 'key2')),
    Param('uuid', GET, Pattern(r'^[a-z-_.]{8,10}$')),
    Param('sys', POST, Required(), Pattern(r'^[a-z.]{3,6}$')),
    Param('type', POST, type_composite),
)
def route(key, uuid):
    return json.dumps({'key': key, 'uuid': uuid})


class TestValidator(TestCase):

    maxDiff = 2000

    def test_invalid_route(self):
        with app.test_client() as client:
            try:
                client.post('/key5/te$t', data={'type': 'wrong'})
            except InvalidRequest as e:
                expected = dict(
                    post=dict(
                        sys=[
                            'Value is required',
                        ],
                        type=[
                            "Incorrect value wrong. Allowed values: ('type1', 'type2')"
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
