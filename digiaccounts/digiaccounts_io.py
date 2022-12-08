import json
import uuid
import logging
from datetime import datetime


from digiaccounts.digiaccounts_data import (
    get_company_registration,
    get_startend_period,
    get_company_postcodes,
    get_dormant_state,
    get_average_employees,
    get_financial_table
)


def get_account_information_dictionary(unique_id, xbrl_instance):

    account_information = {
        '_id': unique_id
    }

    try:
        account_information['registration_number'] = get_company_registration(xbrl_instance)
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
        account_information['post_codes'] = get_company_postcodes(xbrl_instance)
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
        account_information['financial_table'] = json.loads(
            get_financial_table(xbrl_instance).to_json(date_format='iso', index=False, orient='split')
        )
    except KeyError as _e:
        logging.warning(repr(_e))
        account_information['financial_table'] = None

    return account_information


def add_account_to_collection(accounts_collection, account_dictionary):

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
    name = filename.split('/')[-1].split('.')[0]
    registration, end_period = name.split('_')[2:4]
    end_period = format_end_period(end_period)
    return registration, end_period


def format_end_period(end_period):
    return datetime.strptime(end_period, "%Y%m%d").date().isoformat()


def get_uuid(registration, end_period):
    return uuid.uuid5(uuid.NAMESPACE_DNS, '_'.join((registration, end_period))).hex


def create_unique_id(filename):
    registration, end_period = get_file_registration_period_from_filename(filename)
    return get_uuid(registration, end_period)
