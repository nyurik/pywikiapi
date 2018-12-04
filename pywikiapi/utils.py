import json


class ApiError(Exception):
    """
    Any error reported by the API is included in this exception
    """

    def __init__(self, message, data):
        self.message = message
        self.data = data

    def __str__(self):
        return self.message + ': ' + json.dumps(self.data)


class ApiPagesModifiedError(ApiError):
    """
    This error is thrown by queryPage() if revision of some pages was changed between calls.
    """

    def __init__(self, data):
        super(ApiError, self).__init__('Pages modified during iteration', data)


class AttrDict(dict):
    """
    Taken from http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python/25320214
    But it seems we should at some point switch to https://pypi.python.org/pypi/attrdict
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
