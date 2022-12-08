"""unit tests for digiaccounts_data functions"""

from digiaccounts.digiaccounts_data import (
    get_single_fact,
    get_company_registration,
    get_accounting_software,
    get_dormant_state,
    get_average_employees,
    get_company_postcode,
    get_financial_facts,
    get_financial_table,
    get_startend_period,
    get_company_address,
    get_share_info,
    get_director_names
)


def test_get_single_fact(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string '0000000000' when parsed string 'UKCompaniesHouseRegisteredNumber' and XbrlInstance of
    example_happy.xhtml
    """
    inst = yield_xbrl_instance
    fact_name = 'UKCompaniesHouseRegisteredNumber'
    data_truth = '0000000000'

    assert get_single_fact(fact_name, inst) == data_truth


def test_get_company_registration(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string '0000000000' when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance
    data_truth = '0000000000'

    assert get_company_registration(inst) == data_truth


def test_get_accounting_software(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string 'VsCode' when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance
    data_truth = 'VsCode'

    assert get_accounting_software(inst) == data_truth


def test_get_dormant_state(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return bool False when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance

    assert not get_dormant_state(inst)


def test_get_average_employees(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return int 5 when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance
    data_truth = 5

    assert get_average_employees(inst) == data_truth


def test_get_company_postcode(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return string 'AA1 1AA' when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance
    data_truth = 'AA1 1AA'

    assert get_company_postcode(inst) == data_truth


def test_get_startend_period(yield_xbrl_instance):
    """test get_single_fact function

    Expected to return tuple ('2020-01-01', '2020-12-31') when parsed XbrlInstance of example_happy.xhtml
    """
    inst = yield_xbrl_instance
    data_truth = ('2020-01-01', '2020-12-31')

    assert get_startend_period(inst) == data_truth


def test_get_financial_facts(yield_xbrl_instance, yield_financial_dict):
    inst = yield_xbrl_instance
    data_truth = yield_financial_dict

    data_test = get_financial_facts(inst)

    assert sorted(data_test['Fact']) == sorted(data_truth['Fact'])
    assert sorted(data_test['Value']) == sorted(data_truth['Value'])
    assert sorted(data_test['Date']) == sorted(data_truth['Date'])


def test_get_financial_table(yield_xbrl_instance, yield_financial_table):
    inst = yield_xbrl_instance
    column_truth, data_truth = yield_financial_table

    dataframe_test = get_financial_table(inst)
    column_test = dataframe_test.columns.to_list()
    data_test = dataframe_test.values.tolist()
    assert sorted(column_test) == sorted(column_truth)
    assert sorted(data_test) == sorted(data_truth)


def test_get_company_address(yield_xbrl_instance, yield_address_table):
    inst = yield_xbrl_instance
    column_truth, data_truth = yield_address_table

    dataframe_test = get_company_address(inst)
    column_test = dataframe_test.columns.to_list()
    data_test = dataframe_test.values.tolist()
    assert sorted(column_test) == sorted(column_truth)
    assert sorted(data_test) == sorted(data_truth)


def test_get_share_info(yield_xbrl_instance, yield_share_table):
    inst = yield_xbrl_instance
    data_truth = yield_share_table

    data_test = get_share_info(inst)
    assert sorted(data_test) == sorted(data_truth)


def test_get_director_names(yield_xbrl_instance):
    inst = yield_xbrl_instance
    data_truth = {
        'Director1': 'J SMITH',
        'Director2': 'F BLOGS'
    }

    assert get_director_names(inst) == data_truth
