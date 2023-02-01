"""Config module for digiaccounts package
"""

# Fact Names
FACT_NAME_START_DATE = 'StartDateForPeriodCoveredByReport'
FACT_NAME_END_DATE = 'EndDateForPeriodCoveredByReport'
FACT_NAME_POSTAL_CODE = 'PostalCodeZip'
FACT_NAME_DORMANT_STATE = ['EntityDormantTruefalse', 'EntityDormant']
FACT_NAME_COMPANY_REGISTRATION = 'UKCompaniesHouseRegisteredNumber'
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