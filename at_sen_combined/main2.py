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
    """Serves aligned sensor and attack data for Grafana."""
    sensors_data = fetch_firebase_data(SENSORS_URL)
    attack_data = fetch_firebase_data(ATTACK_URL)

    if not sensors_data or not attack_data:
        return jsonify([]), 500

    # Collect all unique timestamps
    all_timestamps = set()
    lane_1_data = {}
    lane_2_data = {}
    attack_data_points = {}

    # Process lane_1
    if "lane_1" in sensors_data:
        for timestamp_key, entry in sensors_data["lane_1"].items():
            if "vehicle_count" in entry and "timestamp" in entry:
                ts_ms = parse_timestamp_to_millis(entry["timestamp"])
                all_timestamps.add(ts_ms)
                lane_1_data[ts_ms] = entry["vehicle_count"]

    # Process lane_2
    if "lane_2" in sensors_data:
        for timestamp_key, entry in sensors_data["lane_2"].items():
            if "vehicle_count" in entry and "timestamp" in entry:
                ts_ms = parse_timestamp_to_millis(entry["timestamp"])
                all_timestamps.add(ts_ms)
                lane_2_data[ts_ms] = entry["vehicle_count"]

    # Process attacks
    for timestamp_key, entry in attack_data.items():
        if "message" in entry:
            timestamp_str = entry["message"].split("Timestamp: ")[1]
            ts_ms = parse_timestamp_to_millis(timestamp_str)
            all_timestamps.add(ts_ms)
            attack_data_points[ts_ms] = 1  # Mark attack with value 1

    # Sort timestamps
    sorted_timestamps = sorted(all_timestamps)

    # Build aligned datapoints
    lane_1_datapoints = []
    lane_2_datapoints = []
    attack_datapoints = []

    for ts in sorted_timestamps:
        lane_1_value = lane_1_data.get(ts, None)  # None if no data at this timestamp
        lane_2_value = lane_2_data.get(ts, None)
        attack_value = attack_data_points.get(ts, None)

        lane_1_datapoints.append([lane_1_value, ts])
        lane_2_datapoints.append([lane_2_value, ts])
        attack_datapoints.append([attack_value, ts])

    metrics = [
        {"target": "lane_1_vehicle_count", "datapoints": lane_1_datapoints},
        {"target": "lane_2_vehicle_count", "datapoints": lane_2_datapoints},
        {"target": "attacks", "datapoints": attack_datapoints},
    ]

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
    app.run(host="0.0.0.0", port=5002, debug=True)
