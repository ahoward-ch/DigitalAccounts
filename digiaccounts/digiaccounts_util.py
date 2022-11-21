"""utility functions for checking XBRL Fact contents"""


def check_unit_gbp(fact):
    """returns boolean check if a fact contains a GBP unit

    Args:
        fact (xbrl.instance.<fact>): single fact object from XbrlInstance

    Returns:
        bool: True if fact has unit GBP
    """
    if hasattr(fact, 'unit') and (fact.unit.unit == 'iso4217:GBP'):
        return True
    else:
        return False


def check_instant_date(fact):
    """returns boolean check if a fact contains a an instant date attribute

    Args:
        fact (xbrl.instance.<fact>): single fact object from XbrlInstance

    Returns:
        bool: True if fact has .context.instant_date
    """
    if hasattr(fact.context, 'instant_date'):
        return True
    else:
        return False


def check_string_in_name(string, fact):
    """returns boolean check if a fact name contains a string

    Args:
        string (str): a string which might be part of a fact name
        fact (xbrl.instance.<fact>): single fact object from XbrlInstance

    Returns:
        bool: True if string is in the fact name
    """
    if string.lower() in fact.concept.name.lower():
        return True
    else:
        return False


def check_name_is_string(string, fact):
    """returns boolean check if a fact name matches a string

    Args:
        string (str): a string which might match a fact name
        fact (xbrl.instance.<fact>): single fact object from XbrlInstance

    Returns:
        bool: True if fact has identical name to string
    """
    if fact.concept.name.lower() == string.lower():
        return True
    else:
        return False


def return_dimension_dict(fact):
    """returns dictionary derived from a fact dimension attribute

    Args:
        fact (xbrl.instance.<fact>): single fact object from XbrlInstance

    Returns:
        dict: fact dimension dictionary
    """
    return fact.json()['dimensions']


def return_dimension_values(fact):
    """returns list containing values from a fact dimension attribute dictionary

    Args:
        fact (xbrl.instance.<fact>): single fact object from XbrlInstance

    Returns:
        list: values from fact dimension attribute dictonary
    """
    return fact.json()['dimensions'].values()
