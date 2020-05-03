from utils import *

with open('data_sources.json', 'r') as myfile:
    data=myfile.read()

sources = json.loads(data)
url = sources['Nations']['Spain']['Catalonia']['requires API']['COVID-19 tests and results by date, sex, and basic health area']

build_GPS_data(url)
