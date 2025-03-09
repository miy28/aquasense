from flask import Flask, request, jsonify
import datetime
import json

from backend import push_data

app = Flask(__name__)

@app.route('/data', methods=['POST'])

def get_temp_data(): # retrieve post request and send to the pandas backend
    data = request.get_json(silent=True)
    if not data:
        print("Error: invalid JSON.")
        return -1

    sensor_type = data.get("sensor")
    temp = data.get("value")
    
    if(sensor_type == "temp"):
        print(f"Temperature: {temp} [Celsius].")

        print("Storing...")
        time = datetime.datetime.now()
        data["timestamp"] = time

        push_data(data)
    else:
        print("No temperature readings found!")
        return -1
    
    return temp

def get_ph_data(): 
    data = request.get_json(silent=True)
    if not data:
        print("Error: invalid JSON.")
        return -1

    sensor_type = data.get("sensor")
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

def get_do_data(): 
    data = request.get_json(silent=True)
    if not data:
        print("Error: invalid JSON.")
        return -1

    sensor_type = data.get("sensor")
    do = data.get("value")
    
    if(sensor_type == "oxygen"):
        print(f"Dissolved oxygen concentration: {do} [mg/L].")
        
        print("Storing...")
        time = datetime.datetime.now()
        data["timestamp"] = time

        push_data(data)
    else:
        print("No dissolved oxygen readings found!")
        return -1

    return do

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)