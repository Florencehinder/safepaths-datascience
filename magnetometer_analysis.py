import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
import math
import datetime
import os
import pathlib
from scipy.spatial.distance import pdist

## Setting home folder paths
home = os.getcwd()
data_folder = pathlib.Path(home, 'magnetometer_data')

## Parsing data generated elsewhere
phone1 = pd.read_json(data_folder/'mgm_a.json')
phone2 = pd.read_json(data_folder/'mgm_b.json')

## Rounding up timestamps at 1'. Averaging coordinates at 1' (reduce noise)
phone1['timestamp'] = phone1['timestamp'].dt.round('min')
phone2['timestamp'] = phone2['timestamp'].dt.round('min')

a = phone1.set_index('timestamp').rolling('1min').mean()#.assign(device=1).head()
b = phone2.set_index('timestamp').rolling('1min').mean()#.assign(device=2).head()


## Merge the two phones
df = a.merge(b, on='timestamp', how='outer', suffixes=('_a','_b')).sort_index()

## Apply euclidian distance
def distance_3d(row, metric='euclidean'):
    """
    Calculates the 3d distance rowwise in a dataframe. 
    Requires a dataframe with coordinates for point a (first 3 columns of the dataframe)
    and point b (second 3 columns of the dataframe).
    Metric can be changed (refer to scipy.spatial.distance.pdist). Euclidean is default.
    """

    if row.shape[0]<6:
        raise TypeError('Dataframe must have 3 columns of coordinates for each point')
    elif row.dtype !='float64':
        raise TypeError('Coordinates columns must be numeric')

    dist = pdist([row[0:3].values, row[3:6].values], metric=metric)

    return(dist[0])

df['distance a_b'] = df.apply(distance_3d, axis=1)
df['time_elapsed'] = pd.TimedeltaIndex(df.index - df.index[0], unit='m') / np.timedelta64(1, 'm')

df.plot(kind='scatter',x='time_elapsed',y='distance a_b',color='red')
df.to_csv('test_dist.csv')