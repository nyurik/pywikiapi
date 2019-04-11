import unittest
from datetime import datetime as dt, timedelta as td, tzinfo

from pywikiapi import Site


class UTC(tzinfo):
    """Simple UTC tzinfo to avoid external deps"""

    def utcoffset(self, dt):
        return td()

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return td()


class NonUTC(tzinfo):
    """Simple NON-UTC tzinfo to avoid external deps"""

    def utcoffset(self, dt):
        return td(hours=1)

    def tzname(self, dt):
        return "NonUTC"

    def dst(self, dt):
        return None


class Tests_CallPrep(unittest.TestCase):

    def test_call_prep_types(self):
        site = Site('url')

        method, request_kw = site._prepare_call(
            'query', dict(
                none=None,
                str='str',
                strEmpty='',
                boolT=True,
                bootF=False,
                int=42,
                int0=0,
                datetime=dt(year=2000, month=1, day=1, hour=2, minute=42),
                datetimeUtc=dt(year=2000, month=1, day=1, hour=2, minute=42).replace(tzinfo=UTC()),
                listEmpty=[],
                list=[None, 'str', '', True, False, 42, 0, dt(year=2000, month=1, day=1, hour=2, minute=42)],
            ))

        self.assertEqual('GET', method)
        self.assertDictEqual(request_kw, dict(
            force_ssl=False,
            params=dict(
                format='json',
                action='query',
                str='str',
                strEmpty='',
                boolT='1',
                int='42',
                int0='0',
                datetime='2000-01-01T02:42:00Z',
                datetimeUtc='2000-01-01T02:42:00Z',
                listEmpty='',
                list='str||1|42|0|2000-01-01T02:42:00Z',
            )))

    def test_call_prep_login(self):
        site = Site('url')

        method, request_kw = site._prepare_call('login', dict(test='abc'))

        self.assertEqual('POST', method)
        self.assertDictEqual(request_kw, dict(
            force_ssl=True,
            data=dict(
                format='json',
                action='login',
                test='abc',
            )))

    def test_call_prep_dt_err(self):
        site = Site('url')
        params = dict(dt=dt(year=2000, month=1, day=1).replace(tzinfo=NonUTC()))
        self.assertRaises(ValueError, lambda: site._prepare_call('query', params))


if __name__ == '__main__':
    unittest.main()