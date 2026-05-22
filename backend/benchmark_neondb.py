import os
import time
import requests
import random
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# benchmark config
NEONDB_URI = os.getenv("NEONDB_URL")
API_URL_WRITE = "http://127.0.0.1:5000/telemetry"
API_URL_READ = "http://127.0.0.1:5000/buckets/MOTOR_BENCHMARK"
TOTAL_DATA = 300  # Simulasi 1 Bucket
MOTOR_ID = "MOTOR_BENCHMARK"

def generate_dummy():
    return {
        "motor_id": MOTOR_ID,
        "ax": round(random.uniform(-1.0, 1.0), 4),
        "ay": round(random.uniform(-1.0, 1.0), 4),
        "az": round(random.uniform(9.0, 10.0), 4),
        "gx": round(random.uniform(-0.1, 0.1), 4),
        "gy": round(random.uniform(-0.1, 0.1), 4),
        "gz": round(random.uniform(-0.1, 0.1), 4),
        "temp": round(random.uniform(40.0, 50.0), 2),
        "hum": round(random.uniform(50.0, 60.0), 2)
    }


# NEONDB Table
print("Connecting to NeonDB (Cloud PostgreSQL)...")
try:
    conn = psycopg2.connect(NEONDB_URI)
    cursor = conn.cursor()
    # Reset table everytime benchmark run
    cursor.execute("DROP TABLE IF EXISTS measurements;")
    cursor.execute("""
        CREATE TABLE measurements (
            id SERIAL PRIMARY KEY,
            motor_id VARCHAR(50),
            t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ax REAL, ay REAL, az REAL,
            gx REAL, gy REAL, gz REAL,
            temp REAL, hum REAL
        );
    """)
    conn.commit()
    print("✓ NeonDB ready. The measurements table has been reset.\n")
except Exception as e:
    print(f"❌ Failed to connect to NeonDB: {e}")
    print("Ensure that the NEONDB_URI is filled correctly.")
    exit()

print(f"=== STARTING BENCHMARK: {TOTAL_DATA} SENSOR DATA ===")
print("Comparing Local API Flask (NoSQL) vs Cloud NeonDB (SQL)\n")

# WRITE LATENCY 
print("--- TEST 1: WRITE LATENCY ---")

# NoSQL 
start_nosql_write = time.perf_counter()
for _ in range(TOTAL_DATA):
    data = generate_dummy()
    try:
        requests.post(API_URL_WRITE, json=data)
    except requests.exceptions.ConnectionError:
        print("❌ Flask API is not running! Run 'python app.py' first in another terminal.")
        exit()
end_nosql_write = time.perf_counter()
nosql_write_time = (end_nosql_write - start_nosql_write) * 1000

# SQL (Direct Insert to NeonDB)
start_sql_write = time.perf_counter()
for _ in range(TOTAL_DATA):
    data = generate_dummy()
    cursor.execute("""
        INSERT INTO measurements (motor_id, ax, ay, az, gx, gy, gz, temp, hum) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (data["motor_id"], data["ax"], data["ay"], data["az"], data["gx"], data["gy"], data["gz"], data["temp"], data["hum"]))
    conn.commit() # Disimpan satu per satu meniru sifat streaming IoT
end_sql_write = time.perf_counter()
sql_write_time = (end_sql_write - start_sql_write) * 1000

print(f"NoSQL (API Bucket Pattern) : {nosql_write_time:.2f} ms")
print(f"SQL (NeonDB Row-Based)     : {sql_write_time:.2f} ms")
if nosql_write_time < sql_write_time:
    print("Write Winner: NoSQL (Faster)\n")
else:
    print("Write Winner: SQL (Faster)\n")


# READ LATENCY
print("--- TEST 2: READ LATENCY ---")

start_nosql_read = time.perf_counter()
res = requests.get(API_URL_READ)
nosql_results = res.json() 
end_nosql_read = time.perf_counter()
nosql_read_time = (end_nosql_read - start_nosql_read) * 1000

# SQL Read (Query 300 data terbaru dari NeonDB)
start_sql_read = time.perf_counter()
cursor.execute("SELECT * FROM measurements WHERE motor_id = %s ORDER BY id DESC LIMIT %s", (MOTOR_ID, TOTAL_DATA))
sql_results = cursor.fetchall()
end_sql_read = time.perf_counter()
sql_read_time = (end_sql_read - start_sql_read) * 1000

print(f"NoSQL (API Bucket Pattern) : {nosql_read_time:.2f} ms")
print(f"SQL (NeonDB Row-Based)     : {sql_read_time:.2f} ms")
if nosql_read_time < sql_read_time:
    print("Read Winner: NoSQL (Faster)\n")
else:
    print("Read Winner: SQL (Faster)\n")

# clear connection
cursor.close()
conn.close()