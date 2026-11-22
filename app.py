from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = 'laporan_desa_secret_key_rahasia_123'

# Inisialisasi DB saat aplikasi dijalankan
init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    mode = request.args.get('mode', 'login')
    return render_template('auth.html', mode=mode)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash('Username dan password wajib diisi!', 'danger')
        return redirect(url_for('auth', mode='login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if user and check_password_hash(user['password'], password):
        # Update last_login
        now = datetime.now()
        conn.execute('UPDATE users SET last_login = ? WHERE id = ?', (now, user['id']))
        conn.commit()
        conn.close()

        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']

        flash(f'Selamat datang kembali, {user["username"]}!', 'success')
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    else:
        conn.close()
        flash('Username atau password salah. Silakan coba lagi.', 'danger')
        return redirect(url_for('auth', mode='login'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not email or not password:
        flash('Semua kolom (Username, Email, Password) wajib diisi!', 'danger')
        return redirect(url_for('auth', mode='daftar'))

    if len(password) < 6:
        flash('Password minimal harus 6 karakter!', 'warning')
        return redirect(url_for('auth', mode='daftar'))

    conn = get_db_connection()
    # Periksa apakah username atau email sudah terdaftar
    existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
    if existing_user:
        conn.close()
        flash('Username atau Email sudah terdaftar! Silakan gunakan yang lain.', 'warning')
        return redirect(url_for('auth', mode='daftar'))

    hashed_pw = generate_password_hash(password)
    try:
        conn.execute('''
            INSERT INTO users (username, email, password, role, created_at, last_login)
            VALUES (?, ?, ?, 'user', ?, ?)
        ''', (username, email, hashed_pw, datetime.now(), datetime.now()))
        conn.commit()
        
        # Ambil user yang baru dibuat untuk langsung auto login
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']

        flash('Pendaftaran akun berhasil! Selamat datang di Portal Laporan Desa.', 'success')
        return redirect(url_for('user_dashboard'))
    except Exception as e:
        conn.close()
        flash(f'Terjadi kesalahan saat pendaftaran: {str(e)}', 'danger')
        return redirect(url_for('auth', mode='daftar'))

@app.route('/beranda')
def user_dashboard():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu untuk mengakses Beranda.', 'info')
        return redirect(url_for('auth', mode='login'))

    conn = get_db_connection()
    # Ambil laporan milik user saat ini
    my_reports = conn.execute('''
        SELECT * FROM reports 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()

    # Statistik laporan desa secara umum
    total_laporan = conn.execute('SELECT COUNT(*) as count FROM reports').fetchone()['count']
    laporan_selesai = conn.execute('SELECT COUNT(*) as count FROM reports WHERE status = "Selesai"').fetchone()['count']
    laporan_proses = conn.execute('SELECT COUNT(*) as count FROM reports WHERE status = "Diproses"').fetchone()['count']
    conn.close()

    return render_template('user_dashboard.html', 
                           my_reports=my_reports, 
                           total_laporan=total_laporan,
                           laporan_selesai=laporan_selesai,
                           laporan_proses=laporan_proses)

@app.route('/laporan/baru', methods=['POST'])
def submit_report():
    if 'user_id' not in session:
        return redirect(url_for('auth', mode='login'))

    judul = request.form.get('judul', '').strip()
    kategori = request.form.get('kategori', '').strip()
    lokasi = request.form.get('lokasi', '').strip()
    isi_laporan = request.form.get('isi_laporan', '').strip()

    if not judul or not kategori or not lokasi or not isi_laporan:
        flash('Seluruh kolom formulir laporan wajib dilengkapi!', 'warning')
        return redirect(url_for('user_dashboard'))

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO reports (user_id, judul, kategori, lokasi, isi_laporan, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'Menunggu Verifikasi', ?)
    ''', (session['user_id'], judul, kategori, lokasi, isi_laporan, datetime.now()))
    conn.commit()
    conn.close()

    flash('Laporan warga berhasil dikirim! Petugas desa akan segera menindaklanjuti.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('auth', mode='login'))
    
    if session.get('role') != 'admin':
        flash('Akses ditolak! Halaman ini hanya untuk Administrator Desa.', 'danger')
        return redirect(url_for('user_dashboard'))

    conn = get_db_connection()
    # Tampilkan seluruh database pengguna yang berhasil terdaftar / login
    users = conn.execute('''
        SELECT id, username, email, role, created_at, last_login 
        FROM users 
        ORDER BY id ASC
    ''').fetchall()

    # Tampilkan seluruh database laporan masyarakat desa
    reports = conn.execute('''
        SELECT r.*, u.username, u.email 
        FROM reports r
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC
    ''').fetchall()

    # Statistik database
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_admins = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "admin"').fetchone()['count']
    total_warga = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "user"').fetchone()['count']
    total_reports = conn.execute('SELECT COUNT(*) as count FROM reports').fetchone()['count']
    
    conn.close()

    return render_template('admin_dashboard.html', 
                           users=users, 
                           reports=reports,
                           total_users=total_users,
                           total_admins=total_admins,
                           total_warga=total_warga,
                           total_reports=total_reports)

@app.route('/admin/laporan/update_status', methods=['POST'])
def update_status():
    if session.get('role') != 'admin':
        flash('Aksi tidak diizinkan.', 'danger')
        return redirect(url_for('auth'))

    report_id = request.form.get('report_id')
    new_status = request.form.get('status')

    if report_id and new_status:
        conn = get_db_connection()
        conn.execute('UPDATE reports SET status = ? WHERE id = ?', (new_status, report_id))
        conn.commit()
        conn.close()
        flash(f'Status laporan #{report_id} berhasil diubah menjadi: {new_status}', 'success')

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar (logout).', 'info')
    return redirect(url_for('auth', mode='login'))

if __name__ == '__main__':
    print("Server Laporan Desa berjalan di http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
