import logging
from typing import Union, Tuple
import json
import os
import sys
import requests
from requests.structures import CaseInsensitiveDict

from .utils import ApiError, ApiPagesModifiedError

PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,
    unicode = str
else:
    # noinspection PyUnresolvedReferences
    string_types = basestring,

try:
    import urllib.parse as urlparse
except ImportError:
    # noinspection PyUnresolvedReferences
    import urlparse


class Site(object):
    """
    This object represents a MediaWiki API endpoint, e.g. https://en.wikipedia.org/w/api.php
    * url: Full url to site's api.php
    * session: current request.session object
    * log: an object that will be used for logging. ConsoleLog is created by default
    """

    def __init__(self, url, headers=None, session=None, logger=None, json_object_hook=None):
        """
        Create a new Site object with a given MediaWiki API endpoint.
        You should always set a `User-Agent` header to identify your bot and allow
        site owner to contact you in case your bot misbehaves.
        By default, User-Agent is set to the dir name + script name of your bot.
        :param str url: API endpoint URL, e.g. https://en.wikipedia.org/w/api.php
        :param Union[dict, CaseInsensitiveDict] headers: Optional headers as a dictionary.
        :param requests.Session session: Allows user-supplied custom Session parameters, e.g. retries
        :param logging.Logger logger: Optional logger object for custom log output
        :param object json_object_hook: use this param to set a custom json object creator,
            e.g. pywikiapi.AttrDict. AttrDict allows direct property access to the result,
            e.g response.query.allpages in addition to response['query']['allpages']
        """
        if logger is None:
            self.logger = logging.getLogger('pywikiapi')
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger

        self.json_object_hook = json_object_hook
        self.session = session if session else requests.Session()
        self.url = url
        self.tokens = {}
        self.no_ssl = False  # For non-ssl sites, might be needed to avoid HTTPS

        # This var will contain (username,password) after the .login() in case of the login-on-demand mode
        self._loginOnDemand = False  # type: Union[Tuple[unicode, unicode], bool]

        self.headers = CaseInsensitiveDict()
        if headers:
            self.headers.update(headers)
        if u'User-Agent' not in self.headers:
            try:
                script = os.path.abspath(sys.modules['__main__'].__file__)
            except (KeyError, AttributeError):
                script = sys.executable
            path, f = os.path.split(script)
            self.headers[u'User-Agent'] = u'%s-%s pywikiapi/0.1' % (os.path.basename(path), f)

    def __call__(self, action, **kwargs):
        """
            Make an API call with any arguments provided as named values:

                data = site('query', meta='siteinfo')

            By default uses GET request to the default URL set in the Site constructor.
            In case of an error, ApiError exception will be raised
            Any warnings will be logged via the logging interface

            :param unicode action : any of the MW API actions, e.g. 'query' and 'login'

            Several special "magic" parameters could be used to customize api call.
            Special parameters must be all CAPS to avoid collisions with the server API:
            :param POST: Use POST method when calling server API. Value is ignored.
            :param HTTPS: Force https (ssl) protocol for this request. Value is ignored.
            :param SSL: Same as HTTPS
            :param EXTRAS: Any extra parameters as passed to requests' session.request(). Value is a dict()
        """
        # Magic CAPS parameters
        method = 'POST' if 'POST' in kwargs or action in ['login', 'edit'] else 'GET'
        force_ssl = not self.no_ssl and (action == 'login' or 'SSL' in kwargs or 'HTTPS' in kwargs)
        request_kw = dict() if 'EXTRAS' not in kwargs else kwargs['EXTRAS']

        # Clean up magic CAPS params as they shouldn't be passed to the server
        for k in ['POST', 'SSL', 'HTTPS', 'EXTRAS']:
            if k in kwargs:
                del kwargs[k]

        for k, val in kwargs.items():
            # Only support the well known types.
            # Everything else should be client's responsibility
            if isinstance(val, list) or isinstance(val, tuple) or isinstance(val, set):
                kwargs[k] = u'|'.join([unicode(v) for v in val])

        # Make server call
        kwargs['action'] = action
        kwargs['format'] = 'json'

        if method == 'POST':
            request_kw['data'] = kwargs
        else:
            request_kw['params'] = kwargs

        if self._loginOnDemand and action != 'login':
            self.login(self._loginOnDemand[0], self._loginOnDemand[1])

        data = self.parse_json(self.request(method, force_ssl=force_ssl, **request_kw))

        # Handle success and failure
        if 'error' in data:
            raise ApiError('Server API Error', data['error'])
        if 'warnings' in data:
            self.logger.warning('server-warnings', {'warnings': data['warnings']})
        return data

    def login(self, user, password, on_demand=False):
        """
        :param str user: user login name
        :param str password: user password
        :param bool on_demand: if True, will postpone login until an actual API request is made
        """
        self.tokens = {}
        if on_demand:
            self._loginOnDemand = (user, password)
            return
        res = self('login', lgname=user, lgpassword=password)['login']
        if res['result'] == 'NeedToken':
            res = self('login', lgname=user, lgpassword=password, lgtoken=res['token'])['login']
        if res['result'] != 'Success':
            raise ApiError('Login failed', res)
        self._loginOnDemand = False

    def query(self, **kwargs):
        """
        Call Query API with given parameters, and yield all results returned
        by the server, properly handling result continuation.
        """
        return self.iterate('query', **kwargs)

    def iterate(self, action, **kwargs):
        """
        Call any "continuation" style MW API with given parameters, such as the 'query' API.
        Yields all results returned by the server, properly handling result continuation.
        :param action str: MW API action, e.g. 'query'
        :param kwargs: any API parameters
        :return: yields each response from the server
        """
        if 'rawcontinue' in kwargs:
            raise ValueError("rawcontinue is not supported with query() function, use object's __call__()")
        if 'formatversion' in kwargs:
            raise ValueError("version is not supported with query() function, use object's __call__()")
        if 'continue' not in kwargs:
            kwargs['continue'] = ''
        req = kwargs
        req['formatversion'] = 2
        while True:
            result = self(action, **req)
            if action in result:
                yield result[action]
            if 'continue' not in result:
                break
            # re-send all continue values in the next call
            req = kwargs.copy()
            req.update(result['continue'])

    def query_pages(self, **kwargs):
        """
        Query the server and yield all page objects one by one.
        This method makes sure that results received in multiple responses are
        correctly merged together.
        """
        incomplete = {}
        changed = set()
        for result in self.query(**kwargs):
            if 'pages' not in result:
                raise ApiError('Missing pages element in query result', result)

            finished = incomplete.copy()
            for page in result['pages']:
                page_id = page['pageid']
                if page_id in changed:
                    continue
                if page_id in incomplete:
                    del finished[page_id]  # If server returned it => not finished
                    p = incomplete[page_id]
                    if 'lastrevid' in page and p['lastrevid'] != page['lastrevid']:
                        # someone else modified this page, it must be requested anew separately
                        changed.add(page_id)
                        del incomplete[page_id]
                        continue
                    self._merge_page(p, page)
                else:
                    p = page
                incomplete[page_id] = p
            for page_id, page in finished.items():
                if page_id not in changed:
                    yield page

        for page_id, page in incomplete.items():
            yield page

        if changed:
            # some pages have been changed between api calls, notify caller
            raise ApiPagesModifiedError(list(changed))

    def _merge_page(self, a, b):
        """
        Recursively merge two page objects
        """
        for k in b:
            val = b[k]
            if k in a:
                if isinstance(val, dict):
                    self._merge_page(a[k], val)
                elif isinstance(val, list):
                    a[k] = a[k] + val
                else:
                    a[k] = val
            else:
                a[k] = val

    def token(self, token_type='csrf'):
        """
        Get an api token.
        :param str token_type:
        :return: str
        """
        if token_type not in self.tokens:
            self.tokens[token_type] = next(self.query(meta='tokens', type=token_type))['tokens'][token_type + 'token']
        return self.tokens[token_type]

    def request(self, method, force_ssl=False, headers=None, **request_kw):
        """Make a low level request to the server"""
        url = self.url
        if force_ssl:
            parts = list(urlparse.urlparse(url))
            parts[0] = 'https'
            url = urlparse.urlunparse(parts)
        if headers:
            h = self.headers.copy()
            h.update(headers)
            headers = h
        else:
            headers = self.headers

        r = self.session.request(method, url, headers=headers, **request_kw)
        if not r.ok:
            raise ApiError('Call failed', r)

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('server-response', {'url': r.request.url, 'headers': headers})
        return r

    def parse_json(self, value):
        """
        Utility function to convert server reply into a JSON object.
        By default, JSON objects support direct property access (JavaScript style)
        """
        if isinstance(value, string_types):
            return json.loads(value, object_hook=self.json_object_hook)
        elif hasattr(value.__class__, 'json'):
            return value.json(object_hook=self.json_object_hook)
        else:
            # Our servers still have requests 0.8.2 ... :(
            return json.loads(value.content, object_hook=self.json_object_hook)
