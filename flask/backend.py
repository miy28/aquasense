# hold collected data

import numpy as np
import pandas as pd

dataframes = []

def push_data(json):
    df = pd.read_json(json, orient='index')
    dataframes.append(df)
    return len(dataframes)