import os
from flask import Flask, jsonify, request
from tms_client import TMSClient, TMSConnectionError

app = Flask(__name__)

API_KEY = os.environ.get("TMS_ADAPTER_API_KEY", "")
client = TMSClient()


def verify_api_key():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token or token != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return None


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "TMS Adapter ready"}), 200


@app.route("/health", methods=["GET"])
def health_check():
    try:
        client.debug_echo()
        return jsonify({"status": "healthy", "tms": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route("/loads/search", methods=["POST"])
def search_loads():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    origin = data.get("origin")
    destination = data.get("destination")
    equipment = data.get("equipment")

    try:
        result = client.load_query(origin, destination, equipment)
        return jsonify({"result": result}), 200
    except TMSConnectionError as e:
        return jsonify({"error": str(e)}), 503


@app.route("/loads/<load_id>", methods=["GET"])
def get_load(load_id):
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    try:
        response = client.load_get(load_id)
        details = client.parse_load_details(response)
        return jsonify(details), 200
    except TMSConnectionError as e:
        return jsonify({"error": str(e)}), 503


@app.route("/loads/<load_id>/book", methods=["POST"])
def book_load(load_id):
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    return jsonify({"message": "Booking not yet implemented"}), 501


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
