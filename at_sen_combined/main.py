from flask import Flask, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# Firebase Configuration
FIREBASE_BASE_URL = "https://iotsecurity-30d1a-default-rtdb.firebaseio.com/"
SENSORS_URL = f"{FIREBASE_BASE_URL}/sensors.json"
ATTACK_URL = f"{FIREBASE_BASE_URL}/attack.json"


def fetch_firebase_data(url):
    """Fetches data from Firebase."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch data: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Firebase fetch failed: {e}")
        return {}


def parse_timestamp_to_millis(timestamp):
    """Converts IST timestamp (YYYY-MM-DD HH:MM:SS) to milliseconds."""
    ist = pytz.timezone("Asia/Kolkata")
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    dt = ist.localize(dt)
    return int(dt.timestamp() * 1000)


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Serves combined sensor and attack data for Grafana."""
    sensors_data = fetch_firebase_data(SENSORS_URL)
    attack_data = fetch_firebase_data(ATTACK_URL)

    if not sensors_data or not attack_data:
        return jsonify([]), 500

    # Prepare time-series data
    metrics = [
        {"target": "lane_1_vehicle_count", "datapoints": []},
        {"target": "lane_2_vehicle_count", "datapoints": []},
        {"target": "attacks", "datapoints": []},  # Attack events
    ]

    # Process sensor data for lane_1
    if "lane_1" in sensors_data:
        for timestamp_key, entry in sensors_data["lane_1"].items():
            if "vehicle_count" in entry and "timestamp" in entry:
                timestamp_ms = parse_timestamp_to_millis(entry["timestamp"])
                metrics[0]["datapoints"].append([entry["vehicle_count"], timestamp_ms])

    # Process sensor data for lane_2
    if "lane_2" in sensors_data:
        for timestamp_key, entry in sensors_data["lane_2"].items():
            if "vehicle_count" in entry and "timestamp" in entry:
                timestamp_ms = parse_timestamp_to_millis(entry["timestamp"])
                metrics[1]["datapoints"].append([entry["vehicle_count"], timestamp_ms])

    # Process attack data
    for timestamp_key, entry in attack_data.items():
        if "message" in entry:
            # Extract timestamp from the message string
            timestamp_str = entry["message"].split("Timestamp: ")[1]
            timestamp_ms = parse_timestamp_to_millis(timestamp_str)
            # Use a value of 1 to mark attack occurrence
            metrics[2]["datapoints"].append([1, timestamp_ms])

    # Sort all datapoints by timestamp
    for metric in metrics:
        metric["datapoints"].sort(key=lambda x: x[1])

    return jsonify(metrics)


@app.route("/search", methods=["GET", "POST"])
def search():
    """Returns available metric names for Grafana."""
    return jsonify(["lane_1_vehicle_count", "lane_2_vehicle_count", "attacks"])


@app.route("/query", methods=["POST"])
def query():
    """Handles Grafana query requests."""
    return get_metrics()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)  # Port 5002 to avoid conflicts
