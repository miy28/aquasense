import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json
from ml.anomaly import detect_anomalies
import pandas as pd

from backend import push_data

app = Flask(__name__)
CORS(app)


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

# new get endpoint for React
@app.route('/api/data', methods=['GET'])
def serve_all_data():
    from backend import data
    from ml.anomaly import run_all_anomaly_checks

    data_copy = data.copy()
    data_copy['is_anomaly'] = False
    data_copy['anomaly_reason'] = None

    anomalies = run_all_anomaly_checks(data)
    anomalies['is_anomaly'] = True

    combined = pd.concat([data_copy, anomalies], ignore_index=True)
    combined = combined.drop_duplicates(subset=['sensor_type', 'value', 'timestamp'], keep='last')
    
    combined = combined.where(pd.notnull(combined), None)

    return jsonify(json.loads(combined.to_json(orient='records')))


# endpoint to get temp data from arduino
@app.route('/data/temp', methods=['POST'])
def get_temp_data(): # retrieve post request and send to the pandas backend
    data = request.get_json(silent=True)
    if not data:
        print("Error: invalid JSON.")
        return -1

    sensor_type = data.get("sensor_type")
    temp = data.get("value")
    
    if(sensor_type == "temp"):
        print(f"Temperature: {temp} [Fahrenheit].")

        print("Storing...")
        time = datetime.datetime.now()  
        data["timestamp"] = time

        print(data)
        push_data(data)
    else:
        print("No temperature readings found!")
        return -1
    
    return str(temp)

# endpoint to get pH data from arduino
@app.route('/data/pH', methods=['POST'])
def get_ph_data(): 
    data = request.get_json(silent=True)
    if not data:
        print("Error: invalid JSON.")
        return -1

    sensor_type = data.get("sensor_type")
    ph = data.get("value")
    
    if(sensor_type == "acid"):
        print(f"Acidity Level: {ph} [pH].")

        print("Storing...")
        time = datetime.datetime.now()
        data["timestamp"] = time

        push_data(data)
    else:
        print("No acidity readings found!")
        return -1

    return ph

# def get_do_data(): 
#     data = request.get_json(silent=True)
#     if not data:
#         print("Error: invalid JSON.")
#         return -1

#     sensor_type = data.get("sensor_type")
#     do = data.get("value")
    
#     if(sensor_type == "oxygen"):
#         print(f"Dissolved oxygen concentration: {do} [mg/L].")
        
#         print("Storing...")
#         time = datetime.datetime.now()
#         data["timestamp"] = time

#         push_data(data)
#     else:
#         print("No dissolved oxygen readings found!")
#         return -1

#     return do

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)