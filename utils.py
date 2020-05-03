import csv
import json
import logging
import logging.handlers
import os
import re
import time

import urllib3

http = urllib3.PoolManager()

log_filename = f"logs/{('_'.join([str(t) for t in time.gmtime()[0:3]]))}.log"
logging.basicConfig(filename=log_filename, 
                    filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.ERROR)


def check_availability(url):
    """ Checks status of connection, logging errors """

    response=http.request('GET', url)
    
    if response.status!=500: return response
    else:
        logging.error('Connection failed.') 
        raise ValueError(f'server response is {response.status}')
        
    
def check_data_type(url):

    """
    Checks if the url contains .csv and .json files. If yes, it parses them
    """

    response = check_availability(url)

    if re.search('.csv', url):
        temp = list(csv.DictReader(response.data.decode('utf-8').splitlines()))
    elif re.search('.json', url):
        temp = json.loads(response.data)
    else: 
        e = 'No data types recognized in URL'
        logging.error(e)
        raise ValueError(e)

    return temp
        
    

def check_GPSdata(url):

    """
    Checks if the data parsed by check_data_type() contain longitude and latitude. 
    If yes, it returns the data.
    """

    temp = check_data_type(url)
    
    relong = re.compile("long", re.IGNORECASE)
    relat = re.compile("lat", re.IGNORECASE)  

    if list(filter(relat.match, list(temp[0].keys()))) and list(filter(relong.match, list(temp[0].keys()))):
        print('GPS data found')
    else: 
        e = f'No GPS data found. \nColumn names are:{temp[0]}'
        logging.error(e)
        raise ValueError(e)
        
    return temp


def build_GPS_data(url, filename='gps_data.csv'):

    """
    Imports data parsed by check_data_type(), selects only longitude and latitude values
    and stores them in a csv files. It can recognize different namings for those two columns.
    Does not store time data.
    """
        
    with open(filename, "w", newline='') as result:
        writer = csv.DictWriter(result, ['latitude','longitude'])
        writer.writeheader()

        temp = check_data_type(url)

        for d in temp[:10]:      #limit to 10 rows for testing purpose
            for key in list(temp[0].keys()):
                filtered_d = dict((key, d[key]) for key in list(d.keys()) if re.search('lat|long', key, re.IGNORECASE))
                
                for old_k in list(filtered_d.keys()):
                    if re.search('long', old_k, re.IGNORECASE):
                        filtered_d['longitude'] = filtered_d.pop(old_k)
                    else: filtered_d['latitude'] = filtered_d.pop(old_k)
                
            writer.writerow(filtered_d)
