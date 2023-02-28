"""unit tests for digiaccounts_data functions"""

import pytest
from datetime import datetime

from digiaccounts.digiaccounts_data import (
    get_single_fact,
    get_entity_registration,
    get_accounting_software,
    get_dormant_state,
    get_average_employees,
    get_entity_postcode,
    get_startend_period,
    get_entity_turnover,
    get_intangible_assets,
    get_investment_property,
    get_investment_assets,
    get_biological_assets,
    get_plant_equipment,
    get_entity_equity
)

# DONE: get_single_fact
# DONE: get_single_fact unhappy
# DONE: get_entity_registration
# DONE: get_accounting_software
# DONE: get_average_employees
# DONE: get_dormant_state
# DONE: get_dormant_state unhappy
# DONE: get_startend_period
# TODO: get_startend_period unhappy
# DONE: get_entity_postcode
# TODO: get_entity_postcode unhappy
# TODO: return_openclose_from_fact_list
# TODO: get_openclose_pairs
# TODO: get_openclose_pairs unhappy
# DONE: get_entity_turnover
# DONE: get_intangible_assets
# DONE: get_investment_property
# DONE: get_investment_assets
# DONE: get_biological_assets
# DONE: get_plant_equipment
# DONE: get_entity_equity


def test_get_single_fact(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string '0000000000' when parsed string 'UKCompaniesHouseRegisteredNumber' and XbrlInstance of
    example_happy.xhtml
    """

    inst = yield_xbrl_instance()
    fact_name = 'UKCompaniesHouseRegisteredNumber'
    data_truth = '0000000000'

    assert get_single_fact(fact_name, inst) == data_truth


def test_unhappy_get_single_fact(yield_xbrl_instance):
    """test get_single_fact function in unhappy path

    Expected to return KeyError string '"No fact with concept name \'FalseFact\'."' parsed string
    'FalseFact' and XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance()
    false_fact_name = 'FalseFact'
    with pytest.raises(KeyError) as e_info:
        get_single_fact(false_fact_name, inst)
    assert str(e_info.value) == '"No fact with concept name \'FalseFact\'."'


def test_get_entity_registration(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string '0000000000' when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance()
    data_truth = '0000000000'

    assert get_entity_registration(inst) == data_truth


def test_get_accounting_software(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string 'VsCode' when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance()
    data_truth = 'VsCode'

    assert get_accounting_software(inst) == data_truth


def test_get_average_employees(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return int 5 when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance()
    data_truth = 5

    assert get_average_employees(inst) == data_truth


def test_get_dormant_state(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return bool False when parsed XbrlInstance of example_happy.xhtml
    """
    # DONE: EntityDormantTrueFalse
    # TODO: EntityDormant
    inst = yield_xbrl_instance()

    assert not get_dormant_state(inst)


def test_unhappy_get_dormant_state(yield_xbrl_instance):
    """test get_dormant_state in unhappy path

    Expected to return KeyError string "'No facts relating to dormancy present.'" parsed string XbrlInstance of
    example_unhappy.xhtml
    """
    unhappy_inst = yield_xbrl_instance(sad=True)

    with pytest.raises(KeyError) as e_info:
        get_dormant_state(unhappy_inst)
    assert str(e_info.value) == "'No facts relating to dormancy present.'"


def test_get_startend_period(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return tuple ('2020-01-01', '2020-12-31') when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance()
    data_truth = (datetime.strptime('2020-01-01', '%Y-%m-%d'),
                  datetime.strptime('2020-12-31', '%Y-%m-%d'))

    assert get_startend_period(inst) == data_truth


def test_get_entity_postcode(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string 'AA1 1AA' when parsed XbrlInstance of example_happy.xhtml
    """
    # DONE: no dimensions
    # TODO: with dimensions
    # TODO: multiplicity
    inst = yield_xbrl_instance()
    data_truth = 'AA1 1AA'

    assert get_entity_postcode(inst) == data_truth


def test_get_entity_turnover(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (10000000.0, 20000000.0)

    assert get_entity_turnover(inst) == data_truth


def test_get_intangible_assets(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (110000000.0, 120000000.0)

    assert get_intangible_assets(inst) == data_truth


def test_get_investment_property(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (210000000.0, 220000000.0)

    assert get_investment_property(inst) == data_truth


def test_get_investment_assets(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (310000000.0, 320000000.0)

    assert get_investment_assets(inst) == data_truth


def test_get_biological_assets(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (410000000.0, 420000000.0)

    assert get_biological_assets(inst) == data_truth


def test_get_plant_equipment(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (510000000.0, 520000000.0)

    assert get_plant_equipment(inst) == data_truth


def test_get_entity_equity(yield_xbrl_instance):
    inst = yield_xbrl_instance()
    data_truth = (610000000.0, 620000000.0)

    assert get_entity_equity(inst) == data_truth
