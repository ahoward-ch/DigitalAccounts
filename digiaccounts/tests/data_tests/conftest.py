import pytest

@pytest.fixture(name='yield_financial_dict', scope='module')
def fixture_yield_financial_dict(sad=False):
    yield {'Fact': ['CashBankOnHand',
                    'CashBankOnHand',
                    'InvestmentProperty',
                    'InvestmentProperty',
                    'CreditorsDueWithinOneYear',
                    'CreditorsDueWithinOneYear',
                    'CreditorsDueAfterOneYear',
                    'CreditorsDueAfterOneYear',
                    'EquityShareCapital',
                    'EquityShareCapital',
                    'NominalValueSharesIssuedSpecificShareIssue',
                    'NominalValueSharesIssuedSpecificShareIssue'],
           'Value': [12345000000.0,
                     12345000000.0,
                     9876000000.0,
                     9876000000.0,
                     10000.0,
                     10000.0,
                     20000.0,
                     20000.0,
                     0.0,
                     100.0,
                     0.0,
                     1.0],
           'Date': ['2020-01-01',
                    '2020-12-31',
                    '2020-01-01',
                    '2020-12-31',
                    '2020-01-01',
                    '2020-12-31',
                    '2020-01-01',
                    '2020-12-31',
                    '2020-01-01',
                    '2020-12-31',
                    '2020-01-01',
                    '2020-12-31']}


@pytest.fixture(name='yield_financial_table', scope='module')
def fixture_yield_financial_table(sad=False):
    columns = ['Fact', '2020-01-01', '2020-12-31']
    data = [
        ['CashBankOnHand', 12345000000.0, 12345000000.0],
        ['CreditorsDueAfterOneYear', 20000.0, 20000.0],
        ['CreditorsDueWithinOneYear', 10000.0, 10000.0],
        ['InvestmentProperty', 9876000000.0, 9876000000.0],
        ['EquityShareCapital', 0.0, 100.0],
        ['NominalValueSharesIssuedSpecificShareIssue', 0.0, 1.0]
    ]
    yield columns, data


@pytest.fixture(name='yield_address_table', scope='module')
def fixture_yield_address_table(sad=False):
    columns = ['AddressLine1', 'PrincipalLocation-CityOrTown', 'PostalCodeZip']
    data = [['1A A STREET', 'A TOWN', 'AA1 1AA']]
    yield columns, data


@pytest.fixture(name='yield_share_table', scope='module')
def fixture_yield_share_table(sad=False):
    shares = [
        ['DescriptionReasonsForSpecificShareIssue', None, 'cash at par', None],
        ['DescriptionShareType', None, 'Ordinary', '2020-12-31'],
        ['EquityShareCapital', '£', 0.0, '2020-01-01'],
        ['EquityShareCapital', '£', 100.0, '2020-12-31'],
        ['NominalValueSharesIssuedSpecificShareIssue', '£', 1.0, '2020-12-31'],
        ['NominalValueSharesIssuedSpecificShareIssue', '£', 0.0, '2020-01-01'],
        ['NumberSharesIssuedFullyPaid', None, 100.0, '2020-12-31'],
        ['NumberSharesIssuedFullyPaid', None, 100.0, '2020-12-31'],
        ['NumberSharesIssuedSpecificShareIssue', None, 100.0, None],
        ['ParValueShare', None, 1.0, None]
    ]
    yield shares