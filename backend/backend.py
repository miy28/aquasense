# hold collected data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import pickle
import os
from ml.anomaly import detect_anomalies

data = pd.DataFrame(columns=["sensor_type", "value", "timestamp"])

if os.path.exists('data.pkl'):
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)

def push_data(json_data):
    global data
    print("Received JSON:", json_data)

    try:
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
 
        df_new_row = pd.DataFrame([json_data])
        df_new_row["timestamp"] = pd.to_datetime(df_new_row["timestamp"])

        data = pd.concat([data, df_new_row], ignore_index=True)
        print("Added data.")
        print(data)

        with open('data.pkl', 'wb') as f:
                pickle.dump(data, f)
    
    except Exception as e:
        print("Error parsing JSON:", str(e))

    return len(data)

def visualize():
    global data
    fig, axs = plt.subplots(figsize=(12, 4))
    data.groupby(data["datetime"].datetime.second)["value"].plot(kind='bar', rot=0, ax=axs)
    plt.xlabel("Seconds")
    plt.ylabel("Celsius")
