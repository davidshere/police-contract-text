STATE_CITY_MAP = {
    "New Mexico": ['Albuquerque'],
    "California": ['Anaheim', 'Bakersfield', 'Chula Vista', 'Fremont', 'Fresno', 'Glendale', 'Irvine', 'Long Beach', 'Los Angeles', 'Oakland', 'Riverside', 'Sacramento', 'San Diego', 'San Francisco', 'San Jose', 'Santa Ana', 'Stockton'],
    "Alaska": ['Anchorage'],
    "Colorado": ['Aurora', "Denver"],
    "Texas": ['Austin', 'Corpus Christi', 'Dallas', 'El Paso', 'Fort Worth', 'Houston', 'Laredo', 'San Antonio'], 
    "Maryland": ['Baltimore'],
    "Louisiana": ['Baton Rouge'],
    "Massachusetts": ['Boston'],
    "New York": ['Buffalo', 'New York', 'Rochester'],
    "Arizona": ['Chandler', 'Phoenix', "Tucson"],
    "Illinois": ['Chicago'],
    "Michigan": ['Detroit'],
    "Indiana": ["Fort Wayne", "Indianapolis"],
    "Ohio": ['Cincinnati', 'Cleveland', 'Columbus'],
    "Nevada": ['Henderson', 'Las Vegas Metropolitan', 'North Las Vegas', 'Reno'],
    "Florid": ['Hialeah', 'Jacksonville', 'Miami', 'Orlando', 'St. Petersburg', 'Tampa'],
    "New Jersey": ['Jersey City', 'Newark'],
    "Nebraska": ['Lincoln', 'Omaha'], 
    "Kentucky": ['Louisville'],
    "Wisconsin": ['Madison', 'Milwaukee'],
    "Tennessee": ['Memphis', 'Metropolitan Nashville'],
    "Minnesota": ["Minneapolis", "St. Paul"],
    "Oklahoma": ['Oklahoma City', "Tulsa"],
    "Pennsylvania": ['Philadelphia', 'Pittsburgh'],
    "Oregon": ['Portland'],
    "Washington": ['Seattle', 'Spokane'],
    "Missouri": ['St. Louis Metropolitan'],
    "Washington, DC": ["Washington DC Metropolitan"],
    "Kansas": ['Wichita'],
}


def camelcase_name(name: str) -> str:
    return name.lower().replace('. ', '_').replace(" ", '_').replace('.', '')


CITY_TO_STATE_MAP = dict()
for state in STATE_CITY_MAP:
    for city in STATE_CITY_MAP[state]:
        CITY_TO_STATE_MAP[camelcase_name(city)] = state
