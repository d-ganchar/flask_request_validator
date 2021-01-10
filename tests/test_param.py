import unittest
from parameterized import parameterized

from flask_request_validator.exceptions import NestedJsonError
from flask_request_validator import JsonParam, Enum, CompositeRule, Min, Max, IsEmail


class TestJsonParam(unittest.TestCase):
    LIST_SCHEMA = JsonParam(
        {
            'person': JsonParam(
                {
                    'info': JsonParam({
                        'contacts': JsonParam({
                            'phones': JsonParam(
                                {'code': [Enum('+375', '+49')], },
                                as_list=True,
                            ),
                            'networks': JsonParam(
                                {'name': [Enum('facebook', 'telegram')]},
                                as_list=True,
                            ),
                            'emails': JsonParam(
                                {'work': [IsEmail()]},
                                as_list=True,
                            ),
                            'addresses': JsonParam(
                                {'street': []},
                                required=False,
                            ),
                        }),
                    }),
                },
            ),
        },
    )

    DICT_SCHEMA = JsonParam(
        {
            'country': [Enum('Belarus')],
            'city': [Enum('Minsk')],
            'street': CompositeRule(Enum('Jakuba Kolasa')),
            'meta': JsonParam(
                {
                    'description': JsonParam({'color': [Enum('green', 'yellow', 'blue')], }, ),
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
        # invalid nested list
        (
            LIST_SCHEMA,
            {
                'person': {
                    'info': {
                        'contacts': {
                            'phones': [
                                {'code': '+375'},
                                {'code': '+49'},
                                {'code': '+420'},
                                {'code': '+10000'}
                            ],
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
                [
                    'root|person|info|contacts|networks|1',
                    ['Incorrect value "insta". Allowed values: (\'facebook\', \'telegram\')'],
                ],
                [
                    'root|person|info|contacts|networks|2',
                    ['Incorrect value "linkedin". Allowed values: (\'facebook\', \'telegram\')']],
                [
                    'root|person|info|contacts', ['emails'],
                ],
            ],
        ),
        # valid nested list
        (
            LIST_SCHEMA,
            {
                'person': {
                    'info': {
                        'contacts': {
                            'phones': [
                                {'code': '+375'},
                                {'code': '+49'},
                                {'code': '+375'},
                                {'code': '+49'},
                            ],
                            'networks': [
                                {'name': 'facebook'},
                                {'name': 'telegram'},
                                {'name': 'telegram'},
                                {'name': 'facebook'},
                            ],
                            'emails': [{'work': 'test@gmail.com'}]
                        },
                    },
                },
            },
            [],
        ),
        # invalid dict
        (
            DICT_SCHEMA,
            {
                'country': 'Germany',
                'city': 'Dresden',
                'street': 'Rampische',
                'meta': {
                    'buildings': {
                        'warehouses': {
                            'small': {'count': 100, },
                            'large': 0,
                        },
                    },
                },
            },
            [
                [
                    'root|meta|buildings|warehouses|small',
                    ['greater then allowed: 100 is not <= 99'],
                ],
                [
                    'root|meta|buildings|warehouses',
                    ['smaller then allowed: 0 is not >= 1'],
                ],
                [
                    'root|meta',
                    ['description'],
                ],
                [
                    'root',
                    [
                        'Incorrect value "Germany". Allowed values: (\'Belarus\',)',
                        'Incorrect value "Dresden". Allowed values: (\'Minsk\',)',
                        'Incorrect value "Rampische". Allowed values: (\'Jakuba Kolasa\',)',
                    ],
                ],
            ],
        ),
        # valid dict
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
            [],
        )
    ])
    def test_validate(self, param: JsonParam, data, exp_errors):
        value, errors = param.validate(data)
        formatted_errors = []
        for error in errors:  # type: NestedJsonError
            self.assertTrue(isinstance(error, NestedJsonError))
            depth = '|'.join(str(e) for e in error.depth)
            node_errors = []
            for node_error in error.errors:
                node_errors.append(str(node_error))
            formatted_errors.append([depth, node_errors])

        self.assertListEqual(formatted_errors, exp_errors)
