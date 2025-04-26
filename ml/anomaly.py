"""
anomaly.py

This module contains real-time anomaly detection logic for AquaSense sensor data.

Responsibilities:
- Detects abnormal sensor readings using rule-based methods (e.g., threshold checks).
- Can be extended to include derivative/spike detection and lightweight anomaly heuristics.
- Designed to run in real-time on incoming data to trigger alerts and logging.

Typical usage:
- Called whenever new data is received from sensors to check for unsafe or unusual conditions.
"""
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# only put in random sample temps for now
IDEAL_TEMP_RANGE = (55, 85)
IDEAL_PH_RANGE = (6.5, 8.5)

'''
# Example DataFrame:
sensor_type | value | timestamp
------------|-------|----------
temp        | 23    | 2025-03-26 14:45:00

# turns into:
[
  {
    "sensor_type": "temp",
    "value": 23,
    "timestamp": "2025-03-26 14:45:00"
  }
]
'''

# basic anomaly detection here so that we can find clearly hazardous values
def detect_anomalies(df: pd.DataFrame):
    """Returns rows with out-of-range values"""
    alerts = []

    for i, row in df.iterrows():
        if row['sensor_type'] == 'temp':
            if not (IDEAL_TEMP_RANGE[0] <= row['value'] <= IDEAL_TEMP_RANGE[1]):
                alerts.append(row)
        elif row['sensor_type'] == 'acid': # may need to be changed depending on output of the pH sensor
            if not (IDEAL_PH_RANGE[0] <= row['value'] <= IDEAL_PH_RANGE[1]):
                alerts.append(row)

    return pd.DataFrame(alerts)

# used to find spikes in teh data which could signal issues
def detect_spikes(df: pd.DataFrame, spike_thresholds={'temp':3.0, 'acid':0.5}):
    df = df.sort_values('timestamp') # sort to ensure correct order (safety)
    df['delta'] = df['value'].diff() 
    df['sensor_prev'] = df['sensor_type'].shift() # temp columns added to perform analysis

    alerts = []

    for i, row in df.iterrows():
        if row['sensor_type'] != row['sensor_prev']:
            continue # the sensor data does not match (values are from diff sensors)
        
        sensor = row['sensor_type']
        delta = abs(row['delta'])

        if sensor in spike_thresholds and delta > spike_thresholds[sensor]:
            row_dict = row.to_dict() # turn data into dict (normal df layout)
            row_dict['anomaly_reason'] = f"sudden {sensor} spike" 
            alerts.append(row_dict)
    
    return pd.DataFrame(alerts)

def run_all_anomaly_checks(df: pd.DataFrame):
    threshold_alerts = detect_anomalies(df)
    spike_alerts = detect_spikes(df)

    combined = pd.concat([threshold_alerts, spike_alerts], ignore_index=True)
    combined = combined.drop_duplicates()

    return combined

def detect_pca_anomalies(df: pd.DataFrame,
                         sensor: str = 'temp',
                         n_components: int = 1,
                         threshold: float = 3.0) -> pd.DataFrame:
    """ copilot comm
    Flag temperature readings whose PCA reconstruction error is > mean + threshold*std.
    Returns a DataFrame of those anomalous rows with `anomaly_reason='PCA reconstruction error'`.
    """

    # 1) Filter just the temperature sensor - has to be updated for ph n light
    temp_df = df[df.sensor_type == sensor].sort_values('timestamp')
    if temp_df.empty:
        return pd.DataFrame(columns=df.columns.tolist() + ['anomaly_reason'])

    # 2) Standardize values -scikit
    values = temp_df['value'].to_numpy().reshape(-1, 1)
    scaler = StandardScaler().fit(values)
    scaled = scaler.transform(values)

    # 3) Fit PCA & reconstruct
    pca = PCA(n_components=n_components).fit(scaled)
    projected    = pca.transform(scaled)
    reconstructed = pca.inverse_transform(projected)

    # 4) Compute reconstruction errors
    recon_err = np.mean((scaled - reconstructed)**2, axis=1)
    mean_err, std_err = recon_err.mean(), recon_err.std()

    # 5) Flag outliers
    outlier_mask = recon_err > (mean_err + threshold * std_err)
    outliers = temp_df.iloc[np.where(outlier_mask)[0]].copy()
    outliers['anomaly_reason'] = 'PCA reconstruction error'
    return outliers



            