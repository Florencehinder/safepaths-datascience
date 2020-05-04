import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

def get_distance(ts):    
    #if outside the test window, return None
    if ts < datetime.datetime(2020, 5, 2, 10, 54, 30):
        return 150
    if ts < datetime.datetime(2020, 5, 2, 10, 56, 25):
        return 126
    if ts < datetime.datetime(2020, 5, 2, 10, 58, 25):
        return 80
    if ts < datetime.datetime(2020, 5, 2, 11, 0, 24):
        return 51
    if ts < datetime.datetime(2020, 5, 2, 11, 2, 21):
        return 22
    if ts < datetime.datetime(2020, 5, 2, 11, 4, 22):        
        return 9
    if ts < datetime.datetime(2020, 5, 2, 11, 6, 28):
        return 0 
   
    if ts < datetime.datetime(2020, 5, 2, 11, 14, 0):
        return 138 + 182
    if ts < datetime.datetime(2020, 5, 2, 11, 17, 20):
        return 138 + 161
    if ts < datetime.datetime(2020, 5, 2, 11, 19, 0):
        return 138 + 126
    if ts < datetime.datetime(2020, 5, 2, 11, 21, 0):
        return 138 + 61
    if ts < datetime.datetime(2020, 5, 2, 11, 26, 35):
        return 138 + 61
      

_dcoll = []
for index,row in phone2.iterrows():
    _d = get_distance(row['timestamp'])
    _dcoll.append(_d)
phone2['truth'] = _dcoll


a = phone1.set_index('timestamp').rolling('1min').mean()#.assign(device=1).head()
b = phone2.set_index('timestamp').rolling('1min').mean()#.assign(device=2).head()


## Merge the two phones
df = a.merge(b, on='timestamp', how='outer', suffixes=('_a','_b')).sort_index()
df['time_elapsed'] = pd.TimedeltaIndex(df.index - df.index[0], unit='m') / np.timedelta64(1, 'm')
df.head()


## Apply distances
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

metrics = ['braycurtis', 'canberra', 'chebyshev', 'cityblock',
    'correlation', 'cosine', 'dice', 'euclidean', 'hamming',
    'jaccard', 'jensenshannon', 'kulsinski', 'matching',
    #'mahalanobis', 
    'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean',
    'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule']

for metric in metrics:
    df[metric] = df.apply(distance_3d, metric=metric, axis=1)
    df.plot(kind='scatter',x='truth',y=metric,color='blue')
    plt.show()

## Plot ground truth (?)
df.plot(kind='scatter',x='time_elapsed',y='truth',color='blue')

## correlation with truth?
plot_data = df.query('truth<150').\
    loc[:,['truth','braycurtis', 'canberra', 'chebyshev', 'cityblock',
    'correlation', 'cosine', 'euclidean', 'minkowski']]

plot_data.corr().loc[:,['truth']].style.background_gradient(cmap='RdYlBu').set_precision(3)

df.to_csv('test_dist.csv')
