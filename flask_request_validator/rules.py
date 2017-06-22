import re

ALLOWED_TYPES = (str, bool, int, float, dict, list)


class AbstractRule(object):

    def validate(self, value):
        """
        :param mixed value:
        :rtype: list|None
        :return: errors
        :rtype: list
        """
        raise NotImplementedError()


class CompositeRule(object):

    def __init__(self, *rules):
        self.rules = rules

    def __iter__(self):
        for rule in self.rules:
            yield rule


class Pattern(AbstractRule):

    def __init__(self, pattern):
        """
        :param str pattern:
        """
        self.pattern = re.compile(pattern)

    def validate(self, value):
        errors = []
        if not self.pattern.search(value):
            errors.append('Value "%s" does not match pattern %s' %
                          (value, self.pattern.pattern))
        return errors


class Enum(AbstractRule):

    def __init__(self, *allowed_values):
        self.allowed_values = allowed_values

    def validate(self, value):
        errors = []
        if value not in self.allowed_values:
            errors.append('Incorrect value "%s". Allowed values: %s' %
                          (value, self.allowed_values))
        return errors


class MaxLength(AbstractRule):

    def __init__(self, length):
        """

        :param int length:
        """
        self.length = length

    def validate(self, value):
        errors = []
        if len(value) > self.length:
            errors.append('Invalid length for value "%s". Max length = %s' %
                          (value, self.length))
        return errors


class MinLength(AbstractRule):

    def __init__(self, length):
        """

        :param int length:
        """
        self.length = length

    def validate(self, value):
        errors = []
        if len(value) < self.length:
            errors.append('Invalid length for value "%s". Min length = %s'
                          % (value, self.length))
        return errors
