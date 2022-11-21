"""contains common root pytest fixtures"""

from os import path
import pytest

from xbrl.cache import HttpCache
from xbrl.instance import XbrlParser


@pytest.fixture(name='yield_xbrl_instance', scope='session')
def fixture_yield_xbrl_instance(sad=False):
    """fixture for generating an XBRL instance for unit testing"""
    cache = HttpCache('./test_cache')
    parser = XbrlParser(cache)

    schema = path.join('digiaccounts', 'tests', 'data', 'example_happy.xhtml')

    yield parser.parse_instance(schema)
