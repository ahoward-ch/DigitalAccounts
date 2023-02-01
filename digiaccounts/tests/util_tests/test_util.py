"""unit tests for digiaccounts utility functions"""

from digiaccounts.digiaccounts_util import (
    check_unit_gbp,
    check_instant_date,
    check_name_is_string,
    check_string_in_name
)


def test_check_unit_gbp(yield_xbrl_instance):
    """unit test for check_unit_gbp.

    Success:
        assert fact 'coh1' as True
        assert fact 'dir1' as False

    Args:
        yield_xbrl_instance (fixture): xbrl instance generator
    """
    inst = yield_xbrl_instance()
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_unit_gbp(fact)
        elif fact.xml_id == 'dir1':
            assert not check_unit_gbp(fact)


def test_check_instant_date(yield_xbrl_instance):
    """unit test for check_instant_date.

    Success:
        assert fact 'coh1' as True
        assert fact 'dir1' as False

    Args:
        yield_xbrl_instance (fixture): xbrl instance generator
    """
    inst = yield_xbrl_instance()
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_instant_date(fact)
        elif fact.xml_id == 'dir1':
            assert not check_instant_date(fact)


def test_check_name_is_string(yield_xbrl_instance):
    """unit test for check_name_is_string.

    Success:
        assert fact 'coh1' as True when string is 'CashBankOnHand'
        assert fact 'dir1' as False when string is 'CashBankOnHand'

    Args:
        yield_xbrl_instance (fixture): xbrl instance generator
    """
    inst = yield_xbrl_instance()
    coh1_fact_name = 'CashBankOnHand'
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_name_is_string(coh1_fact_name, fact)
        elif fact.xml_id == 'dir1':
            assert not check_name_is_string(coh1_fact_name, fact)


def test_check_string_in_name(yield_xbrl_instance):
    """unit test for check_string_in_name.

    Success:
        assert fact 'coh1' as True when string is 'Bank'
        assert fact 'dir1' as False when string is 'Bank'

    Args:
        yield_xbrl_instance (fixture): xbrl instance generator
    """
    inst = yield_xbrl_instance()
    coh1_fact_partial_name = 'Bank'
    for fact in inst.facts:
        if fact.xml_id == 'coh1':
            assert check_string_in_name(coh1_fact_partial_name, fact)
        elif fact.xml_id == 'dir1':
            assert not check_string_in_name(coh1_fact_partial_name, fact)
