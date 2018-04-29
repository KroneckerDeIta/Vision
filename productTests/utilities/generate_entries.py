import random

from . import country_codes


####################################################################################################
def generate_number_of_entries(number):
    """ Generates number of entries.

    Args:
        number: The number of entries.
    """
    entries = []
    for index in range(number):
        country = random.choice(country_codes.COUNTRY_CODES)
        country_code_lower = country["Code"].lower()

        next_entry = {"id": str(index), "type": "entries", "attributes": {}}
        next_entry["attributes"]["country"] = country["Name"]
        next_entry["attributes"]["icon"] = country_code_lower
        next_entry["attributes"]["image"] = "/images/flags/flags_iso/128/"+country_code_lower+".png"
        next_entry["attributes"]["telephone"] = str(index)
        next_entry["attributes"]["link"] = ""
        next_entry["attributes"]["order"] = index

        entries.append(next_entry)

    return entries
