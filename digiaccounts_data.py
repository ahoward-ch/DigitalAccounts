"""functions for extracting information from digital accounts (iXBRL files)
"""

import logging
import pandas as pd


def get_profitloss_facts(xbrl_instance):
    names = []
    values = []
    dates = []

    for fact in xbrl_instance.facts:
        if (hasattr(fact.context, 'instant_date')) and (hasattr(fact, 'unit')):
            if fact.concept.name == 'Creditors':
                period = fact.json()['dimensions']['MaturitiesOrExpirationPeriodsDimension']
                names.append(fact.concept.name + period)
            else:
                names.append(fact.concept.name)
            values.append(fact.value)
            dates.append(fact.context.instant_date)
    return names, values, dates


def create_profitloss_table(xbrl_instance):

    names, values, dates = get_profitloss_facts(xbrl_instance)

    df = pd.DataFrame({'Fact': names, 'Value': values, 'Date': dates})
    mask = df[['Fact', 'Date']].duplicated(keep=False)
    df.loc[mask, 'Fact'] += df.groupby(['Fact', 'Date']).cumcount().add(1).astype(str)
    df['id'] = [i for i in range(int(len(df)/2)) for _ in range(2)]

    pf = df.pivot(index='id', columns='Date', values='Value').reset_index()
    col_list = list(pf.columns)
    col_list.remove('id')
    return pf.merge(df[['Fact', 'id']].drop_duplicates(), how='left', on='id')[['Fact'] + col_list]


def get_startend_period(xbrl_instance):
    for fact in xbrl_instance.facts:
        if fact.concept.name == 'StartDateForPeriodCoveredByReport':
            start = fact.context.instant_date
        elif fact.concept.name == 'EndDateForPeriodCoveredByReport':
            end = fact.context.instant_date
        else:
            pass
    return start, end


def get_company_info(xbrl_instance):
    address = {}
    address_variables_flags = [
        'AddressLine',
        'PrincipalLocation',
        'PostalCodeZip'
    ]
    for fact in xbrl_instance.facts:
        if fact.concept.name == 'UKCompaniesHouseRegisteredNumber':
            reg_number = fact.value
        elif any(s in fact.concept.name for s in address_variables_flags):
            address[fact.concept.name] = [fact.value]
    address_df = pd.DataFrame(address)
    return reg_number, address
