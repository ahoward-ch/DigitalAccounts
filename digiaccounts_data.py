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
        if (check_instant_date(fact)) and (check_unit_gbp(fact)):
            fact_dimensions = return_dimension_dict(fact)
            if check_name_is_string('creditors', fact):
                if 'MaturitiesOrExpirationPeriodsDimension' in fact_dimensions:
                    if fact_dimensions['MaturitiesOrExpirationPeriodsDimension'] == 'WithinOneYear':
                        period = 'DueWithinOneYear'
                        names.append(fact.concept.name + period)
                    else:
                        period = 'DueAfterOneYear'
                        names.append(fact.concept.name + period)
                elif 'FinancialInstrumentCurrentNon-currentDimension' in fact_dimensions:
                    if (fact_dimensions['FinancialInstrumentCurrentNon-currentDimension']
                        == 'CurrentFinancialInstruments'):
                        period = 'DueWithinOneYear'
                        names.append(fact.concept.name + period)
                    else:
                        period = 'DueAfterOneYear'
                        names.append(fact.concept.name + period)
                else:
                    raise KeyError(fact.json())
            elif (check_name_is_string('equity', fact)) and ('EquityClassesDimension' in fact_dimensions):
                entity_type = fact_dimensions['EquityClassesDimension']
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

def get_accounting_software(xbrl_instance):

    for fact in xbrl_instance.facts:
        if fact.concept.name == 'NameProductionSoftware':
            return fact.value

def get_share_info(xbrl_instance):

    share_info = []
    for fact in xbrl_instance.facts:
        if (check_string_in_name('share', fact)):
            name = fact.concept.name
            value = fact.value 
            unit = None
            date = None               
            if check_instant_date(fact):
                date = fact.context.instant_date.isoformat()
            if check_unit_gbp(fact):
                unit = '£'
            share_info.append([name, unit, value, date])
        elif check_name_is_string('equity', fact):
            dimensions = return_dimension_values(fact)
            if any(['share' in v.lower() for v in dimensions]):
                for v in dimensions:
                    if 'share' in v.lower():
                        name = fact.concept.name + v
                        break
                value = fact.value
                unit = None
                date = None
                if check_instant_date(fact):
                    date = fact.context.instant_date.isoformat()
                if check_unit_gbp(fact):
                    unit = '£'
                share_info.append([name, unit, value, date])
    return share_info


def check_unit_gbp(fact):
    if hasattr(fact, 'unit') and (fact.unit.unit == 'iso4217:GBP'):
        return True
    else:
        return False

def check_instant_date(fact):
    if hasattr(fact.context, 'instant_date'):
        return True
    else:
        return False

def check_string_in_name(string, fact):
    if string.lower() in fact.concept.name.lower():
        return True
    else:
        return False

def check_name_is_string(string, fact):
    if fact.concept.name.lower() == string.lower():
        return True
    else:
        return False

def return_dimension_dict(fact):
    return fact.json()['dimensions']

def return_dimension_values(fact):
    return fact.json()['dimensions'].values()
                