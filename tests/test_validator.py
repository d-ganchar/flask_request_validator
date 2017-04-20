import json
from unittest import TestCase

import flask
from flask import request

from flask_request_validator import Type
from flask_request_validator.exceptions import InvalidRequest

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
from flask_request_validator.request import FlaskRequest
from flask_request_validator.validator import VIEW, get_request_value

app = flask.Flask(__name__)
app.testing = True
app.request_class = FlaskRequest

type_composite = CompositeRule(Required(), Type(str), Enum('type1', 'type2'))


@app.route('/main/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', VIEW, Type(str), Enum('key1', 'key2')),
    Param('uuid', VIEW, Type(str), Pattern(r'^[a-z-_.]{8,10}$')),
    Param('id', GET, Type(int)),
    Param('sure', GET, Type(bool)),
    Param('sys', POST, Type(str), Required(), Pattern(r'^[a-z.]{3,6}$')),
    Param('type', POST, type_composite),
    Param('price', POST, Type(float)),
)
def route(key, uuid):
    return json.dumps({'key': key, 'uuid': uuid})


@app.route('/test/<string:key>', methods=['POST'])
def route2(key):
    return json.dumps({'key': key})


class TestValidator(TestCase):

    maxDiff = 2000

    def test_invalid_route(self):
        with app.test_client() as client:
            try:
                client.post('/main/key5/te$t', data={'type': 'wrong'})
            except InvalidRequest as e:
                expected = {
                    GET: {},
                    POST: {
                        'sys': [
                            'Value is required',
                        ],
                        'type': [
                            "Incorrect value wrong. Allowed values: ('type1', 'type2')"
                        ]
                    },
                    VIEW: {
                        'uuid': [
                            'Value te$t does not match pattern ^[a-z-_.]{8,10}$'
                        ],
                        'key': [
                            "Incorrect value key5. Allowed values: ('key1', 'key2')"
                        ]
                    }
                }

                self.assertDictEqual(expected, e.errors)

    def test_valid_route(self):
        with app.test_client() as client:
            sys_value = 'key.a'
            type_value = 'type1'
            price_value = 2.99
            client.post(
                '/main/key1/test_test?id=1&sure=True',
                data=dict(
                    sys=sys_value,
                    type=type_value,
                    price=price_value
                )
            )

            self.assertEqual(1, request.get_valid_param(GET, 'id'))
            self.assertTrue(request.get_valid_param(GET, 'sure'))
            self.assertEqual('key1', request.get_valid_param(VIEW, 'key'))
            self.assertEqual(type_value, request.get_valid_param(POST, 'type'))
            self.assertEqual(sys_value, request.get_valid_param(POST, 'sys'))
            self.assertEqual(price_value, request.get_valid_param(POST, 'price'))

    def test_invalid_get(self):
        with app.test_client() as client:

            try:
                client.post(
                    '/main/key1/test_test?id=wrong',
                    data=dict(sys='key.a', type='type1')
                )
            except InvalidRequest as e:
                expected = {
                    GET: {'id': ['Invalid type for value wrong']},
                    POST: {},
                    VIEW: {}
                }

                self.assertDictEqual(expected, e.errors)

    def test_get_request_value(self):
        with app.test_client() as client:
            client.post(
                '/test/test_key?id=1&limit=10', data=dict(type='test_type')
            )

            expected = [
                ('id', GET, u'1'),
                ('limit', GET, u'10'),
                ('key', VIEW, u'test_key'),
                ('type', POST, u'test_type'),
            ]

            for name, param_type, value in expected:
                self.assertEqual(
                    value,
                    get_request_value(param_type, name)
                )
