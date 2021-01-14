from unittest import TestCase
from urllib.parse import urlencode

import flask
from flask_restful import Api, Resource
from parameterized import parameterized

from flask_request_validator import GET, Param, validate_params, ValidRequest
from flask_request_validator.exceptions import *
from flask_request_validator.rules import *
from flask_request_validator.validator import HEADER, PATH


_app = flask.Flask(__name__)
_test_api = Api(_app, '/v1')
_app.testing = True
_VALID_REST_ROUTE = '/v1/rest/Metallica'
_VALID_HEADERS = {
    'Authorization': 'Bearer token',
    'Custom header': 'custom value',
}


_PARAMS = (
    Param('Authorization', HEADER, str, rules=[Enum('Bearer token')]),
    Param('Custom header', HEADER, str, rules=[Enum('custom value')]),
    Param('band', PATH, str, rules=[Enum('Metallica')]),
    Param('track1', GET, str, rules=[Enum('die die my darling')]),
    Param('track2', GET, str, rules=[Enum('whiskey in the jar')]),
    Param('Polar Music Prize', GET, bool),
)


class TestApi(Resource):
    @validate_params(*_PARAMS)
    def put(self, valid: ValidRequest, band):
        return flask.jsonify({
            GET: valid.get_params(),
            PATH: valid.get_path_params(),
        })

    @validate_params(*_PARAMS)
    def get(self, valid: ValidRequest, band):
        return flask.jsonify({
            GET: valid.get_params(),
            PATH: valid.get_path_params(),
        })

    @validate_params(*_PARAMS)
    def post(self, valid: ValidRequest, band):
        return flask.jsonify({
            GET: valid.get_params(),
            PATH: valid.get_path_params(),
        })

    @validate_params(*_PARAMS)
    def delete(self, valid: ValidRequest, band):
        return flask.jsonify({
            GET: valid.get_params(),
            PATH: valid.get_path_params(),
        })


_test_api.add_resource(TestApi, '/rest/<string:band>')


class TestRest(TestCase):
    @parameterized.expand([
        ('get', InvalidHeadersError, {}),
        ('post', InvalidHeadersError, {}),
        ('put', InvalidHeadersError, {}),
        ('delete', InvalidHeadersError, {}),
        ('get', InvalidRequestError, _VALID_HEADERS),
        ('post', InvalidRequestError, _VALID_HEADERS),
        ('put', InvalidRequestError, _VALID_HEADERS),
        ('delete', InvalidRequestError, _VALID_HEADERS),
    ])
    def test_headers(self, method, error, headers):
        with _app.test_client() as client:
            self.assertRaises(error, getattr(client, method), _VALID_REST_ROUTE, headers=headers)

    @parameterized.expand([
        # invalid
        ('get', InvalidRequestError, {}, {}),
        ('post', InvalidRequestError, {'track1': 'die die my darling'}, {}),
        ('put', InvalidRequestError, {'track2': 'whiskey in the jar'}, {}),
        ('delete', InvalidRequestError, {'Polar Music Prize': '1'}, {}),
        # valid
        (
            'get',
            None,
            {
                'Polar Music Prize': 'True',
                'track1': 'die die my darling',
                'track2': 'whiskey in the jar',
            },
            {
                'GET': {
                    'Polar Music Prize': True,
                    'track1': 'die die my darling',
                    'track2': 'whiskey in the jar',
                },
                'PATH': {'band': 'Metallica'},
             }
        ),
        (
            'post',
            None,
            {
                'Polar Music Prize': 'True',
                'track1': 'die die my darling',
                'track2': 'whiskey in the jar',
            },
            {
                'GET': {
                    'Polar Music Prize': True,
                    'track1': 'die die my darling',
                    'track2': 'whiskey in the jar',
                },
                'PATH': {'band': 'Metallica'},
            },
        ),
        (
            'put',
            None,
            {
                'Polar Music Prize': 'True',
                'track1': 'die die my darling',
                'track2': 'whiskey in the jar',
            },
            {
                'GET': {
                    'Polar Music Prize': True,
                    'track1': 'die die my darling',
                    'track2': 'whiskey in the jar',
                },
                'PATH': {'band': 'Metallica'},
            },
        ),
        (
            'delete',
            None,
            {
                'Polar Music Prize': 'True',
                'track1': 'die die my darling',
                'track2': 'whiskey in the jar',
            },
            {
                'GET': {
                    'Polar Music Prize': True,
                    'track1': 'die die my darling',
                    'track2': 'whiskey in the jar',
                },
                'PATH': {'band': 'Metallica'},
            },
        ),
    ])
    def test_methods(self, method, err, get_params, result):
        route = ''.join([_VALID_REST_ROUTE, '?', urlencode(get_params, doseq=True)])
        with _app.test_client() as client:
            try:
                response = getattr(client, method)(route, headers=_VALID_HEADERS).json
            except Exception as e:
                self.assertTrue(isinstance(e, err))
                return
        self.assertDictEqual(response, result)
