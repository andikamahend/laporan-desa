import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'laporan_desa.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # Table Laporan Desa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            judul TEXT NOT NULL,
            kategori TEXT NOT NULL,
            lokasi TEXT NOT NULL,
            isi_laporan TEXT NOT NULL,
            status TEXT DEFAULT 'Menunggu Verifikasi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Cek apakah default admin sudah ada
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    admin_exists = cursor.fetchone()
    if not admin_exists:
        hashed_pw = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password, role, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@desaku.id', hashed_pw, 'admin', datetime.now(), datetime.now()))

    # Cek apakah sample warga sudah ada
    cursor.execute('SELECT * FROM users WHERE username = ?', ('warga_budi',))
    user_exists = cursor.fetchone()
    if not user_exists:
        hashed_pw = generate_password_hash('warga123')
        cursor.execute('''
            INSERT INTO users (username, email, password, role, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('warga_budi', 'budi@gmail.com', hashed_pw, 'user', datetime.now(), datetime.now()))
        user_id = cursor.lastrowid

        # Sample dummy reports
        cursor.execute('''
            INSERT INTO reports (user_id, judul, kategori, lokasi, isi_laporan, status)
            VALUES 
            (?, 'Lampu Jalan Rusak di RT 03', 'Infrastruktur', 'Jalan Mawar RT 03 / RW 01', 'Lampu penerangan jalan utama padam sejak 3 hari lalu, mohon perbaikan demi keamanan warga di malam hari.', 'Diproses'),
            (?, 'Saluran Air Tersumbat Sampah', 'Kebersihan', 'Depan Pos Ronda RW 02', 'Selokan meluap saat hujan deras karena tertumpuk sampah dan ranting pohon.', 'Selesai')
        ''', (user_id, user_id))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database SQLite laporan_desa.db berhasil diinisialisasi.")
