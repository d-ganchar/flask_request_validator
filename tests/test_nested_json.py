import unittest
from copy import deepcopy

from parameterized import parameterized

from flask_request_validator import JsonParam, Enum, CompositeRule, Min, Max, IsEmail, Number, MinLength
from flask_request_validator.exceptions import *


class TestJsonParam(unittest.TestCase):
    LIST_SCHEMA = JsonParam(
        {
            'person': JsonParam(
                {
                    'info': JsonParam({
                        'contacts': JsonParam({
                            'phones': JsonParam([Enum('+375', '+49')], as_list=True),
                            'networks': JsonParam(
                                {'name': [Enum('facebook', 'telegram')]},
                                as_list=True,
                            ),
                            'emails': JsonParam([IsEmail()], as_list=True),
                            'addresses': JsonParam({'street': []},  required=False),
                        }),
                    }),
                },
            ),
        },
    )

    DICT_SCHEMA = JsonParam(
        {
            'street': CompositeRule(Enum('Jakuba Kolasa')),
            'meta': JsonParam(
                {
                    'description': JsonParam({
                        'color': [Enum('green', 'yellow', 'blue')],
                    }, ),
                    'buildings': JsonParam({
                        'warehouses': JsonParam({
                            'small': JsonParam({
                                'count': CompositeRule(Min(0), Max(99)),
                            }),
                            'large': [Min(1), Max(10)]
                        }),
                    }),
                    'not_required': JsonParam({'text': []}, required=False),
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
    def test_validate(self, param: JsonParam, data, exp):
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
        param = JsonParam({
            'age': [Number()],
            'name': [MinLength(1), ],
            'tags': JsonParam({'name': [MinLength(1)]}, required=False, as_list=True)
        }, as_list=True)

        valid_value, errors = param.validate(deepcopy(value))
        self.assertListEqual(value, valid_value)
        self.assertEqual(0, len(errors))

    def test_root_list_invalid(self):
        param = JsonParam({
            'age': [Number()],
            'name': [MinLength(1), ],
            'tags': JsonParam({'name': [MinLength(1)]}, required=False, as_list=True)
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
