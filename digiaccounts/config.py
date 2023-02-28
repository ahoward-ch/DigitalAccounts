"""Config module for digiaccounts package
"""

# Fact Names
FACT_NAME_START_DATE = 'StartDateForPeriodCoveredByReport'
FACT_NAME_END_DATE = 'EndDateForPeriodCoveredByReport'
FACT_NAME_POSTAL_CODE = 'PostalCodeZip'
FACT_NAME_DORMANT_STATE = ['EntityDormantTruefalse', 'EntityDormant']
FACT_NAME_ENTITY_REGISTRATION = 'UKCompaniesHouseRegisteredNumber'
FACT_NAME_ENTITY_NAME = 'EntityCurrentLegalOrRegisteredName'
FACT_NAME_ACCOUNTING_SOFTWARE = 'NameProductionSoftware'
FACT_NAME_AVERAGE_EMPLOYEES = 'AverageNumberEmployeesDuringPeriod'
FACT_NAME_TURNOVER = 'TurnoverRevenue'
FACT_NAME_INTANGIBLE_ASSETS = 'IntangibleAssets'
FACT_NAME_PLANT_EQUIPMENT = 'PropertyPlantEquipment'
FACT_NAME_INVESTMENT_ASSETS = 'InvestmentsFixedAssets'
FACT_NAME_INVESTMENT_PROPERTY = 'InvestmentProperty'
FACT_NAME_BIOLOGICAL_ASSETS = 'BiologicalAssets'
FACT_NAME_EQUITY = 'Equity'


# Fact Extra Dimension Keys
FACT_DIMENSION_PLANT_EQUIPMENT = 'PropertyPlantEquipmentClassesDimension'
FACT_DIMENSION_EQUITY = 'EquityClassesDimension'


# Mongo Keys
MONGO_KEY_START_DATE = 'period_opening_current'
MONGO_KEY_END_DATE = 'period_closing_current'
MONGO_KEY_POSTAL_CODE = 'registered_office_post_code'
MONGO_KEY_DORMANT_STATE = 'dormant_state'
MONGO_KEY_ENTITY_REGISTRATION = 'registration_number'
MONGO_KEY_ENTITY_NAME = 'registered_name'
MONGO_KEY_ACCOUNTING_SOFTWARE = 'accounting_software'
MONGO_KEY_AVERAGE_EMPLOYEES = 'average_employees'
MONGO_KEY_TURNOVER_CLOSING_CURRENT = 'turnover_value_closing_current'
MONGO_KEY_TURNOVER_CLOSING_PREVIOUS = 'turnover_value_closing_previous'
MONGO_KEY_INTANGIBLE_ASSETS_CLOSING_CURRENT = 'intangible_assets_value_closing_current'
MONGO_KEY_INTANGIBLE_ASSETS_CLOSING_PREVIOUS = 'intangible_assets_value_closing_previous'
MONGO_KEY_PLANT_EQUIPMENT_CLOSING_CURRENT = 'plant_equipment_value_closing_current'
MONGO_KEY_PLANT_EQUIPMENT_CLOSING_PREVIOUS = 'plant_equipment_value_closing_previous'
MONGO_KEY_INVESTMENT_ASSETS_CLOSING_CURRENT = 'investment_assets_value_closing_current'
MONGO_KEY_INVESTMENT_ASSETS_CLOSING_PREVIOUS = 'investment_assets_value_closing_previous'
MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_CURRENT = 'investment_property_value_closing_current'
MONGO_KEY_INVESTMENT_PROPERTY_CLOSING_PREVIOUS = 'investment_property_value_closing_previous'
MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_CURRENT = 'biological_assets_value_closing_current'
MONGO_KEY_BIOLOGICAL_ASSETS_CLOSING_PREVIOUS = 'biological_assets_value_closing_previous'
MONGO_KEY_TANGIBLE_ASSETS_CLOSING_CURRENT = 'tangible_assets_value_closing_current'
MONGO_KEY_TANGIBLE_ASSETS_CLOSING_PREVIOUS = 'tangible_assets_value_closing_previous'
MONGO_KEY_EQUITY_CLOSING_CURRENT = 'balance_value_closing_current'
MONGO_KEY_EQUITY_CLOSING_PREVIOUS = 'balance_value_closing_previous'


# Error Config


def fact_name_error(error_key):
    """_summary_

    Args:
        error_key (str): string defining missing fact name

    Returns:
        str: string containing error message for missing fact name
    """
    return f"No fact with concept name '{error_key}'."


def start_end_error(start_key, end_key):
    return ' '.join(
        (
            fact_name_error(start_key),
            fact_name_error(end_key)
        )
    )


def financial_data_error():
    return "No facts with single dates or units of 'iso4217:GBP'."


def dormant_state_error():
    return "No facts relating to dormancy present."
