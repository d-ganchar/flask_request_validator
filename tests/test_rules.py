import unittest

from parameterized import parameterized

from flask_request_validator.rules import AbstractRule, CompositeRule, Enum, IsEmail, Max, \
    MaxLength, Min, MinLength, NotEmpty, Pattern


class TestRules(unittest.TestCase):

    def test_abstract_rule(self) -> None:
        with self.assertRaises(expected_exception=TypeError):
            AbstractRule()

    @parameterized.expand([
        (1.0, 0,),
        (1, 0,),
        (1.0002, 0,),
        (1.2, 0,),
        (1.5, 0,),
        (1.9999, 0,),
        (2, 0,),
        (2.0, 0,),
        (-42, 1,),
        (-1, 1,),
        (0, 1,),
        (0.999, 1,),
        (2.00001, 1,),
        (2.4, 1,),
        (3.8, 1,),
        (46868841635, 1,),
    ])
    def test_composite_rule(self, value, expected) -> None:
        rules = [Min(1), Max(2)]
        rule = CompositeRule(*rules)
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        ('0', 0),
        ('23456', 0),
        (213, 0),
        ('1100', 0),
        ('hello', 1),
        (' ', 1),
        ('2345h456z', 1),
    ])
    def test_pattern_rule(self, value, expected) -> None:
        rule = Pattern(r'^[0-9]*$')

        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        ('Hi', 0),
        ('there!', 0),
        (5, 0),
        ('hello', 1),
        (10, 1),
        (4 * ' ', 1),
    ])
    def test_enum_rule(self, value, expected) -> None:
        values = ['Hi', 'there!', 5]
        rule = Enum(*values)
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        ('hi!', 0),
        (3 * ' ', 0),
        ([1, 2, 3], 0),
        ('', 0),
        ('hi', 0),
        (2 * ' ', 0),
        ([1, 2], 0),
        ([], 0),
        ('hello', 1),
        (list(range(42)), 1),
        (4 * ' ', 1),
    ])
    def test_max_length_rule(self, value, expected) -> None:
        rule = MaxLength(3)
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        ('hi!', 0),
        (3 * ' ', 0),
        ([1, 2, 3], 0),
        ('hello', 0),
        (list(range(42)), 0),
        (4 * ' ', 0),
        ('', 1),
        ('hi', 1),
        (2 * ' ', 1),
        ([1, 2], 1),
        ([], 1),
    ])
    def test_min_length_rule(self, value, expected) -> None:
        rule = MinLength(3)
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        ('hi', 0),
        ('  v a  l   i d   ', 0),
        ('', 1),
        (' ' * 5, 1),
    ])
    def test_not_empty_rule(self, value, expected) -> None:
        rule = NotEmpty()
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        (-42, True, 0),
        (-2, True, 0),
        (-1, True, 0),
        (0, True, 0),
        (1, True, 0),
        (2, True, 0),
        (3, True, 0),
        (4, True, 1),
        (5, True, 1),
        (6, True, 1),
        (100, True, 1),
        (-42, False, 0),
        (-2, False, 0),
        (-1, False, 0),
        (0, False, 0),
        (1, False, 0),
        (2, False, 0),
        (2.999, False, 0),
    ])
    def test_max_rule(self, value, boundary, expected) -> None:
        rule = Max(3, include_boundary=boundary)
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        (4, True, 0),
        (5, True, 0),
        (6, True, 0),
        (100, True, 0),
        (4.001, False, 0),
        (5, False, 0),
        (6, False, 0),
        (100, False, 0),
    ])
    def test_min_rule(self, value, boundary, expected) -> None:
        rule = Min(4, include_boundary=boundary)
        self.assertEqual(expected, len(rule.validate(value)))

    @parameterized.expand([
        ('fred@web.de', 0),
        ('genial@gmail.com', 0),
        ('test@test.co.uk', 0),
        ('fred', 1),
        ('fred@web', 1),
        ('fred@w@eb.de', 1),
        ('fred@@web.de', 1),
        ('invalid@invalid', 1),
    ])
    def test_is_email_rule(self, value, expected) -> None:
        rule = IsEmail()
        self.assertEqual(expected, len(rule.validate(value)))
