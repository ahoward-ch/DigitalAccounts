from os import path
import pytest


from xbrl.cache import HttpCache
from xbrl.instance import XbrlParser, XbrlInstance

from digiaccounts.digiaccounts_data import (
    check_unit_gbp,
    check_instant_date,
    check_name_is_string,
    check_string_in_name
)


@pytest.fixture(name='yield_xbrl_instance', scope='module')
def fixture_yield_xbrl_instance(sad=False):
    cache = HttpCache('./test_cache')
    parser = XbrlParser(cache)

    schema = path.join('digiaccounts', 'tests', 'data', 'example_happy.xhtml')

    yield parser.parse_instance(schema)


def test_check_unit_gbp(yield_xbrl_instance):
    inst = yield_xbrl_instance
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_unit_gbp(fact)
        elif fact.xml_id == 'dir1':
            assert not check_unit_gbp(fact)


def test_check_instant_date(yield_xbrl_instance):
    inst = yield_xbrl_instance
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_instant_date(fact)
        elif fact.xml_id == 'dir1':
            assert not check_instant_date(fact)


def test_check_name_is_string(yield_xbrl_instance):
    inst = yield_xbrl_instance
    coh1_fact_name = 'CashBankOnHand'
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_name_is_string(coh1_fact_name, fact)
        elif fact.xml_id == 'dir1':
            assert not check_name_is_string(coh1_fact_name, fact)


def test_check_string_in_name(yield_xbrl_instance):
    inst = yield_xbrl_instance
    coh1_fact_partial_name = 'Bank'
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_string_in_name(coh1_fact_partial_name, fact)
        elif fact.xml_id == 'dir1':
            assert not check_string_in_name(coh1_fact_partial_name, fact)
