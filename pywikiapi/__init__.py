"""Minimalistic MediaWiki API library by the author of the MediaWiki API itself.
See README.md"""

__version__ = "4.1.1"

__author__ = "Yuri Astrakhan"
__copyright__ = "Copyright (C) 2018-2020 Yuri Astrakhan"
__license__ = "MIT License"
__email__ = "YuriAstrakhan@gmail.com"

from .Site import Site
from .api import wikipedia
from .utils import ApiError, ApiPagesModifiedError, AttrDict, to_datetime, to_timestamp
