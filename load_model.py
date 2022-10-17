import os
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import requests
from datetime import datetime
import numpy as np
import streamlit as st

HEADERS = {'Content-Type': 'application/json'}

USERNAME = st.secrets["username"]
PASSWORD = st.secrets["password"]

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

def getTotalLoad(startTime="520w", endTime="1d", interval="1h"):
    names = ['PP_Electric_Purch', 'PP_Electric_Gen']
    df = get_historical_df(names, startTime, endTime, interval)
    df['Load'] = df['PP_Electric_Purch'] + df['PP_Electric_Gen']
    return df

def convert2matrix(data_arr, look_back):
    X, Y = [], []
    for i in range(len(data_arr)-look_back):
        d=i+look_back  
        X.append(data_arr[i:d])
        Y.append(data_arr[d])
    return np.array(X), np.array(Y)

def make_predictions(hours=12):
    past_day = getTotalLoad(startTime="24h", endTime="1h", interval="1h")
    # print(past_day.tail())
    all_preds = []
    vals = past_day['Load'].values
    vals = np.append(past_day['Load'].values, past_day['Load'].values[-1]) 
    testX, _ = convert2matrix(vals, 24)
    # print(testX.shape, testY.shape)
    # print(testY)
    reconstructed_model = keras.models.load_model("load_predictor")
    predictions = reconstructed_model.predict(testX)
    # print(predictions)
    all_preds.append(predictions[0,0])

    for i in range(hours-1):
        print(testX.shape, predictions.shape)
        # print(testX)
        testX = np.append(testX, predictions)[1:]
        testX = testX[np.newaxis,...]
        # print(testX)

        predictions = reconstructed_model.predict(testX)
        print(predictions)
        all_preds.append(predictions[0,0])
    past_xs = [x-len(vals)+1 for x in range(len(vals)-1)]
    past_load = vals[:-1]
    past = pd.DataFrame({'Time': past_xs, 'Load': past_load})
    pred_xs = [x for x in range(len(all_preds))]
    preds = pd.DataFrame({'Time': pred_xs, 'Load': all_preds})
    return past, preds
    
