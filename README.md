# Centralized Multi-Sensor Telemetry Engine (Bosch IIoT Case Study)

## Project Member
- Khalisa Zahra M (2406425395)
- Muhammad Rafif (2406408836)
- M Daffa Rizki (2406402050)
- Ferdyano (2406353723)
- Sakabudi M (2406429683)

## Project Description

Pada pabrik modern, mesin-mesin menggunakan berbagai jenis sensor (vibrasi, suhu, kelembapan) yang menghasilkan payload JSON dengan struktur berbeda-beda setiap detiknya. Database relasional (SQL) tradisional seringkali kewalahan menghadapi heterogenitas skema ini dan besarnya volume data *time-series* (menyebabkan *overhead index* dan *bottleneck I/O*).

Proyek ini menyelesaikan tantangan tersebut dengan mengimplementasikan **MongoDB Bucket Pattern**. Alih-alih menyimpan satu dokumen baru untuk setiap pembacaan sensor, sistem mengelompokkan data berfrekuensi tinggi ke dalam sebuah "bucket" berdasarkan rentang waktu tertentu (contoh: 5 menit per *bucket*). 
 

**Key Features:**
- **Schema Flexibility:** Mampu menerima struktur payload yang dinamis dari berbagai jenis sensor tanpa memerlukan downtime untuk `ALTER TABLE`.
- **High-Throughput Ingestion:**  Menggunakan operation MongoDB `$push` dan `$inc` untuk write yang cepat.
- **Pre-Aggregation:** Menghitung statistik dasar (RMS, rata-rata, nilai maksimum) di level database saat sebuah bucket ditutup, sehingga data siap di-query.
- **Analytics Engine:** Mngintegrasi library Pandas dan SciPy untuk mendeteksi anomali (Z-Score) dan Fast Fourier Transform (FFT) untuk mengidentifikasi secara spesifik komponen motor mana yang rusak (misal: Rotor, Stator, Bearing)

---

Architecture Diagram

```mermaid
graph TD
    subgraph "Edge Device / Simulation"
        A[IoT Simulator<br/>simulator.py]
    end

    subgraph "Backend Server (Flask API)"
        B(Data Ingestion & Routing<br/>app.py)
        C(Analytics Engine<br/>analytics.py)
    end

    subgraph "Database Layer"
        D[(MongoDB<br/>Bucket Pattern)]
    end

    subgraph "Client / Frontend"
        E[Streamlit Dashboard / Postman]
    end

    A -- "POST /telemetry (JSON)" --> B
    B -- "Atomic $push & $inc" --> D
    
    E -- "GET /health (Quick Stats)" --> B
    B -- "Fetch Summary Stats" --> D

    E -- "GET /analytics (Deep ML)" --> B
    B -- "Fetch Raw Array" --> D
    D -. "Return Measurements" .-> B
    B -- "Pass DataFrame" --> C
    C -- "FFT & Z-Score Results" --> B
    B -- "Predictive Health Response" --> E
