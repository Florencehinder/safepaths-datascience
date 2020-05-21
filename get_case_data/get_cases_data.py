import datetime # add date to filename; progress bar time estimate
import time # progress bar time estimate
import sys # progress bar
import argparse
import textwrap
import numpy as np
import csv
import requests # get HTML data from url
from bs4 import BeautifulSoup # get data from HTML
from uszipcode import SearchEngine # get lat-long from city,state

class case_batch:
    """
    Holds the number of cases for each city,state.
    """
    def __init__(self, city, state, num_cases):
        # string, string, int
        self.city = city
        self.state = state
        self.num_cases = num_cases

    def __repr__(self):
        return "{},{},{}".format(str(self.lat), str(self.lng), str(self.num_cases))

    def __str__(self):
        return "{},{},{}".format(str(self.lat), str(self.lng), str(self.num_cases))

    def print_one(self):
        return "{},{},1".format(str(self.lat), str(self.lng))

    def set_latlng(self, lat, lng):
        # float, float
        self.lat = lat
        self.lng = lng

    def set_ID(self, ID):
        # string
        self.ID = ID
    
def add_latlong(search, lc):
    """ 
    Get lat, lng data from zipcode.

    @param:
        search (uszipcode SearchEngine)
        lc (case_batch object)

    @return:
        lc (case_batch objet with lat,lng values)
            if found, else None
    """
    data_search = search.by_city_and_state(lc.city, lc.state)
    if len(data_search) > 0:
        data = data_search[0]
        lc.set_latlng(data.lat, data.lng)
        return lc
    else:
        return None
    

def get_cases_from_url(state, table_num, th, url, search):
    """
    Get BeautifulSoup HTML from url and extract HTML table table_num.
    Get the number of cases for each location (county, state) by getting
    the values from the table heading th.

    @params:
        url (string)
        table_num (int)
        th (string): name of table heading w/ num. of cases
        state (two letter string)
        search (uszipcode SearchEngine)

    @return:
        A list of case_batch objects.
    """
    # using parser other than "lxml" may have different results
    r = requests.get(url)
    soup_html = BeautifulSoup(r.content, "lxml")

    # get table table_num
    html_cases_table = soup_html.find_all("table")[table_num - 1]

    # is the heading tag <th> or <td>
    th_tag = "th"
    if len(soup_html.find_all("th"))==0:
        th_tag = "td"

    # convert html html_cases_table to list of sets
    headings = [th.get_text().strip() for th in html_cases_table.find("tr").find_all(th_tag)]
    datasets = [] 
    # skip header row
    for row in html_cases_table.find_all("tr")[1:]: 
        dataset = dict(zip(headings, (td.get_text() for td in row.find_all("td")))) 
        datasets.append(dataset) 

    # make list of case_batch objects
    cases_by_county = []
    for row in datasets:
        # string.strip() to remove any extra spaces
        county_cases = case_batch(row["County"].strip(), state, int(row[th].strip()))
        county_cases = add_latlong(search, county_cases)
        if county_cases is not None:
            cases_by_county.append(county_cases)

    return cases_by_county

def print_progress(current_step, total_steps, start):
    """ print progress bar """
    size = 50
    bar = "#" * int(size * (current_step/total_steps))
    time_passed = time.time() - start
    time_left = time_passed * (1 - current_step/total_steps)
    progress = "    ({}%) [{}/{}]".format(int(current_step * 100/total_steps), 
        datetime.timedelta(seconds=time_passed),
        datetime.timedelta(seconds=time_left))
    sys.stdout.write(bar + progress)
    sys.stdout.flush()
    sys.stdout.write("]\n")

def get_data(state_md, state, search):
    """
    Return data.

    @param:
        state (USPS abbrev.; e.g. MA, NY)
        search (uszipcode SearchEngine)
    
    @return:
        list of case_batch objects
    """
    print("Getting data from state {}...\n".format(state))

    # Get data from 4th table on PA website (table with num. of total cases)
    # get_cases_from_url(state, table_num, th, url)
    return get_cases_from_url(state, state_md["tnum"], state_md["th"], state_md["url"], search)

def init():
    """ main function """

    print("Starting...\n")    

    # maps state to metadata (url, table #, table header from which to extract number of cases)
    us_states_md = {"PA": {"url":"https://www.health.pa.gov/topics/disease/coronavirus/Pages/Cases.aspx",
        "th":"Total Cases", "tnum":4}, "MI": {"url": "https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html",
        "th":"Confirmed Cases", "tnum": 1}}

    print("Getting data...\n")
    
    # start uszipcode SearchEngine
    # use rich info zipcode database
    search = SearchEngine(simple_zipcode=False)

    # get user args
    parser = argparse.ArgumentParser(
        prog="python get_cases_data.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Function: Get the latitude,longitude,num_cases data for the given
            US state (or, if no state is specified, all states that have been
            configured. Data will be saved to a .CSV file (see examples below 
            for format).'''),
        epilog=textwrap.dedent('''
            Example (batched) file:
                LAT,LNG,NUM_CASES
                40.3,-79.65,197
                39.87,-75.43,58
                40.68,-80.37,539
                39.9,-78.6,83
                40.2,-77.8,204
                ...

            Example (unbatched) file: 
                LAT,LNG,NUM_CASES
                39.9,-78.6,1
                39.9,-78.6,1
                39.9,-78.6,1
                ...
                40.2,-77.8,1
                ...'''))

    parser.add_argument('-s', type=str, default="ALL", help="USPS state name (e.g. PA). If no state is given, all states will be outputted to the file us-cases_[date].csv")
    parser.add_argument('-o', type=str, default="state-cases_date.csv", help="Output filename (default is [state]-cases_[date].csv")
    parser.add_argument('--batch-data', dest='batchdata', action='store_true', 
        help="Print cases in batches for each coordinate (lat,lng,N). Default is to print cases to file unbatched (lat,lng,1) for each of the N cases at that lat-lng coordinate.")
    parser.set_defaults(batchdata=False)

    args = parser.parse_args()
    
    output_fn = args.o
    state = args.s
    batch_data = args.batchdata
    data = []

    # get data
    if state=="ALL":
        output_fn = "us-cases_" + str(datetime.date.today()) + ".csv"
        for state in us_states_md.keys():
            data = np.append(data, get_data(us_states_md[state], state, search))
    elif state in us_states_md.keys():
        output_fn = state + "-cases_" + str(datetime.date.today()) + ".csv"
        data = np.append(data, get_data(us_states_md[state], state, search))
    else:
        print("This state is not configured.")
        return

    print("Saving data...\n")

    # save data to csv
    with open(output_fn, 'w') as f:
        header = "LAT,LONG,NUM_CASES\n"
        f.write(header)
        for i,datapoint in enumerate(data):
            if batch_data:
                f.write(datapoint.print())
                f.write("\n")
            else:
                for case in range(datapoint.num_cases):
                    f.write(datapoint.print_one())
                    f.write("\n")

if __name__== "__main__":
    init()
