import pytest

from digiaccounts.digiaccounts_data import (
    get_financial_facts,
    get_financial_table,
    get_startend_period,
    get_company_address,
    get_company_registration,
    get_accounting_software,
    get_share_info,
    get_director_names
)


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


def test_get_startend_period(yield_xbrl_instance):
    inst = yield_xbrl_instance

    assert get_startend_period(inst) == ('2020-01-01', '2020-12-31')


def test_get_company_address(yield_xbrl_instance, yield_address_table):
    inst = yield_xbrl_instance
    column_truth, data_truth = yield_address_table

    dataframe_test = get_company_address(inst)
    column_test = dataframe_test.columns.to_list()
    data_test = dataframe_test.values.tolist()
    assert sorted(column_test) == sorted(column_truth)
    assert sorted(data_test) == sorted(data_truth)


def test_get_company_registration(yield_xbrl_instance):
    inst = yield_xbrl_instance

    assert get_company_registration(inst) == '0000000000'


def test_get_accounting_software(yield_xbrl_instance):
    inst = yield_xbrl_instance

    assert get_accounting_software(inst) == 'VsCode'


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
