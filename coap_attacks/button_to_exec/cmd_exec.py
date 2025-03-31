from flask import Flask, request, jsonify, render_template
import subprocess
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)  # Enable CORS to avoid frontend errors

# Mapping attack types to shell scripts or commands
attack_scripts = {
    "flood": "./block_flood.sh",
    "resource": "./limit_resources.sh",
    "cache": "./purge_cache.sh",
    "observe": "./throttle_observe.sh",
    "uri": "./validate_uris.sh",
}


@app.route("/")
def index():
    """Serve the HTML page."""
    return render_template("index.html")


@app.route("/execute", methods=["POST"])
def execute_script():
    """Handle attack execution requests."""
    data = request.json
    attack_type = data.get("attack")

    if attack_type in attack_scripts:
        script_path = attack_scripts[attack_type]

        try:
            # Execute the script and capture output
            result = subprocess.run(
                [script_path], capture_output=True, text=True, shell=True
            )
            return jsonify({"status": "success", "output": result.stdout})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid attack type"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
