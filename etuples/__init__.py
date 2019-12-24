from .core import etuple
from .dispatch import etuplize, apply, rator, rands, term, operator, arguments

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
