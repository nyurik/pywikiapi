from datetime import tzinfo, timedelta as td


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
