import json
from unittest import TestCase
from urllib.parse import urlencode

import flask
from flask_restful import Api
from parameterized import parameterized

from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.rules import *
from flask_request_validator.validator import *

_app = flask.Flask(__name__)
_test_api = Api(_app, '/v1')

_app.testing = True
_VALID_HEADERS = {
    'Authorization': 'Bearer token',
    'Custom header': 'custom value',
}


@_app.route('/form/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('Authorization', HEADER, str, rules=[Enum('Bearer token')]),
    Param('Custom header', HEADER, str, rules=[Enum('custom value')]),
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


@_app.route('/json', methods=['POST'])
@validate_params(
    Param('Authorization', HEADER, str, rules=[Enum('Bearer token')]),
    Param('Custom header', HEADER, str, rules=[Enum('custom value')]),
    Param('email', JSON, str, rules=[IsEmail()]),
    Param('number', JSON, float),
    Param('user', JSON, str, rules=CompositeRule(Pattern(r'^[a-z]{8,10}$'))),
)
def route_json(valid: ValidRequest):
    return flask.jsonify({JSON: valid.get_json()})


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
                    'uuid': [RulesError, [ValuePatternError, ValueMinLengthError]],
                },
                FORM: {
                    'flag': RequiredValueError,
                    'bands': RequiredValueError,
                    'countries': RequiredValueError,
                    'number': RequiredValueError,
                    'count': RequiredValueError,
                },
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
                FORM: {
                    'bands': RequiredValueError,
                    'number': TypeConversionError,
                    'count': TypeConversionError,
                },
            },
            {},
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
    def test_form_with_headers(self, get, route, form, exp, response):
        with _app.test_client() as client:
            try:
                result = client.post(
                    route + '?' + urlencode(get, doseq=True),
                    data=form,
                    headers=_VALID_HEADERS,
                ).json
            except InvalidRequestError as e:
                for param_type, errors_by_key in exp.items():  # type: str, dict
                    for k, exception in getattr(e, param_type.lower()).items():
                        if isinstance(exception, RulesError):
                            for rule_ix in range(len(exception.errors)):
                                self.assertTrue(isinstance(exception.errors[rule_ix],
                                                           exp[param_type][k][1][rule_ix]))
                        else:
                            self.assertTrue(isinstance(exception, exp[param_type][k]))
                return
        self.assertEqual(response, result)

    @parameterized.expand([
        # empty all
        ({}, {}),
        # email only
        ({'email': 'test@gmail.com'}, {}),
        # number only
        ({'number': 8.64}, {}),
        # user only
        ({'user': 'qwertyuio'}, {}),
        # wrong number
        ({'email': 'test@gmail.com', 'number': 'abc', 'user': 'qwertyuio'}, {}),
        # valid
        (
            {'email': 'test@gmail.com', 'number': 8.64, 'user': 'qwertyuio'},
            {'email': 'test@gmail.com', 'number': 8.64, 'user': 'qwertyuio'},
        ),
    ])
    def test_json_param(self, data, expected):
        with _app.test_client() as client:
            if expected:
                result = client.post(
                    '/json',
                    data=json.dumps(data),
                    headers=_VALID_HEADERS,
                    content_type='application/json',
                ).json
                self.assertDictEqual(result, {JSON: expected})
            else:
                self.assertRaises(
                    InvalidRequestError,
                    client.post,
                    '/json',
                    data=json.dumps(data),
                    headers=_VALID_HEADERS,
                    content_type='application/json',
                )

    @parameterized.expand([
        # invalid
        (
            {},
            {
                'Authorization': RequiredValueError,
                'Custom header': RequiredValueError,
            },
        ),
        (
            {
                'Authorization': 'Bearer token',
            },
            {
                'Custom header': RequiredValueError,
            },
        ),
        (
            {
                'Custom header': 'custom value',
            },
            {
                'Authorization': RequiredValueError,
            },
        ),
        # valid headers
        (_VALID_HEADERS, {}, ),
    ])
    def test_headers(self, headers, exp):
        with _app.test_client() as client:
            for route in ('/form/key1/test_test', '/json'):
                try:
                    client.post(route, headers=headers)
                except InvalidHeadersError as e:
                    self.assertEqual(len(exp), len(e.errors))
                    for k, err in e.errors.items():
                        self.assertTrue(isinstance(err, exp[k]))
                except InvalidRequestError:
                    return


class TestParam(TestCase):
    @parameterized.expand([
        # param_type
        (GET, None, False, None, None),
        (PATH, None, True, None, None),
        (FORM, None, False, None, None),
        (FORM, None, True, None, None),
        (HEADER, None, False, None, None),
        ('undefined', None, True, None, True),
        # value_type
        (FORM, str, False, None, None),
        (FORM, bool, True, None, None),
        (FORM, int, False, None, None),
        (FORM, float, True, None, None),
        (GET, dict, False, None, None),
        (GET, list, True, None, None),
        (GET, object, False, None, True),
        (GET, 'bad_type', True, None, True),
        # required
        (FORM, str, True, '1', True),
        (FORM, list, True, lambda x: [1, 2, 3], True),
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

    @parameterized.expand([
        (Param('test', GET, int, required=False, default=0), 0, '0'),
        (Param('test', GET, str, required=False, default=''), '', ''),
        (Param('test', GET, bool, required=False, default=False), False, 'False'),
        (Param('test', GET, list, required=False, default=[]), [], []),
    ])
    def test_default_value(self, param, expected, value):
        self.assertEqual(param.value_to_type(value), expected)


_app2 = flask.Flask(__name__)


@_app2.errorhandler(InvalidRequestError)
def handler(e):
    return flask.jsonify(demo_error_formatter(e)), 400


@_app2.route('/', methods=['POST'])
@validate_params(
    JsonParam({
        'island': [Pattern(r'^[a-z]{4,20}$')],
        'iso': [IsDatetimeIsoFormat()],
        'music': JsonParam({
            'bands': JsonParam({
                'name': [MinLength(2), MaxLength(20)],
                'details': JsonParam({
                    'description': [MinLength(5)],
                    'status': [Enum('active', 'not_active'), ],
                }),
                'persons': JsonParam({'name': [MinLength(3), MaxLength(20)]}, as_list=True),
            }, as_list=True, ),
        }),
    })
)
def home(valid: ValidRequest):
    valid_json = valid.get_json()
    valid_json['iso'] = valid_json['iso'].strftime('%Y-%m-%d')
    return flask.jsonify({'json': valid.get_json()})


class TestNestedJson(TestCase):
    maxDiff = 2000

    @parameterized.expand([
        # invalid
        (
            {
                'island': 'sm',
                'iso': 'error',
                'music': {
                    'bands': [
                        {
                            'name': 'c',
                            'details': {'description': 'sm', 'status': 'invalid2'},
                            'persons': [{'name': 'ba'}, {'name': 'gs'}],
                        },
                        {
                            'name': 'z',
                            'details': {'description': 'zp', 'status': 'invalid3'},
                            'persons': [{'name': 'nm'}, {'name': 'valid_name'}],
                        },
                    ],
                }
            },
            [
                {
                    'errors': [
                        {'keys': {'description': 'invalid length, min length = 5',
                                  'status': 'not allowed, allowed values: active|not_active'},
                         'path': 'root|music|bands|details'},
                        {'list_items': {'0': {'name': 'invalid length, min length = 3'},
                                        '1': {'name': 'invalid length, min length = 3'}},
                         'path': 'root|music|bands|persons'}, {
                            'keys': {'description': 'invalid length, min length = 5',
                                     'status': 'not allowed, allowed values: active|not_active'},
                            'path': 'root|music|bands|details'},
                        {'list_items': {'0': {'name': 'invalid length, min length = 3'}},
                         'path': 'root|music|bands|persons'},
                        {'list_items': {'0': {'name': 'invalid length, min length = 2'},
                                        '1': {'name': 'invalid length, min length = 2'}},
                         'path': 'root|music|bands'}, {
                            'keys': {'island': 'value does not match pattern ^[a-z]{4,20}$',
                                     'iso': 'expected a datetime in ISO format'}, 'path': 'root'}],
                    'message': 'invalid JSON parameters'
                }
            ],
            '400 BAD REQUEST',
        ),
        # valid
        (
            {
                'island': 'valid',
                'iso': '2021-01-02T03:04:05.450686Z',
                'music': {
                    'bands': [
                        {
                            'name': 'Metallica',
                            'details': {'details': 'Los Angeles, California, U.S.',
                                        'status': 'active'},
                            'persons': [
                                {'name': 'James Hetfield'},
                                {'name': 'Lars Ulrich'},
                                {'name': 'Kirk Hammett'},
                                {'name': 'Robert Trujillo'},
                            ],
                        },
                        {
                            'name': 'AC/DC',
                            'details': {'details': 'Sydney, Australia', 'status': 'active'},
                            'persons': [
                                {'name': 'Angus Young'},
                                {'name': 'Stevie Young'},
                                {'name': 'Brian Johnson'},
                                {'name': 'Phil Rudd'},
                                {'name': 'Cliff Williams'},
                            ],
                        },
                    ],
                }
            },
            {
                'json': {
                    'island': 'valid', 'iso': '2021-01-02', 'music': {
                        'bands': [
                            {'details': {'details': 'Los Angeles, California, U.S.',
                                         'status': 'active'},
                             'name': 'Metallica',
                             'persons': [{'name': 'James Hetfield'}, {'name': 'Lars Ulrich'},
                                         {'name': 'Kirk Hammett'}, {'name': 'Robert Trujillo'}]},
                            {'details': {'details': 'Sydney, Australia', 'status': 'active'},
                             'name': 'AC/DC',
                             'persons': [{'name': 'Angus Young'}, {'name': 'Stevie Young'},
                                         {'name': 'Brian Johnson'}, {'name': 'Phil Rudd'},
                                         {'name': 'Cliff Williams'}]
                             }
                        ]
                    }
                }
            },
            '200 OK'
        ),
    ])
    def test_json_route_with_error_formatter(self, data, expected, status):
        with _app2.test_client() as client:
            response = client.post('/', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status, status)
            self.assertEqual(response.json, expected)
