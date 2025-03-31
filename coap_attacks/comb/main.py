from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

SENSOR_URL = "http://localhost:5000/data"
ATTACKS_URL = "http://localhost:5001/attacks"


def fetch_sensor_data():
    response = requests.get(SENSOR_URL)
    return response.json() if response.status_code == 200 else {}


def fetch_attack_data():
    response = requests.get(ATTACKS_URL)
    return response.json() if response.status_code == 200 else {}


@app.route("/combined", methods=["GET"])
def get_combined_data():
    """Fetch sensor and attack data and return a single JSON response."""
    sensor_data = fetch_sensor_data()
    attack_data = fetch_attack_data()

    return jsonify({"sensor": sensor_data, "attacks": attack_data})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)  # Run on a single port
