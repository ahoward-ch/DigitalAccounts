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
