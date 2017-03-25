from unittest import TestCase

from flask_request_validator import Enum
from flask_request_validator import Required
from flask_request_validator import Type
from flask_request_validator.rules import MaxLength, MinLength, Pattern, CompositeRule


class TestRules(TestCase):

    def test_required(self):
        required = Required()

        self.assertEqual(['Value is required'], required.validate(None))
        self.assertEqual(None, required.validate('value'))

    def test_type_str(self):
        type_rule = Type(str)

        self.assertEqual(None, type_rule.validate(u'test'))
        self.assertEqual(None, type_rule.validate('test'))
        self.assertEqual(['Invalid type for value None'], type_rule.validate(None))

    def test_type_int(self):
        type_int = Type(int)

        self.assertEqual(None, type_int.validate(1))
        self.assertEqual(None, type_int.validate(u'1'))
        self.assertEqual(None, type_int.validate('1'))
        self.assertEqual(['Invalid type for value 1test'], type_int.validate('1test'))

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
        rule = CompositeRule(Required(), Pattern(r'^[a-zA-Z0-9-_.]{5,20}$'))

        self.assertEqual([], rule.validate('test_5'))
        self.assertEqual(
            [
                'Value is required',
                'Value None does not match pattern ^[a-zA-Z0-9-_.]{5,20}$'
            ],
            rule.validate(None)
        )
