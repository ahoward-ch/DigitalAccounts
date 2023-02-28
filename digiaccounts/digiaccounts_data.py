"""functions for extracting information from digital accounts (iXBRL files)
"""

import logging
# import pandas as pd
import dateutil.parser
import digiaccounts.config as cfg
from digiaccounts.digiaccounts_util import (
    check_name_is_string,
    return_dimension_dict,
    dimension_in_dimension_dict,
    #    check_unit_gbp,
    #    check_string_in_name,
    #    check_instant_date,
    #    return_dimension_values,
)


def get_single_fact(fact_name, xbrl_instance):
    """extracts and returns single fact value from an XBRL file instance of accounts based on a fact concept name

    Args:
        fact_name (str): a string giving the name of an XBRL fact
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Raises:
        KeyError: _description_

    Returns:
        _type_: _description_
    """
    _s = f"Searching instance for single fact: '{fact_name}'"
    logging.info(_s)
    for fact in xbrl_instance.facts:
        if check_name_is_string(fact_name, fact):
            if isinstance(fact.value, str):
                return fact.value.strip()
            else:
                return fact.value
    raise KeyError(cfg.fact_name_error(fact_name))


def get_entity_registration(xbrl_instance):
    """extracts and returns the registered entity registration number from an XBRL file instance of accounts
    information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the entity
        registration needs to be extracted

    Returns:
        string: a string containing the entity registration number
    """
    fact_name = cfg.FACT_NAME_ENTITY_REGISTRATION
    return get_single_fact(fact_name, xbrl_instance)


def get_entity_registered_name(xbrl_instance):
    fact_name = cfg.FACT_NAME_ENTITY_NAME
    return get_single_fact(fact_name, xbrl_instance)


def get_accounting_software(xbrl_instance):
    """extracts and returns the software used to generate the XBRL file

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        str: a string indicating the name of the accounting software used
    """
    fact_name = cfg.FACT_NAME_ACCOUNTING_SOFTWARE
    return get_single_fact(fact_name, xbrl_instance)


def get_average_employees(xbrl_instance):
    """extracts and returns the average number of employees for the accounting period

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        int: an integer indicating the number of employees
    """
    fact_name = cfg.FACT_NAME_AVERAGE_EMPLOYEES
    return get_single_fact(fact_name, xbrl_instance)


def get_dormant_state(xbrl_instance):
    """extracts and returns dormant status of a entity named in an XBRL accounts instance

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        bool: a boolian value for determining dormant state of entity
    """
    fact_names = cfg.FACT_NAME_DORMANT_STATE
    state = False
    for fact_name in fact_names:
        try:
            state = get_single_fact(fact_name, xbrl_instance)
        except KeyError:
            pass
    if state:
        return state.lower() == 'true'
    else:
        raise KeyError(cfg.dormant_state_error())


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
    _s = "Searching instance for period start/end date."
    logging.info(_s)
    start_key = cfg.FACT_NAME_START_DATE
    end_key = cfg.FACT_NAME_END_DATE

    start = None
    end = None

    try:
        start = get_single_fact(start_key, xbrl_instance)
        start = dateutil.parser.parse(start)
    except KeyError:
        pass

    try:
        end = get_single_fact(end_key, xbrl_instance)
        end = dateutil.parser.parse(end)
    except KeyError:
        pass

    if (start is not None) or (end is not None):
        return start, end
    else:
        raise KeyError(cfg.start_end_error(start_key, end_key))


def get_entity_postcode(xbrl_instance):
    """Extracts and returns the primary postcode found within the XBRL tags of an instance of accounts information. Also
    tags any postcodes with supplementary information if it is present.

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the entity address
        needs to be extracted

    Returns:
        str
    """
    _s = "Searching instance for registered post code"
    logging.info(_s)
    fact_name = cfg.FACT_NAME_POSTAL_CODE

    post_codes = {}
    pcn = 1
    for fact in xbrl_instance.facts:
        if check_name_is_string(fact_name, fact):
            code = fact.value.strip()
            dimensions = return_dimension_dict(fact)
            if 'EntityContactTypeDimension' in dimensions:
                key = dimensions['EntityContactTypeDimension'] + str(pcn)
            else:
                key = 'PostCodeUntagged' + str(pcn)
            post_codes[key] = code
            pcn += 1
    if post_codes and any('RegisteredOffice' in k for k in post_codes):
        primary_key = [k for k in post_codes if 'RegisteredOffice' in k][0]
        return post_codes[primary_key]
    elif post_codes:
        return next(iter(post_codes.values())).strip()
    else:
        raise KeyError(cfg.fact_name_error(fact_name))


def return_openclose_from_fact_list(value_date_dict_list, xbrl_instance):
    """return tuple of paired facts associated with starting and ending period when given a list of value/date pairs
    and the XBRL accounts instance they came from

    e.g. return closing and opening turnover

    Args:
        value_date_dict_list (list): list of value/date pairs (as dict) of type float and datetime
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the value/date pairs
        were extracted - used to obtain the start and end period dates

    Returns:
        tuple: values for the closing and opening period
    """
    start, end = get_startend_period(xbrl_instance)

    closing = None
    opening = None

    for item in value_date_dict_list:
        if (
            (opening is None)
            and (start is not None)
            and (item['date'] <= start.date())
        ):
            opening = item['value']
        elif (
            (closing is None)
            and (item['date'] >= end.date())
        ):
            closing = item['value']
        else:
            pass
    return opening, closing


def get_openclose_pairs(xbrl_instance, fact_name, dim_name=None, instant=True):
    """retrieves fact value pairs for closing/opening period (or start/end date)

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the value/date pairs
        were extracted - used to obtain the start and end period dates
        fact_name (str): context name of fact to search for
        dim_name (str, optional): name of fact sub-dimension. Facts with this sub-dimension present will be omitted.
        Defaults to None.
        instant (bool, optional): flag for facts with instant date type. If False, will instead look for end date of
        duration date type. Defaults to True.

    Returns:
        tuple: values for the closing and opening period
    """
    _s = "Searching instance for opening/closing values for fact: '{fact_name}'"
    logging.info(_s)
    fact_list = []

    for fact in xbrl_instance.facts:
        if (
            (check_name_is_string(fact_name, fact)) and
            (
                (dim_name is None) or
                (not dimension_in_dimension_dict(dim_name, fact))
            )
        ):
            fact_list.append({
                'value': fact.value,
                'date': fact.context.instant_date if instant else fact.context.end_date
            })

    if fact_list:
        return return_openclose_from_fact_list(fact_list, xbrl_instance)
    else:
        raise KeyError(cfg.fact_name_error(fact_name))


def get_entity_turnover(xbrl_instance):
    """extracts and returns tuple of closing and opening turnover from an XBRL file containing finanical accounts
    information. Turnover is stored with a duration, not an instant date. This is reflected in the call to
    get_closing_opening_pairs

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening turnover
    """
    fact_name = cfg.FACT_NAME_TURNOVER

    return get_openclose_pairs(xbrl_instance, fact_name, instant=False)


def get_intangible_assets(xbrl_instance):
    """extracts and returns tuple of closing and opening intangible assets from an XBRL file containing finanical
    accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening intangible assets
    """
    fact_name = cfg.FACT_NAME_INTANGIBLE_ASSETS

    return get_openclose_pairs(xbrl_instance, fact_name)


def get_investment_property(xbrl_instance):
    """extracts and returns tuple of closing and opening investment property value from an XBRL file containing
    finanical accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening investment property value
    """
    fact_name = cfg.FACT_NAME_INVESTMENT_PROPERTY

    return get_openclose_pairs(xbrl_instance, fact_name)


def get_investment_assets(xbrl_instance):
    """extracts and returns tuple of closing and opening investment assets value from an XBRL file containing finanical
    accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening investment assets value
    """
    fact_name = cfg.FACT_NAME_INVESTMENT_ASSETS

    return get_openclose_pairs(xbrl_instance, fact_name)


def get_biological_assets(xbrl_instance):
    """extracts and returns tuple of closing and opening biological assets value from an XBRL file containing finanical
    accounts information

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening biological assets value
    """
    fact_name = cfg.FACT_NAME_BIOLOGICAL_ASSETS

    return get_openclose_pairs(xbrl_instance, fact_name)


def get_plant_equipment(xbrl_instance):
    """extracts and returns tuple of closing and opening plant property value from an XBRL file containing finanical
    accounts information. Plant property value has sub-dimensions used for breaking down production plants, equipment
    and vehicles in the extended profit and loss sheet. These sub-dimensions are explicitly ignored, as reflected in the
    call to get_closing_opening_pairs

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening plant property value
    """
    fact_name = cfg.FACT_NAME_PLANT_EQUIPMENT
    dim_name = cfg.FACT_DIMENSION_PLANT_EQUIPMENT

    return get_openclose_pairs(xbrl_instance, fact_name, dim_name=dim_name)


def get_entity_equity(xbrl_instance):
    """extracts and returns tuple of closing and opening balance sheet total from an XBRL file containing finanical
    accounts information. Equity has sub-dimensions used for breaking down different equity sources. These
    sub-dimensions are explicitly ignored, as reflected in the call to get_closing_opening_pairs

    Args:
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        tuple: closing and opening balance sheet total
    """
    fact_name = cfg.FACT_NAME_EQUITY
    dim_name = cfg.FACT_DIMENSION_EQUITY

    return get_openclose_pairs(xbrl_instance, fact_name, dim_name=dim_name)


# def get_financial_facts(xbrl_instance):
#     """create lists for the financial facts in XBRL file instances of accounts information

#     Args:
#         xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
#         to be extracted

#     Returns:
#         dict: a dictionary of the financial data from the accounts, listing the Fact, Value and Date for each data
#         point
#     """
#     names = []
#     values = []
#     dates = []

#     for fact in xbrl_instance.facts:
#         if (check_instant_date(fact)) and (check_unit_gbp(fact)):
#             fact_dimensions = return_dimension_dict(fact)
#             if check_name_is_string('creditors', fact):
#                 if 'MaturitiesOrExpirationPeriodsDimension' in fact_dimensions:
#                     if fact_dimensions['MaturitiesOrExpirationPeriodsDimension'] == 'WithinOneYear':
#                         period = 'DueWithinOneYear'
#                         names.append(fact.concept.name + period)
#                     else:
#                         period = 'DueAfterOneYear'
#                         names.append(fact.concept.name + period)
#                 elif 'FinancialInstrumentclosingNon-closingDimension' in fact_dimensions:
#                     if (fact_dimensions['FinancialInstrumentclosingNon-closingDimension']
#                             == 'closingFinancialInstruments'):
#                         period = 'DueWithinOneYear'
#                         names.append(fact.concept.name + period)
#                     else:
#                         period = 'DueAfterOneYear'
#                         names.append(fact.concept.name + period)
#                 else:
#                     _s = 'Creditors Fact does not contain known credit period key.'
#                     _s_json = f'Fact JSON dictionary: {fact.json()}'
#                     logging.error(_s)
#                     logging.debug(_s_json)
#                     raise KeyError(_s)
#             elif (check_name_is_string('equity', fact)) and ('EquityClassesDimension' in fact_dimensions):
#                 entity_type = fact_dimensions['EquityClassesDimension']
#                 names.append(fact.concept.name + entity_type)
#             else:
#                 names.append(fact.concept.name)
#             values.append(fact.value)
#             dates.append(fact.context.instant_date.isoformat())
#     if names:
#         return {'Fact': names, 'Value': values, 'Date': dates}
#     else:
#         raise KeyError(cfg.financial_data_error)


# def get_financial_table(xbrl_instance):
#     """formats and returns a pandas dataframe of finanical data contained within an XBRL file instance of accounts
#     information

#     Args:
#         xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
#         to be extracted

#     Returns:
#         pf (DataFrame): a pandas dataframe containing the finanical information split out by reporting period start
#         and end date
#     """
#     financial_dict = get_financial_facts(xbrl_instance)

#     df = pd.DataFrame(financial_dict)
#     mask = df[['Fact', 'Date']].duplicated(keep=False)
#     df.loc[mask, 'Fact'] += df.groupby(['Fact', 'Date']).cumcount().add(1).astype(str)

#     df = df.pivot(index='Fact', columns='Date', values='Value').reset_index()
#     df.index.name = None

#     return df


# def get_entity_address(xbrl_instance):
#     """extracts and returns the registered entity address from an XBRL file instance of accounts information

#     DEPRECIATEDTODO: closingly non-functional for accounts that have multiple addresses of differing lengths

#     Args:
#         xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which the entity address
#         needs to be extracted

#     Returns:
#         address_df (DataFrame): a pandas dataframe containing the entity address
#     """
#     address = {}
#     address_variables_flags = [
#         'AddressLine',
#         'PrincipalLocation',
#         'PostalCodeZip'
#     ]
#     for fact in xbrl_instance.facts:
#         if any(s in fact.concept.name for s in address_variables_flags):
#             if fact.concept.name in address:
#                 address[fact.concept.name].append(fact.value.strip())
#             else:
#                 address[fact.concept.name] = [fact.value.strip()]
#         else:
#             pass
#     address_df = pd.DataFrame(address)
#     return address_df


# def get_share_info(xbrl_instance):
#     """create list for any share data contained within the accounts.

#     DEPRECIATEDTODO:
#         closing extent and type of share information contained within accounts is unknown. At present, procedure is to
#         just return a list of any possible share information. Once full scope is understood, it will be presented in a
#         better format.

#     Args:
#         xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
#         to be extracted

#     Returns:
#         list: a list of all collated share information contained within an XBRL instance
#     """
#     share_info = []
#     for fact in xbrl_instance.facts:
#         if check_string_in_name('share', fact):
#             name = fact.concept.name
#             value = fact.value
#             unit = None
#             date = None
#             if check_instant_date(fact):
#                 date = fact.context.instant_date.isoformat()
#             if check_unit_gbp(fact):
#                 unit = '£'
#             share_info.append([name, unit, value, date])
#         elif check_name_is_string('equity', fact):
#             dimensions = return_dimension_values(fact)
#             if any(['share' in v.lower() for v in dimensions]):
#                 for v in dimensions:
#                     if 'share' in v.lower():
#                         name = fact.concept.name + v
#                         break
#                 value = fact.value
#                 unit = None
#                 date = None
#                 if check_instant_date(fact):
#                     date = fact.context.instant_date.isoformat()
#                 if check_unit_gbp(fact):
#                     unit = '£'
#                 share_info.append([name, unit, value, date])
#     return share_info


# def get_director_names(xbrl_instance):
#     """create dictionary of all directors named in an XBRL accounts instance

#     Args:
#         xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
#         to be extracted

#     Returns:
#         dict: a dictionary of the named directors listing their position and name
#     """
#     director_dict = {}
#     duplicate_director_idx = 0
#     for fact in xbrl_instance.facts:
#         if check_name_is_string('NameEntityOfficer', fact):
#             director_number = return_dimension_dict(fact)['EntityOfficersDimension']
#             director = fact.value.strip()
#             if (director_number not in director_dict) and (director not in director_dict.values()):
#                 director_dict[director_number] = director
#             elif (director_number not in director_dict) and (director in director_dict.values()):
#                 director_dict[director_number] = director
#                 _s = 'Same director holding multiple board positions.'
#                 logging.warning(_s)
#             elif (director_number in director_dict) and (director not in director_dict.values()):
#                 duplicate_director_idx += 1
#                 director_number = director_number + f'_{duplicate_director_idx}'
#                 director_dict[director_number] = director
#                 _s = 'Multiple directors holding same board position.'
#                 logging.warning(_s)
#             else:
#                 pass
#     return director_dict
