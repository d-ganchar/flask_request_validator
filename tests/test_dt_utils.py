import unittest
from datetime import datetime

from flask_request_validator.dt_utils import dt_from_iso


class TestDtUtils(unittest.TestCase):
    def test_dt_from_iso(self):
        self.assertTrue(dt_from_iso(datetime.utcnow().isoformat()))
