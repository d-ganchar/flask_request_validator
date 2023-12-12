import unittest
import random
from datetime import timezone, timedelta

from parameterized import parameterized

from flask_request_validator.rules import *
from flask_request_validator.exceptions import *


class TestRules(unittest.TestCase):
    def test_abstract_rule(self) -> None:
        with self.assertRaises(expected_exception=TypeError):
            AbstractRule()

    @parameterized.expand([
        (1.00001, Min(1), Max(2), 1.00001),
        (1.00000, Min(1), Max(2), 1.00000),
        (1.99999, Min(1), Max(2), 1.99999),
        (2.00000, Min(1), Max(2), 2.00000),
        (0.000009, Min(1), Max(2), ValueMinError),
        (1.00000, Min(1, False), Max(2), ValueMinError),
        (2.0000001, Min(1), Max(2), ValueMaxError),
        (2.00000, Min(1), Max(2, False), ValueMaxError),
        ('mammal hands', MinLength(11), MaxLength(13), 'mammal hands'),
        ('', MinLength(3), MaxLength(5), ValueMinLengthError),
        ('mammal hands', MinLength(11), MaxLength(13), ValueMinLengthError),
        ('#mammal hands#', MinLength(11), MaxLength(13), ValueMaxLengthError),
    ])
    def test_composite_min_max_rule(self, value, min_l, max_l, expected):
        rules = CompositeRule(*[min_l, max_l])
        if not type(expected) is type:
            self.assertEqual(rules.validate(value), expected)
            return

        try:
            rules.validate(value)
        except RulesError as e:
            self.assertTrue(1, len(e.errors))
            self.assertTrue(isinstance(e.errors[0], expected))

    def test_composite_wrong_usage(self):
        checkers = [
            Number(),
            BoolRule(),
            BoolRule({'+'}),
            BoolRule({'+'}, {'-'}),
            BoolRule({'-'}),
            IntRule(),
            IntRule(False),
            FloatRule(),
            FloatRule({','}),
        ]

        random.shuffle(checkers)
        with self.assertRaises(expected_exception=WrongUsageError):
            CompositeRule(*checkers[0:2])

    @parameterized.expand([
        # Pattern
        (
            Pattern(r'^[0-9]*$'),
            [
                ['0', '0'],
                ['god is an astronaut', ValuePatternError],
                [' ', ValuePatternError],
            ]
        ),
        # Enum
        (
            Enum('thievery corporation', 'bonobo'),
            [
                ['jimi hendrix', ValueEnumError],
                ['thievery corporation', 'thievery corporation'],
                ['bonobo', 'bonobo'],
            ],
        ),
        # NotEmpty
        (NotEmpty(), [
            ['exxasens', 'exxasens'],
            ['  exxasens   ', 'exxasens'],
            ['', ValueEmptyError],
            [' ' * random.randint(2, 20), ValueEmptyError],
        ]),
        # IsEmail
        (
            IsEmail(),
            [
                ['fred@web.de', 'fred@web.de'],
                ['genial@gmail.com', 'genial@gmail.com'],
                ['test@test.co.uk', 'test@test.co.uk'],
                ['test@test.co.uk', 'test@test.co.uk'],
                ['fred', ValueEmailError],
                ['fred@web', ValueEmailError],
                ['fred@w@eb.de', ValueEmailError],
                ['invalid@invalid', ValueEmailError],
            ],
        ),
        # IsDatetimeIsoFormat
        (
            IsDatetimeIsoFormat(),
            [
                ['2021-01-02T03:04:05.450686Z', datetime(2021, 1, 2, 3, 4, 5, 450686)],
                ['2020-12-01T21:31:32.956214+02:00', datetime(2020, 12, 1, 21, 31, 32,
                                                              956214, timezone(timedelta(seconds=7200)))],
                ['2020-12-01T21:31:32.956214+02:00', datetime(2020, 12, 1, 21, 31, 32, 956214,
                                                              timezone(timedelta(seconds=7200)))],
                ['2021-01-02', datetime(2021, 1, 2)],
                ['2020-12-01T21:31:41', datetime(2020, 12, 1, 21, 31, 41)],
                ['2020-12-01T21', datetime(2020, 12, 1, 21, 0, 0)],
                ['2020-12-01T21:30', datetime(2020, 12, 1, 21, 30, 0)],
                ['2020-12-01T', ValueDtIsoFormatError],
                ['2020-12', ValueDtIsoFormatError],
                ['2020', ValueDtIsoFormatError],
            ],
        ),
        # Datetime
        (Datetime('%Y-%m-%d'), [['2021-01-02', datetime(2021, 1, 2)]]),
        (Datetime('%Y-%m-%d %H:%M:%S'), [['2020-02-03 04:05:06', datetime(2020, 2, 3, 4, 5, 6)]]),
        (Datetime('%Y-%m-%d %H:%M:%S'), [['2020-0a-0b 04:05:06', ValueDatetimeError]]),
        (Datetime('%Y-%m-%d'), [['2020-01-0z', ValueDatetimeError]]),
        # Number
        (
            Number(),
            [
                [1.0000000000000001e-21, 1.0000000000000001e-21],
                [2, 2],
                [3.04, 3.04],
                ['3o1', NumberError],
                ['', NumberError],
                [[], NumberError],
                [{}, NumberError],
            ],
        ),
        # IntRule
        (IntRule(), [[8, 8], ['69', 69]]),
        (
            IntRule(False),
            [
                ['101', TypeConversionError],
                [1.05, TypeConversionError],
                [[], TypeConversionError],
                [{}, TypeConversionError],
                [None, TypeConversionError],
            ]
        ),
        # FloatRule
        (
            FloatRule(),
            [
                [99.69, 99.69],
                [-1.08, -1.08],
                ['1.001', TypeConversionError],
                [7, TypeConversionError],
                [[], TypeConversionError],
                [{}, TypeConversionError],
            ],
        ),
        (
            FloatRule({'.', ','}),
            [
                ['1000,0001', 1000.0001],
                ['1000.0001', 1000.0001],
                ['1000-0001', TypeConversionError],
                [65, TypeConversionError],
            ],
        ),
        # BoolRule
        (
            BoolRule(),
            [
                [True, True],
                [False, False],
                [[], TypeConversionError],
                [{}, TypeConversionError],
                [1, TypeConversionError],
                ['1', TypeConversionError],
                [0, TypeConversionError],
                ['0', TypeConversionError],
            ],
        ),
        (
            BoolRule({'yes', '+', 1}, {'-', 'no', 0}),
            [
                [True, True],
                [1, True],
                ['yes', True],
                ['YeS', True],
                ['+', True],
                [False, False],
                [0, False],
                ['no', False],
                ['No', False],
                ['-', False],
            ],
        ),
    ])
    def test_rule(self, rule, values):
        for value, expected in values:
            if type(expected) is type:
                self.assertRaises(expected, rule.validate, value)
                continue

            self.assertEqual(expected, rule.validate(value))

