from utils import *

log_filename = f"logs/{('_'.join([str(t) for t in time.gmtime()[0:3]]))}.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)

with open('data_sources.json', 'r') as myfile:
    data=myfile.read()

sources = json.loads(data)
url = sources['Nations']['US']['National']['JHU CSSE']


if re.search('.csv', url):
    try:
        check_GPS_csv(url)
    except ValueError as e:
        with open(log_filename, 'a') as log:
            log.writelines(('-'.join([str(t) for t in time.gmtime()[3:6]]))+str(e))
            e

    build_GPS_data_csv(url)
