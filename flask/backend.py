# hold collected data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

data = pd.DataFrame(columns=["sensor", "value", "timestamp"])

def push_data(json):
    global data
    df_new_row = pd.read_json(json, orient='records')
    df_new_row["timestamp"] = pd.to_datetime(df_new_row["timestamp"])

    data = pd.concat([data, df_new_row], ignore_index=True)

    return len(data)

def visualize():
    global data
    fig, axs = plt.subplots(figsize=(12, 4))
    data.groupby(data["datetime"].datetime.second)["value"].plot(kind='bar', rot=0, ax=axs)
    plt.xlabel("Seconds")
    plt.ylabel("Celsius")