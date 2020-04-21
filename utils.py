import csv
import json
import logging
import os
import re
import time

import urllib3

http = urllib3.PoolManager()

def check_GPS_csv(url):
    
    response=http.request('GET', url)
    
    if response.status==500:
        raise ValueError('Connection failed.')
    
    relong = re.compile("long", re.IGNORECASE)
    relat = re.compile("lat", re.IGNORECASE)
    
    temp = list(csv.DictReader(response.data.decode('utf-8').splitlines()))
    
    if list(filter(relat.match, list(temp[0].keys()))) and list(filter(relong.match, list(temp[0].keys()))):
        print('GPS data found')
    else:
        raise ValueError('No GPS data found. \nColumn names are:', temp[0])


def build_GPS_data_csv(url, filename='gps_data.csv'):
    with open(filename, "w", newline='') as result:
        writer = csv.DictWriter(result, ['latitude','longitude'])

        response = http.request('GET', url)
        temp = list(csv.DictReader(response.data.decode('utf-8').splitlines()))

        for d in temp[:10]:      #limit to 10 rows for testing purpose
            for key in list(temp[0].keys()):
                filtered_d = dict((key, d[key]) for key in list(d.keys()) if re.search('lat|long', key, re.IGNORECASE))
                
                for old_k in list(filtered_d.keys()):
                    if re.search('long', old_k, re.IGNORECASE):
                        filtered_d['longitude'] = filtered_d.pop(old_k)
                    else: filtered_d['latitude'] = filtered_d.pop(old_k)

            writer.writerow(filtered_d)
