# Real-World Case Study: Bosch Industry

## Company Overview
Bosch (khususnya divisi Bosch IoT) adalah pionir dalam transformasi *smart manufacturing* tingkat global. Mereka bertugas memodernisasi peralatan dan lini produksi menjadi sistem yang saling terhubung (Industry 4.0).

## Specific Problem
Di dalam lini produksi pabrik, kerusakan motor industri yang terjadi tiba-tiba dapat menghentikan seluruh proses yang bernilai kerugian sangat tinggi. Mereka butuh cara untuk memonitor profil kesehatan motor, seperti getaran dan suhu isolasi, secara *real-time* berbasis IoT untuk implementasi **Predictive Maintenance**. Data sensor menghasilkan volume data *time-series* dalam jumlah raksasa setiap detiknya.

## Why NoSQL Document Store (MongoDB)?
Bosch dan banyak *engineer* IoT sering menjauhi Relational DB standar untuk kasus ini dan beralih menggunakan Document Store. Alasannya:
- **Schema Flexibility**: Setiap sensor dari pabrikan yang berbeda sering kali memuntahkan JSON yang berbeda-beda (*heterogeneous payload*). Merubah skema tabel terus-terusan di SQL sangat tidak lazim.
- **Bucket Pattern & Efficiency**: Jika 1 sensor menembakan 1 data tiap detik per motor, MySQL/Postgres harus meng-index ratusan ribu baris data individu setiap harinya. Dengan MongoDB, data dikelompokkan *(bucketing)* per 5 menit ke dalam sebuah Array dalam 1 Dokumen. Ini memangkas besar memori Index hingga 300 kali lipat, mencegah penumpukan I/O, dan mempercepat agregasi/tarikan analitik ke Fast Fourier Transform (FFT) karena algoritma cukup meload array secara leksikal.