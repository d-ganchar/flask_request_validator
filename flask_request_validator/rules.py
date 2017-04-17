import re


class AbstractRule(object):

    def validate(self, value):
        """
        :param mixed value:
        :rtype: list|None
        :return: errors
        :rtype: list
        """
        raise NotImplementedError()


class CompositeRule(AbstractRule):

    def __init__(self, *rules):
        """
        :param tuple rules: (Rule(), Rule())
        """
        self.rules = rules

    def validate(self, value):
        errors = []
        for rule in self.rules:
            if isinstance(rule, Required) or value:
                error = rule.validate(value)
                if error:
                    errors.extend(error)

        return errors


class Required(AbstractRule):

    def validate(self, value):
        if not value:
            return ['Value is required']


class Pattern(AbstractRule):

    def __init__(self, pattern):
        """
        :param str pattern:
        """
        self.pattern = re.compile(pattern)

    def validate(self, value):
        if not self.pattern.search(value):
            return ['Value %s does not match pattern %s' % (value, self.pattern.pattern)]


class Enum(AbstractRule):

    def __init__(self, *allowed_values):
        """
        :param tuple allowed_values:
        """
        self.allowed_values = allowed_values

    def validate(self, value):
        if value not in self.allowed_values:
            return ['Incorrect value %s. Allowed values: %s' % (value, self.allowed_values)]


class Type(AbstractRule):

    def __init__(self, value_type):
        self.value_type = value_type

    def validate(self, value):
        try:
            if self.value_type == bool:
                value = value.lower()
                if value not in ('true', '1', 'false', '0'):
                    return ['Invalid type for value %s' % value]

            value = self.value_type(value)
        except ValueError:
            return ['Invalid type for value %s' % value]


class MaxLength(AbstractRule):

    def __init__(self, length):
        """

        :param int length:
        """
        self.length = length

    def validate(self, value):
        if len(value) > self.length:
            return ['Invalid length for value %s. Max length = %s' % (value, self.length)]


class MinLength(AbstractRule):

    def __init__(self, length):
        """

        :param int length:
        """
        self.length = length

    def validate(self, value):
        if len(value) < self.length:
            return ['Invalid length for value %s. Min length = %s' % (value, self.length)]
