import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

IDEAL_TEMP_RANGE = (55, 85)
IDEAL_PH_RANGE = (6.5, 8.5)

# --- Basic threshold check (unsafe ranges) ---
def detect_anomalies(df: pd.DataFrame):
    """Detects readings outside ideal ranges."""
    alerts = []

    for i, row in df.iterrows():
        sensor_type = row['sensor_type'].lower()
        value = row['value']
        
        if 'temp' in sensor_type:
            if not (IDEAL_TEMP_RANGE[0] <= value <= IDEAL_TEMP_RANGE[1]):
                row_dict = row.to_dict()
                row_dict['anomaly_reason'] = 'temperature out of range'
                alerts.append(row_dict)

        elif 'ph' in sensor_type:
            if not (IDEAL_PH_RANGE[0] <= value <= IDEAL_PH_RANGE[1]):
                row_dict = row.to_dict()
                row_dict['anomaly_reason'] = 'pH out of range'
                alerts.append(row_dict)

    return pd.DataFrame(alerts)

# --- Spike Detection (for temp, pH, light) ---
def detect_spikes(df: pd.DataFrame, spike_thresholds={'temp': 0.5, 'ph': 0.2, 'light': 100.0}):
    """Detects sudden jumps/drops in sensor values, grouped properly by sensor type."""
    alerts = []
    
    # Group by sensor type to avoid cross-sensor diffs
    for sensor_type, group in df.groupby('sensor_type'):
        group = group.sort_values('timestamp')  # Sort inside group
        
        # Calculate delta within the sensor group
        group['delta'] = group['value'].diff().abs()

        threshold = None
        sensor_lower = sensor_type.lower()

        if 'temp' in sensor_lower:
            threshold = spike_thresholds['temp']
        elif 'ph' in sensor_lower:
            threshold = spike_thresholds['ph']
        elif 'light' in sensor_lower:
            threshold = spike_thresholds['light']
        
        if threshold is None:
            continue

        for _, row in group.iterrows():
            if pd.notna(row['delta']) and row['delta'] > threshold:
                row_dict = row.to_dict()
                if 'temp' in sensor_lower:
                    row_dict['anomaly_reason'] = 'sudden temperature spike'
                elif 'ph' in sensor_lower:
                    row_dict['anomaly_reason'] = 'sudden pH spike'
                elif 'light' in sensor_lower:
                    row_dict['anomaly_reason'] = 'sudden light spike'
                alerts.append(row_dict)

    return pd.DataFrame(alerts)


# --- Run all anomaly checks together ---
def run_all_anomaly_checks(df: pd.DataFrame):
    """Combines threshold and spike-based anomaly detection."""
    threshold_alerts = detect_anomalies(df)
    spike_alerts = detect_spikes(df)

    combined = pd.concat([threshold_alerts, spike_alerts], ignore_index=True)
    combined = combined.drop_duplicates()
    return combined

# --- Advanced PCA-based anomaly detection (optional) ---
def detect_pca_anomalies(df: pd.DataFrame,
                         sensor: str = 'temp',
                         n_components: int = 1,
                         threshold: float = 3.0) -> pd.DataFrame:
    """Flags readings with high PCA reconstruction error."""
    temp_df = df[df.sensor_type.str.contains(sensor, case=False)].sort_values('timestamp')
    if temp_df.empty:
        return pd.DataFrame(columns=df.columns.tolist() + ['anomaly_reason'])

    values = temp_df['value'].to_numpy().reshape(-1, 1)
    scaler = StandardScaler().fit(values)
    scaled = scaler.transform(values)

    pca = PCA(n_components=n_components).fit(scaled)
    projected = pca.transform(scaled)
    reconstructed = pca.inverse_transform(projected)

    recon_err = np.mean((scaled - reconstructed)**2, axis=1)
    mean_err, std_err = recon_err.mean(), recon_err.std()

    outlier_mask = recon_err > (mean_err + threshold * std_err)
    outliers = temp_df.iloc[np.where(outlier_mask)[0]].copy()
    outliers['anomaly_reason'] = 'PCA reconstruction error'
    return outliers