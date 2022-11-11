"""functions for extracting information from digital accounts (iXBRL files)
"""

import logging
import pandas as pd


def get_financial_facts(xbrl_instance):
    """create lists for the financial tables in XBRL file instances of accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        dict: a dictionary of the financial data from the accounts, listing the Fact, Value and Date for each data point
    """
    names = []
    values = []
    dates = []

    for fact in xbrl_instance.facts:
        if (hasattr(fact.context, 'instant_date')) and (hasattr(fact, 'unit')):
            if fact.concept.name == 'Creditors':
                if 'MaturitiesOrExpirationPeriodsDimension' in fact.json()['dimensions']:
                    if fact.json()['dimensions']['MaturitiesOrExpirationPeriodsDimension'] == 'WithinOneYear':
                        period = 'DueWithinOneYear'
                        names.append(fact.concept.name + period)
                    else:
                        period = 'DueAfterOneYear'
                        names.append(fact.concept.name + period)
                elif 'FinancialInstrumentCurrentNon-currentDimension' in fact.json()['dimensions']:
                    if fact.json()['dimensions']['FinancialInstrumentCurrentNon-currentDimension'] == 'CurrentFinancialInstruments':
                        period = 'DueWithinOneYear'
                        names.append(fact.concept.name + period)
                    else:
                        period = 'DueAfterOneYear'
                        names.append(fact.concept.name + period)
                else:
                    raise KeyError(fact.json())
            elif (fact.concept.name == 'Equity') and ('EquityClassesDimension' in fact.json()['dimensions']):
                entity_type = fact.json()['dimensions']['EquityClassesDimension']
                names.append(fact.concept.name + entity_type)
            else:
                names.append(fact.concept.name)
            values.append(fact.value)
            dates.append(fact.context.instant_date.isoformat())
    return {'Fact': names, 'Value': values, 'Date': dates}


def get_financial_table(xbrl_instance):
    """formats and returns a pandas dataframe of finanical data contained within an XBRL file instance of accounts
    information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        pf (DataFrame): a pandas dataframe containing the finanical information split out by reporting period start and
        end date
    """
    financial_dict = get_financial_facts(xbrl_instance)

    df = pd.DataFrame(financial_dict)
    mask = df[['Fact', 'Date']].duplicated(keep=False)
    df.loc[mask, 'Fact'] += df.groupby(['Fact', 'Date']).cumcount().add(1).astype(str)

    return df.pivot(index='Fact', columns='Date', values='Value').reset_index()


def get_startend_period(xbrl_instance):
    """extracts and returns the start and end dates for the reporting period covered by an XBRL file instance of
    accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the reporting period
        start and end dates need to be extracted

    Returns:
        start (string): a datetime date object containing the reporting period start date
        end (string): a datetime date object containing the reporting period end date
    """
    for fact in xbrl_instance.facts:
        if fact.concept.name == 'StartDateForPeriodCoveredByReport':
            start = fact.context.instant_date.isoformat()
        elif fact.concept.name == 'EndDateForPeriodCoveredByReport':
            end = fact.context.instant_date.isoformat()
        else:
            pass
    return start, end


def get_company_address(xbrl_instance):
    """extracts and returns the registered company address from an XBRL file instance of accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the company address
        needs to be extracted

    Returns:
        address_df (DataFrame): a pandas dataframe containing the company address
    """
    address = {}
    address_variables_flags = [
        'AddressLine',
        'PrincipalLocation',
        'PostalCodeZip'
    ]
    for fact in xbrl_instance.facts:
        if any(s in fact.concept.name for s in address_variables_flags):
            if fact.concept.name in address:
                address[fact.concept.name].append(fact.value)
            else:
                address[fact.concept.name] = [fact.value]
        else:
            pass
    address_df = pd.DataFrame(address)
    return address_df

def get_company_registration(xbrl_instance):
    """extracts and returns the registered company registration number from an XBRL file instance of accounts
    information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the company
        registration needs to be extracted

    Returns:
        string: a string containing the company registration number
    """
    for fact in xbrl_instance.facts:
        if fact.concept.name == 'UKCompaniesHouseRegisteredNumber':
            return fact.value
        else:
            pass
                