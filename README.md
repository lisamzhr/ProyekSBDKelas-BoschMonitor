# 🏭 Centralized Multi-Sensor Telemetry Engine — Industrial IoT
### Predictive Maintenance Prototype (Bosch Case Study)

> Platform analitik *end-to-end* untuk pemantauan kondisi motor industri secara *real-time*, mendeteksi anomali getaran dan suhu menggunakan pendekatan *Bucket Pattern*.

---

## 📖 Deskripsi Singkat

**Motor Telemetry Engine** adalah purwarupa sistem *Industrial Internet of Things* (IIoT) yang menyimulasikan pemantauan kesehatan mesin (seperti motor servo/hidrolik) di lini produksi pabrik. Sistem ini mengumpulkan data dari sensor *vibration* dan *temperature*, menyimpannya secara efisien untuk analisis deret waktu (*time-series*), dan menjalankan *pipeline* analitik (RMS, FFT, Z-Score) untuk mendeteksi potensi kerusakan (*bearing fault*, *overheat*) sebelum kegagalan sistem terjadi.

---

## 🛠️ Tech Stack

| Layer | Teknologi | Kegunaan Utama |
|---|---|---|
| **Hardware Simulation** | Wokwi | ESP32 DevKit, MPU-6050 (Vibrasi), DHT22 (Suhu) |
| **Backend API** | Python + Flask | Data ingestion, validasi skema, timestamping |
| **Database** | MongoDB | Penyimpanan *time-series* frekuensi tinggi |
| **Analytics Engine** | Pandas, NumPy, SciPy | Kalkulasi RMS, FFT Spectrum, deteksi anomali |
| **Frontend/Dashboard** | Streamlit | Visualisasi *real-time*, log anomali, *health score* |
| **Deployment** | Docker Compose | Orkestrasi *container* terpadu |

---

## 📁 Struktur Folder

```text
bosch-motor-monitor/
├── wokwi/                    # Simulasi Hardware (ESP32 + Sensor)
│   ├── diagram.json          # Rangkaian ESP32 + MPU-6050 + DHT22
│   └── sketch.ino            # Firmware ESP32 (Kirim JSON ke Flask API)
├── backend/                  # Data Ingestion & Analytics Pipeline
│   ├── app.py                # Flask API endpoint
│   ├── db.py                 # Koneksi & logika Bucket Pattern MongoDB
│   └── analytics.py          # Pipeline Pandas/NumPy/SciPy
├── frontend/                 # UI Dashboard
│   └── dashboard.py          # Streamlit app
├── docker-compose.yml        # Orkestrasi Flask, MongoDB, Streamlit
└── requirements.txt          # Dependensi Python
```

---

## ⚙️ Konfigurasi Environment Variables

Buat file `.env` di *root* direktori proyek dan isi dengan konfigurasi berikut:

```env
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=bosch_telemetry
MONGO_COLLECTION=motor_buckets

# Flask API
FLASK_APP=backend/app.py
FLASK_ENV=development
API_PORT=5000

# Streamlit App
STREAMLIT_SERVER_PORT=8501
```

> ⚠️ Pastikan file `.env` sudah dimasukkan ke dalam `.gitignore`.

---

## 🚀 Setup & Menjalankan Sistem

### Cara 1 — Menggunakan Docker (Direkomendasikan)
Cara termudah untuk menjalankan seluruh layanan (API, Database, Dashboard) secara serentak.

```bash
# Clone repositori
git clone [https://github.com/username/bosch-motor-monitor.git](https://github.com/username/bosch-motor-monitor.git)
cd bosch-motor-monitor

# Jalankan seluruh stack
docker-compose up --build
```

### Cara 2 — Menjalankan Lokal (Development)

**1. Jalankan MongoDB**
Pastikan MongoDB *server* sudah berjalan di sistem lokal Anda pada *port* standar `27017`.

**2. Setup Virtual Environment & Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # Untuk Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Jalankan Flask Backend**
```bash
python backend/app.py
# Server berjalan di http://localhost:5000
```

**4. Jalankan Streamlit Dashboard** (Buka terminal baru)
```bash
streamlit run frontend/dashboard.py
# Dashboard berjalan di http://localhost:8501
```

---

## 📡 API Endpoints

Base URL lokal: `http://localhost:5000/api/v1`

### 📥 Telemetry Ingestion

| Method | Endpoint | Deskripsi |
|---|---|---|
| POST | `/telemetry` | Menerima *payload* sensor dari ESP32/Wokwi |

**POST `/telemetry`**
```json
// Request Body dari ESP32
{
  "sensor_id": "MPU6050_01",
  "motor_id": "MOTOR_01",
  "ax": 0.12, "ay": 0.08, "az": 9.81,
  "gx": 0.02, "gy": 0.01, "gz": 0.00,
  "temp": 42.3,
  "hum": 61.2
}

// Response 201
{
  "status": "success",
  "message": "Data ingested to bucket"
}
```

### 📊 Health & Analytics

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/health/:motor_id` | Mengembalikan *health score* dan status terbaru |

**GET `/health/MOTOR_01`**
```json
// Response 200
{
  "motor_id": "MOTOR_01",
  "health_score": 85,
  "status": "WARNING",
  "latest_stats": {
    "vib_rms": 0.145,
    "temp_avg": 42.1
  }
}
```

---

## 🗄️ Skema Database (MongoDB Bucket Pattern)

Sistem dirancang untuk efisiensi pembacaan data historis dalam jumlah besar menggunakan *Bucket Pattern*. Alih-alih membuat satu dokumen untuk setiap pembacaan (1 Hz), sistem menampung ~300 pembacaan ke dalam satu dokumen per rentang 5 menit.

**Contoh Struktur Dokumen (`motor_buckets`):**
```json
{
  "_id": "MOTOR_01_2024-01-15T10:00:00",
  "sensor_id": "MPU6050_01",
  "motor_id": "MOTOR_01",
  "bucket_start": ISODate("2024-01-15T10:00:00Z"),
  "bucket_end": ISODate("2024-01-15T10:05:00Z"),
  "count": 300,
  "measurements": [
    {
      "t": ISODate("2024-01-15T10:00:01Z"),
      "ax": 0.12, "ay": 0.08, "az": 9.81,
      "temp": 42.3
    }
    // ... 299 data lainnya
  ],
  "stats": {
    "vib_rms": 0.145,
    "temp_avg": 42.1,
    "temp_max": 43.8
  }
}
```
*Keuntungan nyata: Mengkueri data 1 hari hanya membutuhkan pemindaian 288 dokumen, bukan 86.400 dokumen.*

---

## 🕹️ Simulasi Wokwi (Hardware)

*Firmware* di dalam folder `/wokwi` tidak hanya mengirimkan data statis, melainkan diprogram untuk menstimulasikan 3 fase pergerakan motor:
1. **Normal:** Getaran stabil, suhu normal.
2. **Warning:** Getaran meningkat perlahan (ditambahkan *noise* sinusoidal).
3. **Fault:** Suhu meningkat drastis dan getaran melewati ambang batas toleransi.

Untuk menjalankan, *copy* kode `sketch.ino` dan `diagram.json` ke *project* baru di [Wokwi](https://wokwi.com), dan pastikan ESP32 terhubung ke *endpoint* Flask Anda (menggunakan ngrok jika Flask berjalan lokal).

---

## 👥 Tim Pengembang

| Nama | Peran / Fokus |
|---|---|
| **Ferdyano** | Lead Backend (Flask API, MongoDB Bucket Schema) |
| **Khalisa Zahra Maulana** | Data Analytics (Z-score, FFT, RMS Pipeline) |
| **Muhammad Daffa Rizki** | Frontend Dashboard (Streamlit UI/UX) |
| **Sakabudi Muhammad** | Hardware Integration (Wokwi Firmware) |
| **Muhammad Rafif Batubara** | DevOps & Testing (Docker, Validation) |

---

## 📝 Catatan Pengembangan
* *Pipeline* kalkulasi (`stats` di MongoDB) dieksekusi secara otomatis setiap kali sebuah *bucket* ditutup (mencapai batas 300 *count* atau lewat batas waktu).
* Deteksi anomali menggunakan *Z-score* $(x - \mu) / \sigma$ dengan ambang batas $|Z| > 3$.
* Logika *health score* mengacu pada standar *Overall Health Index* (OHI).
