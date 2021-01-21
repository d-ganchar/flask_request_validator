import unittest
from datetime import datetime, timedelta, timezone

from flask_request_validator.date_time_iso_format import datetime_from_iso_format
from flask_request_validator.rules import IsEmail, IsDatetimeIsoFormat, NotEmpty, Max, Min, AbstractRule, MinLength, \
    MaxLength, Enum, Pattern, CompositeRule


class TestRules(unittest.TestCase):

    def test_abstract_rule(self) -> None:
        with self.assertRaises(expected_exception=TypeError):
            AbstractRule()

    def test_composite_rule(self) -> None:
        rules = [Min(1), Max(2)]
        rule = CompositeRule(*rules)

        for r in rule:
            self.assertIn(r, rules)

        for value in [1.0, 1, 1.0002, 1.2, 1.5, 1.9999, 2, 2.0]:
            self.assertEqual((value, []), rule.validate(value))

        for value in [-42, -1, 0, 0.999, 2.00001, 2.4, 3.8, 46868841635]:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_pattern_rule(self) -> None:
        rule = Pattern(r'^[0-9]*$')

        for value in ['0', '23456', 213, '1100']:
            self.assertEqual((value, []), rule.validate(value))

        for value in ['hello', ' ', '2345h456z']:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_enum_rule(self) -> None:
        values = ['Hi', 'there!', 42, None, unittest.TestCase]
        rule = Enum(*values)

        for value in values:
            self.assertEqual((value, []), rule.validate(value))

        for value in ['hello', list(range(42)), 4 * ' ']:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_max_length_rule(self) -> None:
        rule = MaxLength(3)

        for value in ['hi!', 3 * ' ', [1, 2, 3], '', 'hi', 2 * ' ', [1, 2], []]:
            self.assertEqual((value, []), rule.validate(value))

        for value in ['hello', list(range(42)), 4 * ' ']:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_min_length_rule(self) -> None:
        rule = MinLength(3)

        for value in ['hi!', 'hello', 3 * ' ', [1, 2, 3], list(range(42))]:
            self.assertEqual((value, []), rule.validate(value))

        for value in ['', 'hi', 2 * ' ', [1, 2], []]:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_not_empty_rule(self) -> None:
        rule = NotEmpty()

        for value in ['hi', '  v a  l   i d   ']:
            self.assertEqual((value.strip(), []), rule.validate(value))

        for value in ['', '   ', '         ']:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_max_rule_include_boundary_true(self) -> None:
        rule = Max(3, include_boundary=True)

        for value in [-42, -2, -1, 0, 1, 2, 3]:
            self.assertEqual((value, []), rule.validate(value))

        for value in [4, 5, 6, 100]:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_max_rule_include_boundary_false(self) -> None:
        rule = Max(3, include_boundary=False)

        for value in [-42, -2, -1, 0, 1, 2, 2.999]:
            self.assertEqual((value, []), rule.validate(value))

        for value in [3, 4, 5, 6, 100]:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_min_rule_include_boundary_true(self) -> None:
        rule = Min(4, include_boundary=True)

        for value in [4, 5, 6, 100]:
            self.assertEqual((value, []), rule.validate(value))

        for value in [-42, -2, -1, 0, 1, 2, 3]:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_min_rule_include_boundary_false(self) -> None:
        rule = Min(4, include_boundary=False)

        for value in [4.001, 5, 6, 100]:
            self.assertEqual((value, []), rule.validate(value))

        for value in [-42, -2, -1, 0, 1, 2, 3, 4]:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_datetime_iso_invalide(self) -> None:
        rule = IsDatetimeIsoFormat()
        now = datetime.now()

        actual, errors = rule.validate(now.isoformat())
        self.assertTrue(abs(now - actual) < timedelta(milliseconds=1))
        self.assertEqual([], errors)

        for value in ['invalid', '2020-01-1', '12.12.2020']:
            self.assertEqual(1, len(rule.validate(value)[1]))

    def test_datetime_iso_valid(self) -> None:
        rule = IsDatetimeIsoFormat()
        for dt_str, exp in (
            ('2021-02-02T02:02:02.518993Z', datetime(2021, 2, 2, 2, 2, 2, 518993)),
            ('2021-02-02T02:02:02.696969', datetime(2021, 2, 2, 2, 2, 2, 696969)),
            (
                '2022-03-03T03:03:03.518993+02:00',
                datetime(2022, 3, 3, 3, 3, 3, 518993, timezone(timedelta(seconds=7200)))
            ),
            ('2023-04-04T05:05:05', datetime(2023, 4, 4, 5, 5, 5, )),
        ):
            self.assertEqual(rule.validate(dt_str)[0], exp)

    def test_is_email_rule(self) -> None:
        rule = IsEmail()

        for value in ['fred@web.de', 'genial@gmail.com', 'test@test.co.uk']:
            self.assertEqual((value, []), rule.validate(value))

        for value in ['fred', 'fred@web', 'fred@w@eb.de', 'fred@@web.de', 'invalid@invalid']:
            self.assertEqual(1, len(rule.validate(value)[1]))
