"""
model_utils.py

this might get cooked 

anomaly.py isn't user specific or anything, just detects numbers inside and outside a range
this model_utils file should:
- Understand natural fluctuations
- Learn from history
- Adapt to specific tanks

Take historical sensor data
Use it to train an ML model to detect anomalies that go beyond hard-coded thresholds.
Examples:
- A temperature spike that's unusual compared to your tank's normal range
- A pattern in pH that precedes fish death
- Sensor noise vs actual problem

does not run live; in charge of:
- Reading the entire historical dataset
- Training an anomaly detection model
- Saving it to disk
- Loading it when needed

Purpose:
Handles training, saving, loading, and inference for machine learning models
used in the system. This includes anomaly detection models and any future
predictive or classification models.

Future responsibilities:
- Preprocess historical data
- Train models
- Save/load models with joblib or pickle
- Expose utility functions for real-time inference
"""
