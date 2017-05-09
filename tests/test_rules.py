from unittest import TestCase

from flask_request_validator import Enum
from flask_request_validator import Required
from flask_request_validator import Type
from flask_request_validator.exceptions import NotAllowedType
from flask_request_validator.rules import (
    MaxLength,
    MinLength,
    Pattern,
    CompositeRule,
    ALLOWED_TYPES
)


class TestRules(TestCase):

    def test_required(self):
        required = Required()

        self.assertEqual(['Value is required'], required.validate(None))
        self.assertEqual(None, required.validate('value'))

    def test_type_str(self):
        type_rule = Type(str)

        for value in ('test', u'test',):
            value = type_rule.value_to_type(value)
            self.assertEqual(None, type_rule.validate(value))

    def test_type_int(self):
        type_int = Type(int)

        for value in (1, '1', u'1',):
            value = type_int.value_to_type(value)
            self.assertEqual(None, type_int.validate(value))

        value = type_int.value_to_type('1test')
        self.assertEqual(['Invalid type for value 1test'], type_int.validate(value))

    def test_type_bool(self):
        type_bool = Type(bool)

        for value in ('False', 'false', '0', 'True', 'true', '1'):
            value = type_bool.value_to_type(value)
            self.assertEqual(None, type_bool.validate(value))

        self.assertEqual(['Invalid type for value 2'], type_bool.validate('2'))
        self.assertEqual(['Invalid type for value test'], type_bool.validate('test'))

    def test_type_list(self):
        type_list = Type(list)
        with_spaces = type_list.value_to_type('key1, key2, key3')
        without = type_list.value_to_type('key1,key2,key3')
        expected = ['key1', 'key2', 'key3']

        self.assertListEqual(with_spaces, expected)
        self.assertListEqual(without, expected)

    def test_type_dict(self):
        type_dict = Type(dict)
        with_spaces = type_dict.value_to_type('orderBy: DESC, select: name')
        without = type_dict.value_to_type('orderBy:DESC,select:name')
        expected = {'orderBy': 'DESC', 'select': 'name'}

        self.assertDictEqual(with_spaces, expected)
        self.assertDictEqual(without, expected)

    def test_supported_types(self):
        for i in ALLOWED_TYPES:
            Type(i)

        with self.assertRaises(NotAllowedType):
            Type(set)

    def test_enum(self):
        type_enum = Enum('test1', 'test2')

        self.assertEqual(None, type_enum.validate('test1'))
        self.assertEqual(
            ["Incorrect value bad. Allowed values: ('test1', 'test2')"],
            type_enum.validate('bad')
        )

    def test_max_len(self):
        rule_max = MaxLength(5)

        self.assertEqual(None, rule_max.validate('test'))
        self.assertEqual(
            ['Invalid length for value very_long. Max length = 5'],
            rule_max.validate('very_long')
        )

    def test_mix_len(self):
        min_len = MinLength(4)

        self.assertEqual(None, min_len.validate('test'))
        self.assertEqual(
            ['Invalid length for value les. Min length = 4'],
            min_len.validate('les')
        )

    def test_pattern(self):
        rule = Pattern(r'^[a-zA-Z0-9-_.]{5,20}$')

        self.assertEqual(None, rule.validate('test_5'))
        self.assertEqual(
            ['Value test_5# does not match pattern %s' % rule.pattern.pattern],
            rule.validate('test_5#')
        )

    def test_composite(self):
        pattern = r'^\w+$'
        rule = CompositeRule(Required(), MinLength(4), Pattern(pattern))
        self.assertEqual([], rule.validate('test'))

        self.assertEqual(
            [
                'Invalid length for value m!n. Min length = 4',
                'Value m!n does not match pattern %s' % pattern,
            ],
            rule.validate('m!n')
        )
