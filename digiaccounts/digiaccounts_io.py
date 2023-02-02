"""functions to deploy the XBRL fact extraction functions from digiaccounts_data and place collected data into
documents"""

import uuid
import logging
from datetime import datetime


from digiaccounts.digiaccounts_data import (
    get_entity_registration,
    get_startend_period,
    get_entity_postcode,
    get_dormant_state,
    get_average_employees,
    get_entity_turnover,
    get_intangible_assets,
    get_investment_property,
    get_investment_assets,
    get_biological_assets,
    get_plant_equipment,
    get_entity_equity
)

from digiaccounts.digiaccounts_util import check_fact_value_string_none


def get_account_information_dictionary(unique_id, xbrl_instance):
    """use functions from digiaccouts_data to extract important facts from XBRL documents and return dictionary of
    results

    Args:
        unique_id (string): UDF to serve as unique ID for dictionary
        xbrl_instance (XbrlInstance): an XBRL instance containing accounts information from which financial data needs
        to be extracted

    Returns:
        dict: dictionary containing extracted fact values
    """

    account_information = {
        '_id': unique_id
    }

    try:
        account_information['registration_number'] = get_entity_registration(xbrl_instance)
    except KeyError as _e:
        logging.error(repr(_e))
        account_information['registration_number'] = None
        return account_information

    try:
        period_starting, period_ending = get_startend_period(xbrl_instance)
        account_information['period_ending'] = period_ending
        account_information['period_starting'] = period_starting
    except KeyError as _e:
        logging.error(repr(_e))
        account_information['period_ending'] = None
        return account_information

    try:
        account_information['post_codes'] = get_entity_postcode(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['post_codes'] = None

    try:
        account_information['is_dormant'] = get_dormant_state(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['is_dormant'] = None

    try:
        account_information['average_employees'] = get_average_employees(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['average_employees'] = None

    try:
        turnover_opening, turnover_closing = get_entity_turnover(xbrl_instance)
        account_information['turnover_opening'] = turnover_opening
        account_information['turnover_closing'] = turnover_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['turnover_opening'] = None
        account_information['turnover_closing'] = None

    try:
        intangible_opening, intangible_closing = get_intangible_assets(xbrl_instance)
        account_information['intangible_asset_value_opening'] = intangible_opening
        account_information['intangible_asset_value_closing'] = intangible_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['intabgible_asset_value_opening'] = None
        account_information['intangible_asset_value_closing'] = None

    try:
        investment_property_opening, investment_property_closing = get_investment_property(xbrl_instance)
        account_information['investment_property_value_opening'] = investment_property_opening
        account_information['investment_property_value_closing'] = investment_property_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['investment_property_value_opening'] = None
        account_information['investment_property_value_closing'] = None

    try:
        investment_asset_opening, investment_asset_closing = get_investment_assets(xbrl_instance)
        account_information['investment_asset_value_opening'] = investment_asset_opening
        account_information['investment_asset_value_closing'] = investment_asset_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['investment_asset_value_opening'] = None
        account_information['investment_asset_value_closing'] = None

    try:
        biological_asset_opening, biological_asset_closing = get_biological_assets(xbrl_instance)
        account_information['biological_asset_value_opening'] = biological_asset_opening
        account_information['biological_asset_value_closing'] = biological_asset_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['biological_asset_value_opening'] = None
        account_information['biological_asset_value_closing'] = None

    try:
        plant_equipment_opening, plant_equipment_closing = get_plant_equipment(xbrl_instance)
        account_information['plant_equipment_value_opening'] = plant_equipment_opening
        account_information['plant_equipment_value_closing'] = plant_equipment_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['plant_equipment_value_opening'] = None
        account_information['plant_equipment_value_closing'] = None

    try:
        tangible_list_opening = [
            account_information['investment_property_value_opening'],
            account_information['investment_asset_value_opening'],
            account_information['biological_asset_value_opening'],
            account_information['plant_equipment_value_opening']
        ]
        tangible_list_closing = [
            account_information['investment_property_value_closing'],
            account_information['investment_asset_value_closing'],
            account_information['biological_asset_value_closing'],
            account_information['plant_equipment_value_closing']
        ]
        account_information['tangible_asset_value_opening'] = sum(
            filter(check_fact_value_string_none, tangible_list_opening)
        )
        account_information['tangible_asset_value_closing'] = sum(
            filter(check_fact_value_string_none, tangible_list_closing)
        )
    except TypeError as _e:
        logging.warning(repr(_e))
        account_information['tangible_asset_value_opening'] = None
        account_information['tangible_asset_value_closing'] = None

    try:
        equity_opening, equity_closing = get_entity_equity(xbrl_instance)
        account_information['balance_opening'] = equity_opening
        account_information['balance_closing'] = equity_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['balance_opening'] = None
        account_information['balance_closing'] = None

    return account_information


def add_account_to_collection(accounts_collection, account_dictionary):
    """updates or creates a document in a mongoDB collection for a given set of accounts data

    Args:
        accounts_collection (_type_): MongoDB collection
        account_dictionary (_type_): dictionary containing data extracted from an annual accounts XBRL instance
    """

    unique_id = account_dictionary['_id']

    accounts_collection.update_one(
        filter={
            '_id': unique_id,
        },
        update={
            '$setOnInsert': account_dictionary | {'first_logged': datetime.now().isoformat()}
        },
        upsert=True,
    )


def get_file_registration_period_from_filename(filename):
    """extracts the entity registration number and end period date from CH archive file name

    Args:
        filename (str): CH archive file name

    Returns:
        tuple: registration number and end period extracted from the file name
    """
    name = filename.split('/')[-1].split('.')[0]
    registration, end_period = name.split('_')[2:4]
    end_period = format_end_period(end_period)
    return registration, end_period


def format_end_period(end_period):
    """converts CH archive end period date to iso format

    Args:
        end_period (str): _description_

    Returns:
        str: iso format date
    """
    return datetime.strptime(end_period, "%Y%m%d").date().isoformat()


def get_uuid(registration, end_period):
    """generates a UUID from a registration number and an iso formatted end period date

    Args:
        registration (str): CH entity registration number
        end_period (str): iso formatted end period date

    Returns:
        str: UUID in hexadecimal format
    """
    return uuid.uuid5(uuid.NAMESPACE_DNS, '_'.join((registration, end_period))).hex


def create_unique_id(filename):
    """generates a uuid from a CH archive annual accounts file name

    Args:
        filename (str): _description_

    Returns:
        str: uuid in hexadecimal format
    """
    registration, end_period = get_file_registration_period_from_filename(filename)
    return get_uuid(registration, end_period)
