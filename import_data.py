from utils import *

with open('data_sources.json', 'r') as myfile:
    data=myfile.read()

sources = json.loads(data)
url = sources['Nations']['Italy']['Regions']['Department of Civil Protection']


build_GPS_data(url)
