import requests
import time
import random
import math

# Konfigurasi
SERVER_URL = "https://proyeksbdkelas-boschmonitor.onrender.com/telemetry" # ganti pakai variabel di .env
MOTOR_ID = "MOTOR_01"
DELAY_SECONDS = 1  # Kirim tiap 1 detik sesuai delay(1000) di sketch.ino

# FASE (Dalam Detik/Siklus)
# BUCKET_SIZE = 300 di db.py (1 bucket = 5 menit)
PHASE_NORMAL_DURATION = 300    # 5 Menit pertama (Bucket 1): Normal
PHASE_WARNING_DURATION = 600   # 5 Menit kedua (Bucket 2): Warning
# Setelah siklus ke-600 otomatis masuk fase FAULT (Bucket 3 dan seterusnya)

def generate_telemetry(cycle_count):
    """
    Fungsi untuk menghasilkan data telemetri berdasarkan siklus waktu (kondisi motor).
    """
    # Kondisi Normal
    if cycle_count < PHASE_NORMAL_DURATION:
        ax = random.uniform(-0.1, 0.1)
        ay = random.uniform(-0.1, 0.1)
        az = random.uniform(9.7, 9.9) # Gravitasi normal
        temp = random.uniform(40.0, 45.0)
        
    # Kondisi Warning (Vibrasi Meningkat)
    elif cycle_count < PHASE_WARNING_DURATION:
        # Vibrasi mulai tidak stabil
        ax = random.uniform(-1.5, 1.5)
        ay = random.uniform(-1.5, 1.5)
        az = random.uniform(8.0, 11.0)
        # Suhu mulai naik perlahan
        temp = random.uniform(45.0, 60.0)
        
    # Kondisi Fault (Vibrasi & Suhu Melebihi Threshold)
    else:
        # Vibrasi ekstrem (Melebihi vib_max: 2.0)
        ax = random.uniform(-3.0, 3.0)
        ay = random.uniform(-3.0, 3.0)
        az = random.uniform(5.0, 15.0)
        # Suhu overheat (Melebihi temp_max: 70.0)
        temp = random.uniform(70.0, 85.0)

    # Gyroscope (Simulasi putaran motor, naik saat anomali)
    base_gyro = 0.05 if cycle_count < PHASE_NORMAL_DURATION else 2.5
    gx = random.uniform(-base_gyro, base_gyro)
    gy = random.uniform(-base_gyro, base_gyro)
    gz = random.uniform(-base_gyro, base_gyro)
    
    # Humidity (Biasanya stabil di lingkungan pabrik)
    hum = random.uniform(50.0, 60.0)

    return {
        "motor_id": MOTOR_ID,
        "ax": round(ax, 4),
        "ay": round(ay, 4),
        "az": round(az, 4),
        "gx": round(gx, 4),
        "gy": round(gy, 4),
        "gz": round(gz, 4),
        "temp": round(temp, 2),
        "hum": round(hum, 2)
    }

def run_simulator():
    print(f"Memulai simulator IoT untuk {MOTOR_ID}...")
    print(f"Target URL: {SERVER_URL}")
    print("-" * 30)
    
    cycle = 0
    while True:
        # Generate data berdasarkan siklus saat ini
        payload = generate_telemetry(cycle)
        
        try:
            # Kirim HTTP POST Request
            response = requests.post(SERVER_URL, json=payload, timeout=60)
            
            # Cek status fase untuk logging
            if cycle < PHASE_NORMAL_DURATION:
                fase = "NORMAL"
            elif cycle < PHASE_WARNING_DURATION:
                fase = "WARNING"
            else:
                fase = "FAULT!"
                
            if response.status_code == 201:
                # print(f"Response: {response.status_code} | {response.text.strip()}")
                print(f"[{fase} Cycle {cycle}] Temp: {payload['temp']}°C | Hum: {payload['hum']}% | Vib(x,y,z): ({payload['ax']}, {payload['ay']}, {payload['az']}) | Gyro(x,y,z): ({payload['gx']}, {payload['gy']}, {payload['gz']})")
                print("-" * 50)
            else:
                print(f"[{fase}] Gagal! Status Code: {response.status_code} | Respon: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error Koneksi: {e}")
        
        # Increment cycle dan tunggu 1 detik
        cycle += 1
        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    run_simulator()