import json
from unittest import TestCase
from urllib.parse import urlencode

import flask
from flask import Response
from flask_restful import Api, Resource
from parameterized import parameterized

from flask_request_validator import GET, Param, validate_params, ValidRequest
from flask_request_validator.exceptions import *
from flask_request_validator.rules import *
from flask_request_validator.validator import FORM, HEADER, JSON, PATH

app = flask.Flask(__name__)
test_api = Api(app, '/v1')

app.testing = True


@test_api.resource('/validator')
class TestApi(Resource):
    @validate_params(
        Param('key', JSON, int),
        Param('sure', JSON, bool)
    )
    def put(self, key, sure):
        return Response(
            json.dumps([
                [key, key.__class__.__name__],
                [sure, sure.__class__.__name__],
            ]),
            mimetype='application/json'
        )

    @validate_params(
        Param('cities', GET, list),
        Param('countries', GET, dict)
    )
    def get(self, cities, countries):
        return Response(
            json.dumps({
                'cities': [cities, cities.__class__.__name__],
                'countries': [countries, countries.__class__.__name__],
            }),
            mimetype='application/json'
        )


@app.route('/form/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', PATH, str, rules=[Enum('key1', 'key2')]),
    Param('uuid', PATH, str, rules=CompositeRule(Pattern(r'^[a-z-_.]{8,10}$'), MinLength(6))),
    Param('sure', GET, bool, True),
    Param('music', GET, list, True),
    Param('cities', GET, dict, True),
    Param('price', GET, float, True),
    Param('cost', GET, int, True),
    Param('default1', GET, int, False, 10),
    Param('flag', FORM, bool, True),
    Param('bands', FORM, list, True),
    Param('countries', FORM, dict, True),
    Param('number', FORM, float, True),
    Param('count', FORM, int, True),
    Param('default2', FORM, int, False, 20),
)
def route_form(valid: ValidRequest, key: str, uuid: str):
    return flask.jsonify({
        FORM: valid.get_form(),
        GET: valid.get_params(),
        PATH: valid.get_path_params(),
    })


class TestRoutes(TestCase):
    @parameterized.expand([
        # empty
        (
            {},
            '/form/bad_key/bad_uid',
            {},
            {
                GET: {
                    'sure': RequiredValueError,
                    'music': RequiredValueError,
                    'cities': RequiredValueError,
                    'price': RequiredValueError,
                    'cost': RequiredValueError,
                },
                PATH: {
                    'key': [RulesError, [ValueEnumError]],
                    'uuid': [RulesError, [ValuePatterError, ValueMinLengthError]],
                },
                JSON: {},
                FORM: {
                    'flag': RequiredValueError,
                    'bands': RequiredValueError,
                    'countries': RequiredValueError,
                    'number': RequiredValueError,
                    'count': RequiredValueError,
                },
                HEADER: {},
            },
            {},
        ),
        # wrong types
        (
            {
                'sure': 'bad_bool',
                'cities': 'wrong_dict',
                'price': 'string',
                'cost': 'string',
                'music': None,
            },
            '/form/key1/qwerty1234',
            {
                'flag': 'bad_bool',
                'countries': 'wrong_dict',
                'number': 'string',
                'count': 'string',
                'bands': None,
            },
            {
                GET: {
                    'price': TypeConversionError,
                    'cost': TypeConversionError,
                },
                PATH: {},
                JSON: {},
                FORM: {
                    'bands': TypeConversionError,
                    'number': TypeConversionError,
                    'count': TypeConversionError,
                },
                HEADER: {},
            },
            {
                GET: {},
                PATH: {},
                JSON: {},
                HEADER: {},
            },
        ),
        # valid
        (
            {
                'sure': '1',
                'cities': 'Germany:Dresden,Belarus:Grodno',
                'price': 1.01,
                'cost': 2,
                'music': 'sigur ros,yndi halda',
            },
            '/form/key1/test_test',
            {
                'flag': 'False',
                'countries': 'Belarus:Minsk,Germany:Berlin',
                'number': 2.03,
                'count': 3,
                'bands': 'mono,calm blue sea',
            },
            {},
            {
                FORM: {
                    'bands': ['mono', 'calm blue sea'],
                    'count': 3,
                    'countries': {'Belarus': 'Minsk', 'Germany': 'Berlin'},
                    'default2': 20,
                    'flag': False,
                    'number': 2.03,
                },
                GET: {
                    'cities': {'Germany': 'Dresden', 'Belarus': 'Grodno'},
                    'cost': 2,
                    'default1': 10,
                    'music': ['sigur ros', 'yndi halda'],
                    'price': 1.01,
                    'sure': True,
                },
                PATH: {'key': 'key1', 'uuid': 'test_test'},
            }
        ),
    ])
    def test_form(self, get, route, form, exp, response):
        with app.test_client() as client:
            try:
                result = client.post(route + '?' + urlencode(get, doseq=True), data=form).json
            except InvalidRequestError as e:
                for k, exception in e.errors.items():
                    if isinstance(exception, RulesError):
                        for rule_ix in range(len(exception.errors)):
                            self.assertTrue(isinstance(exception.errors[rule_ix], exp[k][rule_ix]))
                return
        self.assertEqual(response, result)


class TestParam(TestCase):
    @parameterized.expand([
        # param_type
        (GET, None, False, None, None),
        (PATH, None, True, None, None),
        (JSON, None, False, None, None),
        (FORM, None, True, None, None),
        (HEADER, None, False, None, None),
        ('undefined', None, True, None, True),
        # value_type
        (JSON, str, False, None, None),
        (FORM, bool, True, None, None),
        (JSON, int, False, None, None),
        (FORM, float, True, None, None),
        (JSON, dict, False, None, None),
        (GET, list, True, None, None),
        (JSON, object, False, None, True),
        (GET, 'bad_type', True, None, True),
        # required
        (JSON, str, True, '1', True),
        (JSON, list, True, lambda x: [1, 2, 3], True),
    ])
    def test_init_wrong_usage(self, param_type, value_type, required, default, err):
        if err:
            self.assertRaises(WrongUsageError, Param, param_type, value_type, required, default)
            return
        Param('name', param_type, value_type, required, default, [])

    @parameterized.expand([
        # GET
        (Param('test', GET, int), 1, '1'),
        (Param('test', GET, bool), True, 'true'),
        (Param('test', GET, bool), True, 'True'),
        (Param('test', GET, bool), False, '0'),
        (Param('test', GET, bool), False, 'false'),
        (Param('test', GET, bool), False, 'False'),
        (Param('test', GET, list), ['Minsk', 'Prague', 'Berlin'], 'Minsk, Prague, Berlin'),
        (
            Param('test', GET, dict),
            {'country': 'Belarus', 'capital': 'Minsk'},
            'country: Belarus, capital: Minsk',
        ),
        # FORM
        (Param('test', FORM, int), 1, '1'),
        (Param('test', FORM, list), ['Minsk', 'Prague', 'Berlin'], 'Minsk, Prague, Berlin'),
        (
            Param('test', FORM, dict),
            {'country': 'Belarus', 'capital': 'Minsk'},
            'country: Belarus, capital: Minsk',
        ),
        (Param('test', FORM, bool), True, 'true'),
        (Param('test', FORM, bool), True, 'True'),
        (Param('test', FORM, bool), False, '0'),
        (Param('test', FORM, bool), False, 'false'),
        (Param('test', FORM, bool), False, 'False'),
    ])
    def test_value_to_type(self, param, expected, value):
        self.assertEqual(param.value_to_type(value), expected)

# class TestRestfull(TestCase):
#
#     @parameterized.expand([
#         ({'sure': str(True)}, ),
#         ({'key': 1}, ),
#     ])
#     def test_put_raises(self, data):
#         with app.test_client() as client:
#             with self.assertRaises(InvalidRequest):
#                 client.put(
#                     '/v1/resource',
#                     data=json.dumps(data),
#                     content_type='application/json'
#                 )
#
#     def test_put_ok(self):
#         key = 1
#         sure = True
#
#         with app.test_client() as client:
#             data = client.put(
#                 '/v1/resource',
#                 data=json.dumps(dict(sure=sure, key=key)),
#                 content_type='application/json'
#             )
#             self.assertEqual(
#                 json.loads(data.get_data(as_text=True)),
#                 [
#                     [key, key.__class__.__name__],
#                     [sure, sure.__class__.__name__],
#                 ]
#             )
#
#     def test_get_ok(self):
#         cities = ['Minsk', 'Tbilisi', ]
#         countries = {'belarus': 'minsk', 'georgia': 'tbilisi'}
#         with app.test_client() as client:
#             data = client.get(
#                 '/v1/resource?' + urlencode({
#                     'cities': ','.join(cities),
#                     'countries': 'belarus:minsk,georgia:tbilisi'
#                 }),
#             )
#
#             self.assertDictEqual(
#                 json.loads(data.get_data(as_text=True)),
#                 {
#                     'cities': [cities, cities.__class__.__name__],
#                     'countries': [countries, countries.__class__.__name__],
#                 }
#             )
#
#
# class TestValidateHttpHeader(TestCase):
#     def test_valid_header(self):
#         with app.test_client() as client:
#             username = 'Max'
#             password = '12345'
#             data = {
#                 'username': username,
#                 'password': password,
#             }
#             res = client.get('/header', headers=data)
#             self.assertEqual(200, res.status_code)
#             self.assertEqual({username: password}, res.json)
#
#     def test_invalid_header(self):
#         with app.test_client() as client:
#             username = 'Max'
#             password = '123'
#             data = {
#                 'username': username,
#                 'password': password,
#             }
#             with self.assertRaises(expected_exception=InvalidHeader):
#                 client.get('/header', headers=data)
#
#
# class TestNestedJson(TestCase):
#
#     def test_nested_json(self):
#         with app.test_client() as client:
#             client.post(
#                 '/nested_json',
#                 data=json.dumps({
#                     'country': 'Germany',
#                     'city': 'Dresden',
#                     'street': 'Rampische',
#                     'meta': {
#                         'buildings': {
#                             'warehouses': {
#                                 'small': {'count': 100, },
#                                 'large': 0,
#                             },
#                         },
#                     },
#                 }),
#                 content_type='application/json'
#             )
