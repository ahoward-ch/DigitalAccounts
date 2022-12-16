"""contains common root pytest fixtures"""

from os import path
import pytest

from xbrl.cache import HttpCache
from xbrl.instance import XbrlParser


@pytest.fixture(name='yield_xbrl_instance', scope='session')
def fixture_yield_xbrl_instance():
    """fixture for generating an XBRL instance for unit testing"""
    cache = HttpCache('./test_cache')
    parser = XbrlParser(cache)

    def _path_select(sad=False):
        if sad:
            schema = path.join('digiaccounts', 'tests', 'data', 'example_unhappy.xhtml')
        else:
            schema = path.join('digiaccounts', 'tests', 'data', 'example_happy.xhtml')
        return parser.parse_instance(schema)
    yield _path_select
