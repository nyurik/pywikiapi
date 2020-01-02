# pywikiapi: A Tiny Python MediaWiki API Lib

[![](https://img.shields.io/travis/nyurik/pywikiapi)](https://travis-ci.org/nyurik/pywikiapi)
[![](https://img.shields.io/coveralls/github/nyurik/pywikiapi)](https://coveralls.io/github/nyurik/pywikiapi)
[![](https://img.shields.io/github/issues/nyurik/pywikiapi)](https://github.com/nyurik/pywikiapi/issues)
[![](https://img.shields.io/github/issues-pr/nyurik/pywikiapi)](https://github.com/nyurik/pywikiapi/pulls)

This is a minimalistic library that handles some of the core MediaWiki API complexities like handling continuations, login, errors, and warnings, but does not impose any additional abstraction layers, allowing you to use every single feature of the MW API directly in the most optimal way. 

The library was written by the original author of the MediaWiki API itself, and tries to address some of the mistakes of the original API design... Some things should have been done differently. :)

```python
from pywikiapi import wikipedia
# Connect to English Wikipedia
site = wikipedia('en')

# Iterate over all query results as they are returned
# from the server, handling continuations automatically.
# (pages whose title begins with "New York-New Jersey")
for r in site.query(list='allpages', apprefix='New York-New Jersey'):
  for page in r.allpages:
    print(page.title)

# Iterate over two pages, getting the page info and the list of links for each of the two pages. Each page will be yielded as a separate result.
for page in site.query_pages(titles=['Test', 'API'], prop=['links', 'info'], pllimit=10):
    print(page.title)
    print(', '.join([l.title for l in page.links]))
    print()

site.login('username', 'password')
site('edit', text=...)
```

## Installation

You can install the  from [PyPI](https://pypi.org/project/pywikiapi/):

    pip install pywikiapi

The library requires Python 3.6+

## How to use

* Create a `Site` object, either directly or with the `wikipedia` helper function.
* Use `site.query(...)` or `site.iterate(action, ...)` for all iteration-related API calls. The API will handle all the continuation logic internally.
* Use `site.query_pages(...)` to get one page object at a time from the action=query.
* Use `site('query', meta='siteinfo')` te access any API action, passing any additional params as keys.

### Data formats
The library will properly handle all of the basic parameter types:
* Numbers and strings will be passed as is
* Boolean `True` will be passed as `"1"`.
* `None` and boolean `False` will **not** be included.
* Datetimes will be formatted with `isoformat()`. **Warning:** make sure datetime is in UTC timezone.
* Lists will be converted into a pipe `|` -separated string of values.

## Development
To test, run `python3 setup.py test -q` or use `./test.sh`
