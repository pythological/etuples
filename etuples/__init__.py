import importlib.metadata

from .core import etuple
from .dispatch import apply, arguments, etuplize, operator, rands, rator, term

__version__ = importlib.metadata.version("etuples")
