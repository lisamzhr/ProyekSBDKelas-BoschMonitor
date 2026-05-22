# Conceptual Data Model (Bucket Pattern)

## Database: `bosch_monitor`
## Collection: `buckets`

Model data ini berfokus pada **Bucket Pattern**, salah satu desain fundamental di Document Store (MongoDB) untuk kasus IoT. Daripada menyimpan ribuan baris/dokumen individual yang mewakili 1 pembacaan dari 1 detik, kita menyimpannya dalam bentuk susunan array per periode waktu (misal: 300 data untuk blok waktu 5 menit). Hal ini sangat disukai oleh *Data Scientist* karena data sudah dalam bentuk *batch* yang siap diproses untuk algoritma *rolling window* maupun kalkulasi FFT (Fast Fourier Transform).

### Structure Diagram
```json
{
  "_id": "MOTOR_01_2024-01-15T10:00:00",
  "motor_id": "MOTOR_01",
  "bucket_start": "ISODate('2024-01-15T10:00:00Z')",
  "is_closed": true,
  "count": 300,
  "measurements": [
    {
      "t": "ISODate('2024-01-15T10:00:01Z')",
      "ax": 0.12, "ay": -0.05, "az": 9.81,
      "gx": 0.02, "gy": 0.01, "gz": -0.04,
      "temp": 42.3, "hum": 55.4
    },
    // ... array dari ratusan measurement lainnya ...
  ],
  "stats": {
    "vib_rms": 0.145,
    "temp_avg": 42.1,
    "temp_max": 43.8
  }
}
```
*Note: Kolom `stats` dikalkulasi (pre-aggregated) otomatis oleh query MongoDB/Python tepat saat bucket ditutup ketika memuat item ke-300.*

---

## Collection: `motors` (Metadata)
Berfungsi mirip seperti tabel master, menjaga nilai limitasi komponen hardware dan properti lokasi statisnya.

### Structure Diagram
```json
{
  "_id": "MOTOR_01",
  "motor_id": "MOTOR_01",
  "location": "Line A - Station 3",
  "model": "Bosch Rexroth MSK071",
  "thresholds": {
    "vib_max": 2.0, 
    "temp_max": 70.0
  },
  "status": "normal"
}
```