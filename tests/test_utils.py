import unittest
from datetime import datetime as dt

from pywikiapi import to_timestamp, to_datetime
from .utils import UTC, NonUTC


class Tests_Utils(unittest.TestCase):
    def test_to_timestamp(self):
        self.assertEqual(to_timestamp(dt(year=2000, month=1, day=1, hour=2, minute=42)), '2000-01-01T02:42:00Z')
        self.assertEqual(to_timestamp(dt(year=2000, month=1, day=1, hour=2, minute=42).replace(tzinfo=UTC())),
                         '2000-01-01T02:42:00Z')
        self.assertRaises(ValueError, lambda: to_timestamp(dt(year=2000, month=1, day=1).replace(tzinfo=NonUTC())))

    def test_to_datetime(self):
        original = '2000-01-01T02:42:00Z'
        result = to_datetime(original)
        self.assertEqual(result, dt(year=2000, month=1, day=1, hour=2, minute=42))
        self.assertEqual(to_timestamp(result), original)


if __name__ == '__main__':
    unittest.main()
