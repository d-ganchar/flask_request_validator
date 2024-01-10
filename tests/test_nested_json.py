import unittest
from copy import deepcopy

from parameterized import parameterized
import flask

from flask_request_validator import (
    JsonParam as P,
    Enum,
    CompositeRule,
    Min,
    Max,
    IsEmail,
    Number,
    MinLength,
    IntRule,
    FloatRule,
    BoolRule,
    validate_params,
    ValidRequest,
)
from flask_request_validator.exceptions import *


class TestJsonParam(unittest.TestCase):
    LIST_SCHEMA = P(
        {
            'person': P(
                {
                    'info': P({
                        'contacts': P({
                            'phones': P([Enum('+375', '+49')], as_list=True),
                            'networks': P(
                                {'name': [Enum('facebook', 'telegram')]},
                                as_list=True,
                            ),
                            'emails': P([IsEmail()], as_list=True),
                            'addresses': P({'street': []}, required=False),
                        }),
                    }),
                },
            ),
        },
    )

    DICT_SCHEMA = P(
        {
            'street': CompositeRule(Enum('Jakuba Kolasa')),
            'meta': P(
                {
                    'description': P({
                        'color': [Enum('green', 'yellow', 'blue')],
                    }, ),
                    'buildings': P({
                        'warehouses': P({
                            'small': P({
                                'count': CompositeRule(Min(0), Max(99)),
                            }),
                            'large': [Min(1), Max(10)]
                        }),
                    }),
                    'not_required': P({'text': []}, required=False),
                },
            ),
        },
    )

    @parameterized.expand([
        # invalid
        (
            DICT_SCHEMA,
            {
                'street': 'Rampische',
                'meta': {'buildings': {'warehouses': {'small': {'count': 100, }, 'large': 0, }, }, },
            },
            [
                "(['root', 'meta', 'buildings', 'warehouses', 'small'],"
                " {'count': RulesError(ValueMaxError(99, True))}, False)",
                "(['root', 'meta', 'buildings', 'warehouses'],"
                " {'large': RulesError(ValueMinError(1, True))}, False)",
                "(['root', 'meta'], {'description': RulesError(MissingJsonKeyError('description'))}, False)",
                "(['root'], {'street': RulesError(ValueEnumError(('Jakuba Kolasa',)))}, False)",
            ],
        ),
        (
            LIST_SCHEMA,
            {
                'person': {
                    'info': {
                        'contacts': {
                            'phones': [
                                '+375',
                                '+49',
                                {'code': '+420'},
                                {'code': '+10000'}
                            ],
                            'emails': [{'work': 'bad_type1'}, {'work': 'bad_type2'}, 'bad_mail'],
                            'networks': [
                                {'name': 'facebook'},
                                {'name': 'insta'},
                                {'name': 'linkedin'},
                            ],
                        },
                    },
                },
            },
            [
                "(['root', 'person', 'info', 'contacts', 'phones'], "
                "{2: JsonListItemTypeError(False), 3: JsonListItemTypeError(False)}, True)",

                "(['root', 'person', 'info', 'contacts', 'networks'], "
                "{1: {'name': RulesError(ValueEnumError(('facebook', 'telegram')))}, "
                "2: {'name': RulesError(ValueEnumError(('facebook', 'telegram')))}}, True)",

                "(['root', 'person', 'info', 'contacts', 'emails'], "
                "{0: JsonListItemTypeError(False), 1: JsonListItemTypeError(False), "
                "2: RulesError(ValueEmailError())}, True)",
            ],
        ),
        # valid
        (
            DICT_SCHEMA,
            {
                'country': 'Belarus',
                'city': 'Minsk',
                'street': 'Jakuba Kolasa',
                'meta': {
                    'buildings': {
                        'warehouses': {
                            'small': {'count': 99, },
                            'large': 1,
                        },
                    },
                    'description': {
                        'color': 'green',
                    },
                },
            },
            {},
        ),
        (
            LIST_SCHEMA,
            {
                'person': {
                    'info': {
                        'contacts': {
                            'phones': ['+375', '+49'],
                            'networks': [
                                {'name': 'facebook'},
                                {'name': 'telegram'},
                                {'name': 'telegram'},
                                {'name': 'facebook'},
                            ],
                            'emails': ['test@gmail.com'],
                        },
                    },
                },
            },
            [],
        ),
    ])
    def test_validate(self, param: P, data, exp):
        value, errors = param.validate(deepcopy(data))
        self.assertEqual(len(errors), len(exp))

        for ix, json_error in enumerate(exp):  # type: int, List[list, dict]
            str_error = str(errors[ix])
            self.assertEqual(json_error, str_error)

    @parameterized.expand([
        (
            [
                {'age': 10, 'name': 'test'},
                {'age': 20, 'name': 'test2'},
                {'age': 30, 'name': 'test3'},
            ],
        ),
        (
            [
                {'age': 10, 'name': 'test', 'tags': [{'name': 'green'}, {'name': 'light'}]},
                {'age': 20, 'name': 'test2'},
                {'age': 30, 'name': 'test3', 'tags': [{'name': 'cat'}, {'name': 'dog'}]},
            ],
        ),
    ])
    def test_root_list_valid(self, value):
        param = P({
            'age': [Number()],
            'name': [MinLength(1), ],
            'tags': P({'name': [MinLength(1)]}, required=False, as_list=True)
        }, as_list=True)

        valid_value, errors = param.validate(deepcopy(value))
        self.assertListEqual(value, valid_value)
        self.assertEqual(0, len(errors))

    def test_root_list_invalid(self):
        param = P({
            'age': [Number()],
            'name': [MinLength(1), ],
            'tags': P({'name': [MinLength(1)]}, required=False, as_list=True)
        }, as_list=True)
        # invalid values
        _, errors = param.validate([
            {'age': 'ab', 'name': 'test'},
            {'age': 'c', 'name': ''},
            {'age': 15, 'name': 'good'},
        ])

        self.assertEqual(
            "[JsonError(['root'], "
            "{0: {'age': RulesError(NumberError())}, 1: "
            "{'age': RulesError(NumberError()), 'name': RulesError(ValueMinLengthError(1))}}, True)]",
            str(errors)
        )

        # invalid type - dict instead list
        _, errors = param.validate({'age': 18, 'name': 'test'})
        self.assertEqual("[JsonListExpectedError(['root'])]", str(errors))

    @parameterized.expand([
        # IntRule
        (
            P(dict(age=[Min(27), IntRule()], day=[Min(1), IntRule()])),
            dict(age=27, day='1'),
            dict(age=27, day=1),
        ),
        (
            P(dict(age=[Min(27), IntRule(False)])),
            dict(age='27'),
            "[JsonError(['root'], {'age': RulesError(TypeConversionError())}, False)]",
        ),
        # FloatRule
        (
            P(dict(price=[Min(0.69), FloatRule()], size=[Min(0.25), FloatRule({','})])),
            dict(price=0.69, size='0,25'),
            dict(price=0.69, size=0.25),
        ),
        # BoolRule
        (
            P(dict(yes=[BoolRule()], no=[BoolRule()])),
            dict(yes=True, no=False),
            dict(yes=True, no=False),
        ),
    ])
    def test_type_checkers(self, param: P, value: dict, expected: dict or str):
        new_val, errors = param.validate(value)
        if isinstance(expected, str):
            self.assertEqual(expected, str(errors))
            return

        self.assertEqual(new_val, expected)


_app = flask.Flask(__name__)

_app.testing = True


@_app.route('/issue-90', methods=['POST'])
@validate_params(P(dict(amount=[IntRule()], price=[FloatRule({','})])))
def issue_90(valid: ValidRequest):
    return flask.jsonify(dict(
        json_after_validation=valid.get_json(),
        raw_json=valid.get_flask_request().json,
    ))


class TestNestedJson(unittest.TestCase):
    def test_nested_json(self):
        data = dict(amount='99', price='101,101')
        with _app.test_client() as client:
            result = client.post('/issue-90', json=data).json

        self.assertDictEqual(result['raw_json'], data)
        self.assertDictEqual(
            result['json_after_validation'],
            dict(amount=99, price=101.101),
        )
