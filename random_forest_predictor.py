# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

API_KEY = "ayNClqmZuOOBeL6lFjA348UfsA0jpzazy8pjyXsQ"
API_IDS = {'wind': 'EBA.MISO-ALL.NG.WND.H',
        'solar': 'EBA.MISO-ALL.NG.SUN.H',
        'hydro': 'EBA.MISO-ALL.NG.WAT.H',
        'coal': 'EBA.MISO-ALL.NG.COL.H',
        'natural_gas': 'EBA.MISO-ALL.NG.NG.H',
        'nuclear': 'EBA.MISO-ALL.NG.NUC.H',
        'other': 'EBA.MISO-ALL.NG.OTH.H'}
HEADERS = {'Content-Type': 'application/json'}
USERNAME = input()
PASSWORD = input()

def get_historical_pi_data(name, start_time, end_time, interval):
    base_url = 'https://itsnt2259.iowa.uiowa.edu/piwebapi/search/query?q=name:'
    url = base_url + name
    query = requests.get(url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    self_url = query['Items'][0]['Links']['Self']
    point = requests.get(self_url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    data_url = point['Links']['InterpolatedData']
    data_url = data_url + '/?startTime=-' + start_time + '&endTime=-' + end_time + '&interval=' + interval
    data = requests.get(data_url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    return data

def get_historical_df(names, startTime, endTime, interval):
    df = pd.DataFrame()
    for i, name in enumerate(names):
        data = get_historical_pi_data(name, startTime, endTime, interval)
        items = data['Items']
        if i == 0:
            times = [int(datetime.strptime(item['Timestamp'][:-2], '%Y-%m-%dT%H:%M:%S.%f').timestamp()//3600) for item in items]
            df['Time'] = times
        validateData = lambda x: min(x, 50) if (isinstance(x, (int, float)) and x >= 0) else 0
        vals = [validateData(item['Value']) for item in items]
        df[name] = pd.DataFrame(vals)
    return df

def getTotalLoad(startTime="520w", endTime="1d", interval="1d"):
    names = ['PP_Electric_Purch', 'PP_Electric_Gen']
    df = get_historical_df(names, startTime, endTime, interval)
    df['Load'] = df['PP_Electric_Purch'] + df['PP_Electric_Gen']
    return df
data = getTotalLoad()
print(data)

feature_keys = [
    "PP_Electric_Purch",
    "PP_Electric_Gen",
    "Load"
]
colors = ["red", "orange", "green"]
date_time_key = "Time"

def show_raw_visualization(data):
    time_data = data[date_time_key]
    fig, axes = plt.subplots(
        nrows=3, ncols=1, figsize=(15, 10), dpi=80, facecolor="w", edgecolor="k"
    )
    for i in range(len(feature_keys)):
        key = feature_keys[i]
        t_data = data[key]
        t_data.index = time_data
        t_data.head()
        ax = t_data.plot(
            ax=axes[i],
            c=colors[i],
            title=key,
            rot=25,
        )
    plt.tight_layout()


show_raw_visualization(data)

train_split = int(0.9 * int(data.shape[0]))
train_data = data.iloc[:train_split]
test_data = data.iloc[train_split:]

print("Training datapoints:", train_data.shape[0])
print("Testing datapoints:", test_data.shape[0])

!pip install forestci

from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
# import forestci as fci
 
# fit the model
model = RandomForestRegressor()
# model = MLPRegressor(random_state=1, max_iter=500)

model.fit(train_data.iloc[:,[0,1]].values, train_data[['Load']].values.ravel().reshape(-1, 1))
# predict on the same period
preds = model.predict(test_data.iloc[:,[0,1]].values)
 
# plot what has been learned
plt.figure(figsize=(15,5))
plt.plot(train_data['Time'].values, train_data['Load'].values)
plt.plot(test_data['Time'].values, preds)

plt.figure(figsize=(15,5))
plt.plot(test_data['Time'].values, test_data['Load'].values)
plt.plot(test_data['Time'].values, preds)

var = fci.random_forest_error(model, train_data.iloc[:,[0,1]].values, test_data.iloc[:,[0,1]].values)
# print(var)
sigma = np.sqrt(var)
# print(sigma)

plt.figure(figsize=(15,5))
plt.plot(test_data['Time'].values, test_data['Load'].values)
plt.plot(test_data['Time'].values, preds)
plt.fill_between(test_data['Time'].values, (preds-2*sigma), (preds+2*sigma), color='b', alpha=.1)
