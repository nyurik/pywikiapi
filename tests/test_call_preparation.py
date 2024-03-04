import unittest
from datetime import datetime as dt

from pywikiapi import Site
from .utils import UTC, NonUTC


# noinspection PyPep8Naming
class Tests_CallPrep(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.maxDiff = None

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
                datetimeUtc=dt(year=2000, month=1, day=1, hour=2, minute=42)
                    .replace(tzinfo=UTC()),
                listEmpty=[],
                list=[None, 'str', '', True, False, 42, 0,
                      dt(year=2000, month=1, day=1, hour=2, minute=42)],
                list_keys=dict(key1='foo', key2='bar').keys(),
                list_values=dict(key1='foo', key2='bar').values(),
            ))

        self.assertEqual('GET', method)
        self.assertDictEqual(request_kw, dict(
            force_ssl=False,
            params=dict(
                format='json',
                formatversion=2,
                maxlag=30,
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
                list_keys='key1|key2',
                list_values='foo|bar',
            )))

    def test_call_prep_login(self):
        site = Site('url')

        method, request_kw = site._prepare_call('login', dict(test='abc'))

        self.assertEqual('POST', method)
        self.assertDictEqual(request_kw, dict(
            force_ssl=True,
            data=dict(
                format='json',
                formatversion=2,
                action='login',
                test='abc',
                maxlag=30,
            )))

    def test_call_prep_dt_err(self):
        site = Site('url')
        params = dict(dt=dt(year=2000, month=1, day=1).replace(tzinfo=NonUTC()))
        self.assertRaises(ValueError, lambda: site._prepare_call('query', params))


if __name__ == '__main__':
    unittest.main()
