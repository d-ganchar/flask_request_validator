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

    def _assert_single_rules_error(self, rules, value, exp_type):
        if exp_type:
            try:
                rules.validate(value)
            except RulesError as e:
                self.assertTrue(1, len(e.errors))
                self.assertTrue(isinstance(e.errors[0], exp_type))

    def _assert_rule_error(self, rule, value, exp_type):
        if exp_type:
            self.assertRaises(exp_type, rule.validate, value)

    @parameterized.expand([
        (1.00001, Min(1), Max(2), None),
        (1.00000, Min(1), Max(2), None),
        (1.99999, Min(1), Max(2), None),
        (2.00000, Min(1), Max(2), None),
        (0.000009, Min(1), Max(2), ValueMinError),
        (1.00000, Min(1, False), Max(2), ValueMinError),
        (2.0000001, Min(1), Max(2), ValueMaxError),
        (2.00000, Min(1), Max(2, False), ValueMaxError),
    ])
    def test_min_max(self, value, min_rule, max_rule, exp) -> None:
        rules = CompositeRule(*[min_rule, max_rule])
        self._assert_single_rules_error(rules, value, exp)

    @parameterized.expand([
        (Pattern(r'^[0-9]*$'), '0', None, ),
        (Pattern(r'^[0-9]*$'), '23456', None, ),
        (Pattern(r'^[0-9]*$'), 'god is an astronaut', ValuePatternError,),
        (Pattern(r'^[0-9]*$'), ' ', ValuePatternError,),
    ])
    def test_pattern_rule(self, rule, value, exp) -> None:
        self._assert_rule_error(rule, value, exp)

    @parameterized.expand([
        (Enum('thievery corporation', 'bonobo'), 'jimi hendrix', ValueEnumError),
        (Enum('thievery corporation', 'bonobo'), 'thievery corporation', None),
        (Enum('thievery corporation', 'bonobo'), 'bonobo', None),
    ])
    def test_enum_rule(self, rule, value, exp) -> None:
        self._assert_rule_error(rule, value, exp)

    @parameterized.expand([
        ('mammal hands', MinLength(11), MaxLength(13), None),
        ('mammal hands', MinLength(11), MaxLength(13), ValueMinError),
        ('#mammal hands#', MinLength(11), MaxLength(13), ValueMaxLengthError),
    ])
    def test_min_max_length_rule(self, value, min_l, max_l, exp):
        rules = CompositeRule(*[min_l, max_l])
        self._assert_single_rules_error(rules, value, exp)

    @parameterized.expand([
        ('exxasens', 'exxasens', None),
        ('  exxasens   ', 'exxasens', None),
        ('', '', ValueEmptyError),
        (' ' * random.randint(2, 20), '', ValueEmptyError),
    ])
    def test_not_empty_rule(self, value, exp_val, exp_err) -> None:
        rule = NotEmpty()
        if exp_err:
            self.assertRaises(exp_err, rule.validate, value)
        else:
            self.assertEqual(rule.validate(value), exp_val)

    @parameterized.expand([
        ('fred@web.de', None, ),
        ('genial@gmail.com', None, ),
        ('test@test.co.uk', None, ),
        ('fred', None, ),
        ('fred@web', ValueEmailError, ),
        ('fred@w@eb.de', ValueEmailError, ),
        ('fred@@web.de', ValueEmailError, ),
        ('fred@@web.de', ValueEmailError, ),
        ('invalid@invalid', ValueEmailError, ),
    ])
    def test_is_email_rule(self, value, exp_err) -> None:
        self._assert_rule_error(IsEmail(), value, exp_err)

    @parameterized.expand([
        ('2021-01-02T03:04:05.450686Z', datetime(2021, 1, 2, 3, 4, 5, 450686)),
        (
            '2020-12-01T21:31:32.956214+02:00',
            datetime(2020, 12, 1, 21, 31, 32, 956214, timezone(timedelta(seconds=7200))),
        ),
        (
            '2020-12-01T21:31:32.956214-02:00',
            datetime(2020, 12, 1, 21, 31, 32, 956214, timezone(timedelta(-1, seconds=79200))),
        ),
        ('2021-01-02', datetime(2021, 1, 2)),
        ('2020-12-01T21:31:41', datetime(2020, 12, 1, 21, 31, 41)),
        ('2020-12-01T21', None),
    ])
    def test_datetime_iso_format_rule(self, value, exp_dt) -> None:
        rule = IsDatetimeIsoFormat()
        if exp_dt:
            self.assertEqual(exp_dt, rule.validate(value))
        else:
            self.assertRaises(ValueDtIsoFormatError, rule.validate, value)

    @parameterized.expand([
        ('2021-01-02', '%Y-%m-%d', datetime(2021, 1, 2), None),
        ('2020-02-03 04:05:06', '%Y-%m-%d %H:%M:%S', datetime(2020, 2, 3, 4, 5, 6), None),
        ('2020-0a-0b 04:05:06', '%Y-%m-%d %H:%M:%S', None, ValueDatetimeError),
        ('2020-01-0z', '%Y-%m-%d', None, ValueDatetimeError),
    ])
    def test_datetime_rule(self, value, dt_format, dt, err):
        rule = Datetime(dt_format)
        if err:
            self.assertRaises(ValueDatetimeError, rule.validate, value)
        else:
            self.assertEqual(dt, rule.validate(value))
