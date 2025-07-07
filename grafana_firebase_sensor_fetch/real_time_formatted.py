from flask import Flask, jsonify
import requests
import time

# Base Firebase Realtime Database URL
BASE_URL = "https://iotsecurity-30d1a-default-rtdb.firebaseio.com/sensors.json"

app = Flask(__name__)


def fetch_all_data():
    """Fetch all sensor data from Firebase Realtime Database."""
    response = requests.get(BASE_URL)

    if response.status_code == 200:
        sensors_data = response.json()
        if sensors_data:
            all_data = {}
            for device_id, readings in sensors_data.items():
                device_readings = readings.get("readings", {})
                all_data[device_id] = device_readings
            return all_data
        else:
            return {"message": "No devices found in the database."}
    else:
        return {"error": f"Failed to retrieve data: {response.status_code}"}


from datetime import datetime
import time


def format_for_grafana(data):
    """Format sensor data for Grafana's JSON API."""
    rows = []

    for device_id, readings in data.items():
        for reading_id, reading in readings.items():
            timestamp_str = reading["timestamp"]

            # Try parsing with both formats
            try:
                parsed_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                try:
                    parsed_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    try:
                        parsed_time = datetime.strptime(
                            timestamp_str, "%Y-%m-%d %H:%M:%S.%f"
                        )
                    except ValueError:
                        parsed_time = datetime.strptime(
                            timestamp_str, "%Y-%m-%d %H:%M:%S"
                        )

            # Convert to UNIX milliseconds
            timestamp = int(parsed_time.timestamp() * 1000)

            # Append formatted row
            rows.append(
                [
                    timestamp,
                    reading["heart_rate"],
                    reading["spo2"],
                    reading["ax"],
                    reading["ay"],
                    reading["az"],
                    reading["gx"],
                    reading["gy"],
                    reading["gz"],
                ]
            )

    return {
        "table": {
            "columns": [
                {"text": "Timestamp", "type": "time"},
                {"text": "Heart Rate", "type": "number"},
                {"text": "SpO2", "type": "number"},
                {"text": "Ax", "type": "number"},
                {"text": "Ay", "type": "number"},
                {"text": "Az", "type": "number"},
                {"text": "Gx", "type": "number"},
                {"text": "Gy", "type": "number"},
                {"text": "Gz", "type": "number"},
            ],
            "rows": rows,
            "type": "table",
        }
    }


@app.route("/data", methods=["GET"])
def get_data():
    """API route to fetch and format sensor data for Grafana."""
    raw_data = fetch_all_data()

    # If Firebase returned an error, forward it as JSON
    if "error" in raw_data or "message" in raw_data:
        return jsonify(raw_data)

    formatted_data = format_for_grafana(raw_data)
    return jsonify(formatted_data)


if __name__ == "__main__":
    print("🌍 Starting Flask server on http://0.0.0.0:5000/data ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
