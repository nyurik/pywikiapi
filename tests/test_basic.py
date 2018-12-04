import logging
import unittest

from pywikiapi import wikipedia
import requests


class Tests(unittest.TestCase):
    session = None

    @classmethod
    def setUpClass(cls):
        Tests.session = requests.Session()

    @classmethod
    def tearDownClass(cls):
        if Tests.session is not None:
            Tests.session.close()
            Tests.session = None

    def test_url(self):
        """Test default WMF site object creation"""
        site = wikipedia(session=Tests.session)
        self.assertEqual(site.url, 'https://en.wikipedia.org/w/api.php')

    def test_get_metadata(self):
        """Get en.wikipedia metadata"""
        site = wikipedia(session=Tests.session)
        result = site('query', meta='siteinfo')
        self.assertEqual(result.query.general.mainpage, 'Main Page')

    def test_query_pages(self):
        """Iterate over query results for two iterations (list=allpages)"""
        site = wikipedia(session=Tests.session)
        last_result = None
        for res in site.query(list='allpages', aplimit=1):
            self.assertIn('allpages', res)
            self.assertIsInstance(res['allpages'], list)
            self.assertEqual(len(res['allpages']), 1)
            self.assertIsInstance(res['allpages'][0], dict)
            self.assertIsNotNone(res['allpages'][0]['ns'])
            self.assertIsNotNone(res['allpages'][0]['title'])
            self.assertIsNotNone(res['allpages'][0]['pageid'])
            if last_result is None:
                last_result = res['allpages'][0]['pageid']
            else:
                self.assertNotEqual(res['allpages'][0]['pageid'], last_result)
                break


if __name__ == '__main__':
    unittest.main()
