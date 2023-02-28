"""functions to deploy the XBRL fact extraction functions from digiaccounts_data and place collected data into
documents"""

import uuid
import logging
from datetime import datetime
import dateutil.parser
import oracledb
import pymongo


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
    get_entity_equity,
    get_accounting_software,
    get_entity_registered_name
)

from digiaccounts.digiaccounts_util import check_fact_value_string_none, return_data_link_credentials
from digiaccounts import config as cfg


def get_account_information_dictionary(unique_id: str, filing_date: datetime.date or str, xbrl_instance):
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

    if isinstance(filing_date, datetime):
        account_information['filing_date'] = filing_date
    elif isinstance(filing_date, str):
        account_information['filing_date'] = dateutil.parser.parse(filing_date)
    else:
        pass

    try:
        account_information[cfg.MONGO_KEY_ENTITY_REGISTRATION] = get_entity_registration(xbrl_instance)
    except KeyError as _e:
        logging.error(repr(_e))
        account_information[cfg.MONGO_KEY_ENTITY_REGISTRATION] = None
        return account_information

    try:
        period_starting, period_ending = get_startend_period(xbrl_instance)
        account_information[cfg.MONGO_KEY_END_DATE] = period_ending
        account_information[cfg.MONGO_KEY_START_DATE] = period_starting
    except KeyError as _e:
        logging.error(repr(_e))
        account_information[cfg.MONGO_KEY_END_DATE] = None
        return account_information

    try:
        account_information[cfg.MONGO_KEY_POSTAL_CODE] = get_entity_postcode(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_POSTAL_CODE] = None

    try:
        account_information[cfg.MONGO_KEY_DORMANT_STATE] = get_dormant_state(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_DORMANT_STATE] = None

    try:
        account_information[cfg.MONGO_KEY_AVERAGE_EMPLOYEES] = get_average_employees(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_AVERAGE_EMPLOYEES] = None

    try:
        turnover_opening, turnover_closing = get_entity_turnover(xbrl_instance)
        account_information[cfg.MONGO_KEY_TURNOVER_CLOSING_PREVIOUS] = turnover_opening
        account_information[cfg.MONGO_KEY_TURNOVER_CLOSING_CURRENT] = turnover_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_TURNOVER_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_TURNOVER_CLOSING_CURRENT] = None

    try:
        intangible_opening, intangible_closing = get_intangible_assets(xbrl_instance)
        account_information[cfg.MONGO_KEY_INTANGIBLE_ASSETS_CLOSING_PREVIOUS] = intangible_opening
        account_information[cfg.MONGO_KEY_INTANGIBLE_ASSETS_CLOSING_CURRENT] = intangible_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_INTANGIBLE_ASSETS_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_INTANGIBLE_ASSETS_CLOSING_CURRENT] = None

    try:
        investment_property_opening, investment_property_closing = get_investment_property(xbrl_instance)
        account_information[cfg.MONGO_KEY_INVESTMENT_ASSETS_CLOSING_PREVIOUS] = investment_property_opening
        account_information[cfg.MONGO_KEY_INVESTMENT_ASSETS_CLOSING_CURRENT] = investment_property_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_INVESTMENT_ASSETS_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_INVESTMENT_ASSETS_CLOSING_CURRENT] = None

    try:
        investment_asset_opening, investment_asset_closing = get_investment_assets(xbrl_instance)
        account_information[cfg.MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_PREVIOUS] = investment_asset_opening
        account_information[cfg.MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_CURRENT] = investment_asset_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_CURRENT] = None

    try:
        biological_asset_opening, biological_asset_closing = get_biological_assets(xbrl_instance)
        account_information[cfg.MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_PREVIOUS] = biological_asset_opening
        account_information[cfg.MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_CURRENT] = biological_asset_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_CURRENT] = None

    try:
        plant_equipment_opening, plant_equipment_closing = get_plant_equipment(xbrl_instance)
        account_information[cfg.MONGO_KEY_PLANT_EQUIPMENT_CLOSING_PREVIOUS] = plant_equipment_opening
        account_information[cfg.MONGO_KEY_PLANT_EQUIPMENT_CLOSING_CURRENT] = plant_equipment_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_PLANT_EQUIPMENT_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_PLANT_EQUIPMENT_CLOSING_CURRENT] = None

    try:
        tangible_list_opening = [
            account_information[cfg.MONGO_KEY_INVESTMENT_ASSETS_CLOSING_PREVIOUS],
            account_information[cfg.MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_PREVIOUS],
            account_information[cfg.MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_PREVIOUS],
            account_information[cfg.MONGO_KEY_PLANT_EQUIPMENT_CLOSING_PREVIOUS]
        ]
        tangible_list_closing = [
            account_information[cfg.MONGO_KEY_INVESTMENT_ASSETS_CLOSING_CURRENT],
            account_information[cfg.MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_CURRENT],
            account_information[cfg.MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_CURRENT],
            account_information[cfg.MONGO_KEY_PLANT_EQUIPMENT_CLOSING_CURRENT]
        ]
        account_information[cfg.MONGO_KEY_TANGIBLE_ASSETS_CLOSING_PREVIOUS] = sum(
            filter(check_fact_value_string_none, tangible_list_opening)
        )
        account_information[cfg.MONGO_KEY_TANGIBLE_ASSETS_CLOSING_CURRENT] = sum(
            filter(check_fact_value_string_none, tangible_list_closing)
        )
    except TypeError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_TANGIBLE_ASSETS_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_TANGIBLE_ASSETS_CLOSING_CURRENT] = None

    try:
        equity_opening, equity_closing = get_entity_equity(xbrl_instance)
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_PREVIOUS] = equity_opening
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_CURRENT] = equity_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_CURRENT] = None

    try:
        software = get_accounting_software(xbrl_instance)
        account_information[cfg.MONGO_KEY_ACCOUNTING_SOFTWARE] = software
    except KeyError:
        account_information[cfg.MONGO_KEY_ACCOUNTING_SOFTWARE] = None

    try:
        name = get_entity_registered_name(xbrl_instance)
        account_information[cfg.MONGO_KEY_ENTITY_NAME] = name
    except KeyError:
        account_information[cfg.MONGO_KEY_ENTITY_NAME] = None

    return account_information


def get_account_information_dictionary_validation(unique_id: str, xbrl_instance):
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
        account_information[cfg.MONGO_KEY_ENTITY_REGISTRATION] = get_entity_registration(xbrl_instance)
    except KeyError as _e:
        logging.error(repr(_e))
        account_information[cfg.MONGO_KEY_ENTITY_REGISTRATION] = None
        return account_information

    try:
        period_starting, period_ending = get_startend_period(xbrl_instance)
        account_information[cfg.MONGO_KEY_END_DATE] = period_ending
        account_information[cfg.MONGO_KEY_START_DATE] = period_starting
    except KeyError as _e:
        logging.error(repr(_e))
        account_information[cfg.MONGO_KEY_END_DATE] = None
        return account_information

    try:
        account_information[cfg.MONGO_KEY_POSTAL_CODE] = get_entity_postcode(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_POSTAL_CODE] = None

    try:
        account_information[cfg.MONGO_KEY_DORMANT_STATE] = get_dormant_state(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_DORMANT_STATE] = None

    try:
        account_information[cfg.MONGO_KEY_AVERAGE_EMPLOYEES] = get_average_employees(xbrl_instance)
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_AVERAGE_EMPLOYEES] = None

    try:
        equity_opening, equity_closing = get_entity_equity(xbrl_instance)
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_PREVIOUS] = equity_opening
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_CURRENT] = equity_closing
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_PREVIOUS] = None
        account_information[cfg.MONGO_KEY_EQUITY_CLOSING_CURRENT] = None

    try:
        software = get_accounting_software(xbrl_instance)
        account_information[cfg.MONGO_KEY_ACCOUNTING_SOFTWARE] = software
    except KeyError:
        account_information[cfg.MONGO_KEY_ACCOUNTING_SOFTWARE] = None

    try:
        name = get_entity_registered_name(xbrl_instance)
        account_information[cfg.MONGO_KEY_ENTITY_NAME] = name
    except KeyError:
        account_information[cfg.MONGO_KEY_ENTITY_NAME] = None

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
            '$setOnInsert': account_dictionary | {'first_logged': datetime.now()}
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


def get_uuid(registration, filing_date):
    """generates a UUID from a registration number and an iso formatted end period date

    Args:
        registration (str): CH entity registration number
        end_period (str): iso formatted end period date

    Returns:
        str: UUID in hexadecimal format
    """
    return uuid.uuid5(uuid.NAMESPACE_DNS, '_'.join((registration, filing_date))).hex


def create_unique_id(filename):
    """generates a uuid from a CH archive annual accounts file name

    Args:
        filename (str): _description_

    Returns:
        str: uuid in hexadecimal format
    """
    registration, end_period = get_file_registration_period_from_filename(filename)
    return get_uuid(registration, end_period)


def return_data_source_connection():
    credentials = return_data_link_credentials('DataSource')
    username = credentials.get('username')
    password = credentials.get('password')
    host = credentials.get('host')
    port = credentials.getint('port')
    protocol = credentials.get('protocol')
    name = credentials.get('name')

    params = oracledb.ConnectParams(host=host, port=port, protocol=protocol, service_name=name)
    return oracledb.connect(user=username, password=password, params=params)


def return_data_target_connection():
    credentials = return_data_link_credentials('DataTargetAdmin')
    username = credentials.get('username')
    password = credentials.get('password')
    _s = f'mongodb+srv://{username}:{password}@cluster0-pl-0.u1nnh.mongodb.net/test?authSource=admin&replicaSet=atlas-mh1x8w-shard-0&readPreference=primary'

    return pymongo.MongoClient(_s)
