"""
anomaly.py

this will just check against the values that we are defining in the threshold

Purpose:
This module will contain logic for rule-based and ML-based anomaly detection.
It will scan incoming sensor data for out-of-range or unusual patterns,
trigger alerts, and return flagged records to the system for logging or user notifications.

Initial version uses threshold-based checks (e.g., temperature/pH out of range)
"""


import pandas as pd

# only put in random sample temps for now
IDEAL_TEMP_RANGE = (65, 75)
IDEAL_PH_RANGE = (6.5, 8.5)

def detect_anomalies(df: pd.DataFrame):
    """Returns rows with out-of-range values"""
    alerts = []

    for _, row in df.iterrows():
        if row['sensor_type'] == 'temp':
            if not (IDEAL_TEMP_RANGE[0] <= row['value'] <= IDEAL_TEMP_RANGE[1]):
                alerts.append(row)
        elif row['sensor_type'] == 'acid': # may need to be changed depending on output of the pH sensor
            if not (IDEAL_PH_RANGE[0] <= row['value'] <= IDEAL_PH_RANGE[1]):
                alerts.append(row)

    return pd.DataFrame(alerts)
