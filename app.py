import os
import time
import logging
from flask import Flask, jsonify, request
from tms_client import TMSClient, TMSConnectionError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app")

app = Flask(__name__)

API_KEY = os.environ.get("TMS_ADAPTER_API_KEY", "")
_client = None

# In-memory cache: query key -> {"loads": [...], "ts": epoch_seconds}
# Last-resort fallback only, used after live + broadened-query attempts both
# fault. Kept short-lived since rates/availability change frequently -- this
# is not meant to serve long-lived "stale" pricing.
_search_cache = {}
CACHE_TTL_SECONDS = 60


def get_client():
    global _client
    if _client is None:
        _client = TMSClient()
    return _client


def _cache_key(origin, destination, equipment):
    return f"{origin or ''}|{destination or ''}|{equipment or ''}"


# Fields TMS sends as space-padded strings but that are semantically numbers.
# Converted to real JSON numbers so consumers don't have to parse strings.
_NUMERIC_FIELDS = {"RATE", "MAX_BUY", "WEIGHT", "MILES", "PIECES"}


def _sanitize_load(load: dict) -> dict:
    if "LOAD_ID" not in load:
        return load  # error shape (CODE/MSG), not a load record -- leave as-is
    sanitized = dict(load)
    for field in _NUMERIC_FIELDS:
        value = sanitized.get(field)
        if isinstance(value, str) and value.strip().isdigit():
            sanitized[field] = int(value.strip())
    return sanitized


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
        echo = get_client().debug_echo()
        if not echo:
            return jsonify({"status": "unhealthy", "tms": "no_response", "error": "TMS did not respond to DEBUG_ECHO"}), 503
        return jsonify({"status": "healthy", "tms": "connected", "echo": echo}), 200
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

    key = _cache_key(origin, destination, equipment)

    try:
        loads = get_client().load_query(origin, destination, equipment)

        if isinstance(loads, dict) and "error" in loads:
            # Live + broadened query both faulted. Fall back to the last
            # known-good result for this query, only if it's within the
            # short TTL (rates/availability change too fast to serve older data).
            cached = _search_cache.get(key)
            age = (time.time() - cached["ts"]) if cached else None
            if cached and age < CACHE_TTL_SECONDS:
                logger.warning(f"SEARCH fault, serving cache key=\"{key}\" age={age:.1f}s fault=\"{loads['error']}\"")
                return jsonify({"loads": cached["loads"], "count": len(cached["loads"]), "source": "cache", "cached_at": cached["ts"], "fault": loads["error"]}), 200
            logger.error(f"SEARCH fault, no usable cache key=\"{key}\" cache_age={age}")
            return jsonify(loads), 400

        loads = [_sanitize_load(l) for l in loads]
        _search_cache[key] = {"loads": loads, "ts": time.time()}
        load_ids = [l.get("LOAD_ID", "?").strip() for l in loads]
        logger.info(f"SEARCH live key=\"{key}\" count={len(loads)} load_ids={load_ids}")
        return jsonify({"loads": loads, "count": len(loads), "source": "live"}), 200
    except TMSConnectionError as e:
        cached = _search_cache.get(key)
        age = (time.time() - cached["ts"]) if cached else None
        if cached and age < CACHE_TTL_SECONDS:
            logger.warning(f"SEARCH connection error, serving cache key=\"{key}\" age={age:.1f}s error=\"{e}\"")
            return jsonify({"loads": cached["loads"], "count": len(cached["loads"]), "source": "cache", "cached_at": cached["ts"], "fault": str(e)}), 200
        logger.error(f"SEARCH connection error, no usable cache key=\"{key}\" error=\"{e}\"")
        return jsonify({"error": str(e)}), 503


@app.route("/loads/<load_id>", methods=["GET"])
def get_load(load_id):
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    try:
        response = get_client().load_get(load_id)
        details = _sanitize_load(get_client().parse_load_details(response))
        logger.info(f"GET_LOAD load_id=\"{load_id}\" result={details}")
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
