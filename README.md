# 🏛️ Proyek Web Laporan Desa

Aplikasi web sistem layanan aspirasi & pengaduan masyarakat desa dengan antarmuka modern (HTML & Tailwind CSS) serta penyimpanan data menggunakan **SQLite**.

---

## 🚀 Fitur Utama

1. **Autentikasi 2 Tampilan (Tabs)**:
   - **Login**: Menggunakan `username` dan `password`.
   - **Daftar (Register)**: Menggunakan `username`, `email`, dan `password`.
2. **2 Role Pengguna**:
   - **Role `admin`**: Akses khusus pengelola/aparat desa.
   - **Role `user`**: Akses warga masyarakat untuk menyampaikan aduan.
3. **Database SQLite (`laporan_desa.db`)**:
   - Tabel `users`: Menyimpan id, username, email, password ter-hash, role (`admin` / `user`), waktu pendaftaran, dan catatan terakhir berhasil login.
   - Tabel `reports`: Menyimpan id, relasi pelapor, judul aduan, kategori, lokasi, detail laporan, status pengerjaan, dan tanggal pembuatan.
4. **Beranda User (Warga)**:
   - Tampilan beranda awal desa yang informatif dan ramah pengguna.
   - Ringkasan statistik laporan desa.
   - Formulir pengajuan aduan baru.
   - Daftar riwayat pengaduan yang diajukan oleh pengguna terkait.
5. **Beranda Admin**:
   - Tampilan visual langsung untuk isi database SQLite.
   - Tab 1: **Database Pengguna (Tabel `users`)** yang menampilkan seluruh user yang terdaftar dan riwayat login.
   - Tab 2: **Database Laporan Warga (Tabel `reports`)** lengkap dengan fitur filter pencarian dan opsi pembaruan status laporan (Menunggu Verifikasi, Diproses, Selesai).

---

## 🔑 Akun Uji Coba (Bawaan Database)

| Role | Username | Password | Deskripsi |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Masuk ke Beranda Admin (Tampilan Database) |
| **User (Warga)** | `warga_budi` | `warga123` | Masuk ke Beranda Awal Warga (Portal Laporan) |

> Anda juga dapat langsung membuat akun baru melalui menu **Daftar** pada halaman web. Akun baru secara otomatis memiliki role **User**.

---

## 💻 Cara Menjalankan Proyek

Pastikan Python telah terpasang di komputer Anda.

1. Buka terminal / Command Prompt / PowerShell di folder proyek ini:
   ```bash
   cd C:\Users\ASUS\.gemini\antigravity\scratch\laporan-desa
   ```

2. Jalankan aplikasi web:
   ```bash
   python app.py
   ```

3. Buka browser dan akses alamat:
   ```
   http://127.0.0.1:5000
   ```

---

## 📂 Struktur File

```
laporan-desa/
│
├── app.py                     # Controller Flask & routing logika aplikasi
├── database.py                # Konfigurasi koneksi & inisialisasi tabel SQLite
├── laporan_desa.db            # File database SQLite lokal
├── README.md                  # Dokumentasi proyek
└── templates/                 # Tampilan Web (HTML)
    ├── auth.html              # Halaman Login & Daftar (2 Tampilan)
    ├── user_dashboard.html    # Beranda Warga (Beranda Awal Laporan Desa)
    └── admin_dashboard.html   # Beranda Admin (Tampilan Database SQLite)
```
