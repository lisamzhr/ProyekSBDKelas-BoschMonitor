from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["bosch_monitor"]

buckets_col = db["buckets"]
motors_col = db["motors"]

BUCKET_SIZE = 300  # max readings per bucket


def get_or_create_bucket(motor_id):
    # cari bucket yang belum penuh dan belum ditutup
    bucket = buckets_col.find_one({
        "motor_id": motor_id,
        "is_closed": False
    })

    if not bucket:
        # buat bucket baru
        now = datetime.now(timezone.utc)
        bucket_id = f"{motor_id}_{now.strftime('%Y-%m-%dT%H:%M:%S')}"
        new_bucket = {
            "_id": bucket_id,
            "motor_id": motor_id,
            "bucket_start": now,
            "count": 0,
            "measurements": [],
            "stats": {
                "vib_rms": None,
                "temp_avg": None,
                "temp_max": None
            },
            "is_closed": False
        }
        buckets_col.insert_one(new_bucket)
        return bucket_id

    return bucket["_id"]


def insert_measurement(motor_id, data):
    bucket_id = get_or_create_bucket(motor_id)

    measurement = {
        "t": datetime.now(timezone.utc),
        "ax": data["ax"],
        "ay": data["ay"],
        "az": data["az"],
        "gx": data["gx"],
        "gy": data["gy"],
        "gz": data["gz"],
        "temp": data["temp"],
        "hum": data["hum"]
    }

    # push measurement ke bucket
    buckets_col.update_one(
        {"_id": bucket_id},
        {
            "$push": {"measurements": measurement},
            "$inc": {"count": 1}
        }
    )

    # cek apakah bucket sudah penuh
    updated = buckets_col.find_one({"_id": bucket_id})
    if updated["count"] >= BUCKET_SIZE:
        close_bucket(bucket_id, updated["measurements"])


def close_bucket(bucket_id, measurements):
    import math

    temps = [m["temp"] for m in measurements]
    ax_list = [m["ax"] for m in measurements]
    ay_list = [m["ay"] for m in measurements]
    az_list = [m["az"] for m in measurements]

    # hitung RMS vibrasi
    rms = math.sqrt(
        sum(ax**2 + ay**2 + az**2
            for ax, ay, az in zip(ax_list, ay_list, az_list))
        / len(measurements)
    )

    stats = {
        "vib_rms": round(rms, 4),
        "temp_avg": round(sum(temps) / len(temps), 2),
        "temp_max": round(max(temps), 2)
    }

    buckets_col.update_one(
        {"_id": bucket_id},
        {"$set": {"is_closed": True, "stats": stats}}
    )


def seed_motor_metadata():
    # insert data motor kalau belum ada
    motors = [
        {
            "_id": "MOTOR_01",
            "motor_id": "MOTOR_01",
            "location": "Line A - Station 3",
            "model": "Bosch Rexroth MSK071",
            "thresholds": {"vib_max": 2.0, "temp_max": 70.0},
            "status": "normal"
        },
        {
            "_id": "MOTOR_02",
            "motor_id": "MOTOR_02",
            "location": "Line B - Station 1",
            "model": "Bosch Rexroth MSK050",
            "thresholds": {"vib_max": 1.8, "temp_max": 65.0},
            "status": "normal"
        }
    ]
    for motor in motors:
        motors_col.update_one(
            {"_id": motor["_id"]},
            {"$setOnInsert": motor},
            upsert=True
        )
    print("Motor metadata seeded.")


if __name__ == "__main__":
    seed_motor_metadata()
    print("Koneksi MongoDB OK.")