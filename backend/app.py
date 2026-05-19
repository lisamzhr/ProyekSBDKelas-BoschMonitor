from flask import Flask, request, jsonify
from db import insert_measurement, buckets_col, motors_col
from datetime import datetime, timezone

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "Bosch Motor Monitor API is running"})


@app.route("/telemetry", methods=["POST"])
def receive_telemetry():
    data = request.get_json()

    # validasi field wajib
    required = ["motor_id", "ax", "ay", "az", "gx", "gy", "gz", "temp", "hum"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        insert_measurement(data["motor_id"], data)
        return jsonify({
            "status": "ok",
            "motor_id": data["motor_id"],
            "received_at": datetime.now(timezone.utc).isoformat()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health/<motor_id>", methods=["GET"])
def get_health(motor_id):
    # ambil bucket terakhir yang sudah ditutup
    bucket = buckets_col.find_one(
        {"motor_id": motor_id, "is_closed": True},
        sort=[("bucket_start", -1)]
    )

    if not bucket:
        return jsonify({"message": "No closed bucket yet for this motor"}), 404

    motor = motors_col.find_one({"motor_id": motor_id})
    thresholds = motor["thresholds"] if motor else {}

    stats = bucket["stats"]
    vib_rms = stats.get("vib_rms", 0)
    temp_avg = stats.get("temp_avg", 0)
    vib_max = thresholds.get("vib_max", 2.0)
    temp_max = thresholds.get("temp_max", 70.0)

    # hitung health score sederhana 0-100
    vib_score = max(0, 100 - (vib_rms / vib_max) * 100)
    temp_score = max(0, 100 - (temp_avg / temp_max) * 100)
    health_score = round((vib_score + temp_score) / 2, 1)

    return jsonify({
        "motor_id": motor_id,
        "bucket_id": bucket["_id"],
        "stats": stats,
        "health_score": health_score,
        "thresholds": thresholds
    })


@app.route("/buckets/<motor_id>", methods=["GET"])
def get_buckets(motor_id):
    # ambil 10 bucket terakhir
    cursor = buckets_col.find(
        {"motor_id": motor_id},
        {"measurements": 0}  # exclude array besar, ambil stats saja
    ).sort("bucket_start", -1).limit(10)

    result = []
    for b in cursor:
        b["_id"] = str(b["_id"])
        b["bucket_start"] = b["bucket_start"].isoformat()
        result.append(b)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)