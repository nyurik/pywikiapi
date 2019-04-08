import unittest
from datetime import datetime, tzinfo

from pywikiapi import Site


class Tests_CallPrep(unittest.TestCase):

    def test_call_prep_types(self):
        site = Site('url')

        method, request_kw = site._prepare_call(
            'query', dict(
                none=None,
                str='str', strEmpty='',
                boolT=True, bootF=False,
                int=42, int0=0,
                datetime=datetime(year=2000, month=1, day=1, hour=2, minute=42),
                listEmpty=[],
                list=[None, 'str', '', True, False, 42, 0, datetime(year=2000, month=1, day=1, hour=2, minute=42)],
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
                datetime='2000-01-01T02:42:00',
                listEmpty='',
                list='str||1|42|0|2000-01-01T02:42:00',
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


if __name__ == '__main__':
    unittest.main()
