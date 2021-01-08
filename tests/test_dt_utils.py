import unittest

from flask_request_validator.dt_utils import dt_from_iso


class TestDtUtils(unittest.TestCase):
    def test_dt_from_iso(self):
        self.assertTrue(dt_from_iso('2008-09-03T20:56:35.450686Z'))
