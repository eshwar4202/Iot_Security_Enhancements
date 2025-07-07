from flask import Flask, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# Firebase Configuration
FIREBASE_RTD_URL = "https://iotsecurity-30d1a-default-rtdb.firebaseio.com/sensors"


def fetch_firebase_data():
    """Fetches all data from Firebase under the sensors node."""
    try:
        response = requests.get(f"{FIREBASE_RTD_URL}.json")
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"❌ Failed to fetch Firebase data: {response.status_code} - {response.text}"
            )
            return {}
    except Exception as e:
        print(f"❌ Firebase fetch failed: {e}")
        return {}


def parse_timestamp_to_iso(timestamp):
    """Converts IST timestamp (YYYY-MM-DD HH:MM:SS) to ISO 8601 format."""
    ist = pytz.timezone("Asia/Kolkata")
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    dt = ist.localize(dt)  # Localize to IST
    return dt.isoformat()  # e.g., "2025-03-09T14:30:45+05:30"


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Serves vehicle count data for Grafana in Simple JSON format."""
    data = fetch_firebase_data()
    if not data:
        return jsonify([]), 500

    # Prepare time-series data for each lane
    metrics = [
        {"target": "lane_1_vehicle_count", "datapoints": []},
        {"target": "lane_2_vehicle_count", "datapoints": []},
    ]

    # Process lane_1 data
    if "lane_1" in data:
        for timestamp_key, entry in data["lane_1"].items():
            if "vehicle_count" in entry and "timestamp" in entry:
                iso_time = parse_timestamp_to_iso(entry["timestamp"])
                # Datapoints: [value, timestamp in milliseconds]
                metrics[0]["datapoints"].append(
                    [
                        entry["vehicle_count"],
                        int(datetime.fromisoformat(iso_time).timestamp() * 1000),
                    ]
                )

    # Process lane_2 data
    if "lane_2" in data:
        for timestamp_key, entry in data["lane_2"].items():
            if "vehicle_count" in entry and "timestamp" in entry:
                iso_time = parse_timestamp_to_iso(entry["timestamp"])
                metrics[1]["datapoints"].append(
                    [
                        entry["vehicle_count"],
                        int(datetime.fromisoformat(iso_time).timestamp() * 1000),
                    ]
                )

    # Sort datapoints by timestamp (optional, for cleaner visualization)
    for metric in metrics:
        metric["datapoints"].sort(key=lambda x: x[1])

    return jsonify(metrics)


@app.route("/search", methods=["POST", "GET"])
def search():
    """Returns available metric names for Grafana Simple JSON plugin."""
    return jsonify(["lane_1_vehicle_count", "lane_2_vehicle_count"])


@app.route("/query", methods=["POST"])
def query():
    """Handles Grafana query requests (alias for /metrics in this case)."""
    return get_metrics()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", port=5001, debug=True
    )  # Port 5001 to avoid conflict with existing app
