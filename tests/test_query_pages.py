import unittest
from typing import List

import responses
from urllib.parse import urlparse, parse_qs

from pywikiapi import Site


class Tests_QueryPages(unittest.TestCase):

    @responses.activate
    def test_query_pages_empty(self):
        answers = [{}]
        pages = self.init(answers).query_pages()
        self.assertEqual(next(pages, None), None)
        self.assertEqual(1, len(responses.calls))
        self.assert_call(0, {})

    @responses.activate
    def test_query_pages_single(self):
        answers = [{'query': {'pages': [
            {'pageid': 1},
        ]}}]
        pages = self.init(answers).query_pages()
        self.assertDictEqual(next(pages), {'pageid': 1})
        self.assertEqual(1, len(responses.calls))
        self.assert_call(0, {})

        self.assertEqual(next(pages, None), None)
        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_query_pages_two_samereq(self):
        answers = [{'query': {'pages': [
            {'pageid': 1},
            {'pageid': 2},
        ]}}]
        pages = self.init(answers).query_pages()
        self.assertDictEqual(next(pages), {'pageid': 1})
        self.assertEqual(1, len(responses.calls))
        self.assert_call(0, {})

        self.assertDictEqual(next(pages), {'pageid': 2})
        self.assertEqual(1, len(responses.calls))

        self.assertEqual(next(pages, None), None)
        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_query_pages_page_split_two_req(self):
        answers = [{'continue': {'c': 'yes'}, 'query': {'pages': [
            {'pageid': 1, 'abc': 2},
        ]}}, {'query': {'pages': [
            {'pageid': 1, 'xyz': 3},
        ]}}]

        pages = self.init(answers).query_pages()
        self.assertDictEqual(next(pages), {'pageid': 1, 'abc': 2, 'xyz': 3})
        self.assertEqual(2, len(responses.calls))
        self.assert_call(0, {})
        self.assert_call(1, {'c': 'yes'})

        self.assertEqual(next(pages, None), None)
        self.assertEqual(2, len(responses.calls))

    @responses.activate
    def test_query_pages_page_split_two_req_more(self):
        answers = [{'continue': {'c': 'A'}, 'query': {'pages': [
            {'pageid': 1},
        ]}}, {'continue': {'c': 'B'}, 'query': {'pages': [
            {'pageid': 2},
        ]}}, {'query': {'pages': [
            {'pageid': 3},
        ]}}]

        pages = self.init(answers).query_pages()
        self.assertDictEqual(next(pages), {'pageid': 1})
        self.assertEqual(2, len(responses.calls))
        self.assert_call(0, {})
        self.assert_call(1, {'c': 'A'})

        self.assertDictEqual(next(pages), {'pageid': 2})
        self.assertEqual(3, len(responses.calls))
        self.assert_call(2, {'c': 'B'})

        self.assertDictEqual(next(pages), {'pageid': 3})
        self.assertEqual(3, len(responses.calls))

        self.assertEqual(next(pages, None), None)
        self.assertEqual(3, len(responses.calls))

    def init(self, answers: List[dict]):
        api_url = 'http://example.org/api.php'
        responses.reset()
        for r in answers:
            responses.add(method=responses.GET, url=api_url, json=r)
        return Site(url=api_url)

    def assert_call(self, index, expected: dict):
        self.assertLess(index, len(responses.calls))
        req = urlparse(responses.calls[index].request.url, allow_fragments=False)
        expected = {**expected, 'action': 'query', 'format': 'json', 'formatversion': '2'}
        expected = {k: [v] for k, v in expected.items()}
        self.assertDictEqual(parse_qs(req.query), expected)


if __name__ == '__main__':
    unittest.main()
