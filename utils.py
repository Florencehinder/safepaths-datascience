import csv
import json
import logging
import os
import re
import time

import urllib3

http = urllib3.PoolManager()

log_filename = f"logs/{('_'.join([str(t) for t in time.gmtime()[0:3]]))}.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)

def check_availability(url):
    response=http.request('GET', url)
    
    if response.status==500:
        raise ValueError('Connection failed.')

    return response

def check_data_type(url):

    response = check_availability(url)

    try:
        if re.search('.csv', url):
            temp = list(csv.DictReader(response.data.decode('utf-8').splitlines()))
        elif re.search('.json', url):
            temp = json.loads(response.data)
    except ValueError as e:
        with open(log_filename, 'a') as log:
            log.writelines(('-'.join([str(t) for t in time.gmtime()[3:6]]))+str(e))
            e
    return temp

def check_GPSdata(url):

    temp = check_data_type(url)
    
    relong = re.compile("long", re.IGNORECASE)
    relat = re.compile("lat", re.IGNORECASE)  

    if list(filter(relat.match, list(temp[0].keys()))) and list(filter(relong.match, list(temp[0].keys()))):
        print('GPS data found')
    else:
        raise ValueError('No GPS data found. \nColumn names are:', temp[0])

    return temp

def build_GPS_data(url, filename='gps_data.csv'):
    
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
