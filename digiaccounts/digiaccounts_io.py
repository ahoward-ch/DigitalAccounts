"""functions to deploy the XBRL fact extraction functions from digiaccounts_data and place collected data into
documents"""

import re
import uuid
import logging
from io import StringIO
from pathlib import Path
from typing import List
from datetime import datetime
import xml.etree.ElementTree as ET
import dateutil.parser
import oracledb
import pymongo
from xbrl import InstanceParseException
from xbrl.cache import HttpCache
from xbrl.helper.uri_helper import resolve_uri
from xbrl.helper.xml_parser import parse_file
from xbrl.taxonomy import Concept, TaxonomySchema, parse_taxonomy, parse_taxonomy_url
from xbrl.instance import (
    LINK_NS,
    XLINK_NS,
    NAME_SPACES,
    AbstractContext,
    AbstractFact,
    AbstractUnit,
    NumericFact,
    TextFact,
    XbrlInstance,
    XbrlParser,
    _extract_non_fraction_value,
    _extract_non_numeric_value,
    _load_common_taxonomy,
    _parse_context_elements,
    _parse_unit_elements,
    _update_ns_map
)

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


class XbrlParserDA(XbrlParser):

    def parse_string_instance(self, string_instance: str) -> XbrlInstance:
        return parse_ixbrl_string(string_instance, self.cache)


def parse_ixbrl_string(string_instance: str, cache: HttpCache, schema_root=None) -> XbrlInstance:
    """
    Parses a inline XBRL (iXBRL) instance file.

    :param string_instance: string in memory containing contents of iXBRL instance
    :param cache: HttpCache instance
    :param schema_root: path to the directory where the taxonomy schema is stored (Only works for relative imports)
    :return: parsed XbrlInstance object containing all facts with additional information
    """

    contents = string_instance
    pattern = r'<[ ]*script.*?\/[ ]*script[ ]*>'
    contents = re.sub(pattern, '', contents, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

    root: ET.ElementTree = parse_file(StringIO(contents))
    ns_map: dict = root.getroot().attrib['ns_map']
    # get the link to the taxonomy schema and parse it
    schema_ref: ET.Element = root.find(f'.//{LINK_NS}schemaRef')
    schema_uri: str = schema_ref.attrib[XLINK_NS + 'href']
    # check if the schema uri is relative or absolute
    # submissions from SEC normally have their own schema files, whereas submissions from the uk have absolute schemas
    if schema_uri.startswith('http'):
        # fetch the taxonomy extension schema from remote
        taxonomy: TaxonomySchema = parse_taxonomy_url(schema_uri, cache)
    elif schema_root:
        # take the given schema_root path as directory for searching for the taxonomy schema
        schema_path = str(next(Path(schema_root).glob(f'**/{schema_uri}')))
        taxonomy: TaxonomySchema = parse_taxonomy(schema_path, cache)
    else:
        # try to find the taxonomy extension schema file locally because no full url can be constructed
        schema_path = resolve_uri(string_instance, schema_uri)
        taxonomy: TaxonomySchema = parse_taxonomy(schema_path, cache)

    # get all contexts and units
    xbrl_resources: ET.Element = root.find('.//ix:resources', ns_map)
    if xbrl_resources is None:
        raise InstanceParseException('Could not find xbrl resources in file')
    # parse contexts and units
    context_dir = _parse_context_elements(xbrl_resources.findall('xbrli:context', NAME_SPACES), ns_map, taxonomy, cache)
    unit_dir = _parse_unit_elements(xbrl_resources.findall('xbrli:unit', NAME_SPACES))

    # parse facts
    facts: List[AbstractFact] = []
    fact_elements: List[ET.Element] = root.findall('.//ix:nonFraction', ns_map) + root.findall('.//ix:nonNumeric',
                                                                                               ns_map)
    for fact_elem in fact_elements:
        # update the prefix map (sometimes the xmlns is defined at XML-Element level and not at the root element)
        _update_ns_map(ns_map, fact_elem.attrib['ns_map'])
        taxonomy_prefix, concept_name = fact_elem.attrib['name'].split(':')

        tax = taxonomy.get_taxonomy(ns_map[taxonomy_prefix])
        if tax is None:
            tax = _load_common_taxonomy(cache, ns_map[taxonomy_prefix], taxonomy)

        xml_id: str or None = fact_elem.attrib['id'] if 'id' in fact_elem.attrib else None

        concept: Concept = tax.concepts[tax.name_id_map[concept_name]]
        context: AbstractContext = context_dir[fact_elem.attrib['contextRef'].strip()]
        # ixbrl values are not normalized! They are formatted (i.e. 123,000,000)

        if fact_elem.tag == '{' + ns_map['ix'] + '}nonFraction':
            fact_value: float or None = _extract_non_fraction_value(fact_elem)

            unit: AbstractUnit = unit_dir[fact_elem.attrib['unitRef'].strip()]
            decimals_text: str = str(fact_elem.attrib['decimals']).strip() if 'decimals' in fact_elem.attrib else '0'
            decimals: int = None if decimals_text.lower() == 'inf' else int(decimals_text)

            facts.append(NumericFact(concept, context, fact_value, unit, decimals, xml_id))
        elif fact_elem.tag == '{' + ns_map['ix'] + '}nonNumeric':
            fact_value: str = _extract_non_numeric_value(fact_elem)
            facts.append(TextFact(concept, context, str(fact_value), xml_id))

    return XbrlInstance(string_instance, taxonomy, facts, context_dir, unit_dir)


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
