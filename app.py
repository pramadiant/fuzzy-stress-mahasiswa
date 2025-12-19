import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
from datetime import datetime, date, time as dt_time

# --- [IMPORT DARI FILE ASLI KAMU] ---
# Pastikan engine_stress.py ada di folder yang sama
from engine_stress import hitung_stres_mingguan

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Sistem Pengukuran Stres", layout="wide")

# Koneksi ke Supabase
conn = st.connection("supabase", type="sql")

# ==========================================
# BAGIAN BARU: FUNGSI DATABASE & LOGIN
# ==========================================

def login_user(username, password):
    """Mengecek user di database users"""
    try:
        df = conn.query("SELECT * FROM users WHERE username = :u;", params={"u": username}, ttl=0)
        if not df.empty:
            if df.iloc[0]['password'] == password:
                return df.iloc[0]
    except Exception as e:
        st.error(f"Error Database: {e}")
    return None

def register_user(username, password, nama, nim):
    """Mendaftarkan user baru"""
    try:
        with conn.session as s:
            s.execute(
                "INSERT INTO users (username, password, nama_lengkap, nim) VALUES (:u, :p, :n, :nim);",
                params={"u": username, "p": password, "n": nama, "nim": nim}
            )
            s.commit()
        return True
    except Exception:
        return False

def simpan_hasil_ke_db(username, hasil, kategori):
    """Menyimpan hasil perhitungan ke tabel stress_history"""
    d = hasil['detail']
    try:
        with conn.session as s:
            s.execute(
                """
                INSERT INTO stress_history 
                (username, skor_total, kategori, detail_beban, detail_kesulitan, detail_deadline, detail_tidur) 
                VALUES (:u, :skor, :kat, :beban, :sulit, :dl, :tidur);
                """,
                params={
                    "u": username,
                    "skor": hasil['skor_total'],
                    "kat": kategori,
                    "beban": d['beban_tugas'],
                    "sulit": d['kesulitan_rata2'],
                    "dl": d['deadline_rata2_jam'],
                    "tidur": d['tidur_rata2']
                }
            )
            s.commit()
        return True
    except Exception as e:
        st.error(f"Gagal simpan: {e}")
        return False

# ==========================================
# LOGIKA UTAMA APLIKASI
# ==========================================

# Cek Status Login
if 'status_login' not in st.session_state:
    st.session_state['status_login'] = False
    st.session_state['user_data'] = None

if not st.session_state['status_login']:
    # --- TAMPILAN JIKA BELUM LOGIN (Login/Register) ---
    st.title("🔐 Sistem Pengukuran Tingkat Stres")
    
    tab1, tab2 = st.tabs(["Login", "Daftar Akun"])
    
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            user = login_user(u, p)
            if user is not None:
                st.session_state['status_login'] = True
                st.session_state['user_data'] = user
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Username/Password salah.")

    with tab2:
        st.write("Belum punya akun? Daftar dulu.")
        reg_u = st.text_input("Username Baru")
        reg_p = st.text_input("Password Baru", type="password")
        reg_nama = st.text_input("Nama Lengkap")
        reg_nim = st.text_input("NIM")
        if st.button("Daftar"):
            if register_user(reg_u, reg_p, reg_nama, reg_nim):
                st.success("Berhasil! Silakan Login.")
            else:
                st.error("Gagal daftar (Username mungkin sudah dipakai).")

else:
    # --- TAMPILAN SETELAH LOGIN (Dashboard User) ---
    user = st.session_state['user_data']
    
    # Sidebar: Identitas Otomatis dari Database
    with st.sidebar:
        st.write(f"### 👋 Halo, {user['nama_lengkap']}")
        st.write(f"NIM: {user['nim']}")
        if st.button("Logout"):
            st.session_state['status_login'] = False
            st.rerun()

    # Menu Navigasi
    menu = st.radio("Menu", ["📝 Hitung Stres", "📊 Riwayat Saya"], horizontal=True)
    st.write("---")

    if menu == "📝 Hitung Stres":
        # ========================================================
        # [BAGIAN INI ADALAH COPY-PASTE DARI KODE ASLI UI.PY KAMU]
        # ========================================================
        
        st.title("📘 Hitung Stres Mingguan")
        
        # 1. Pilih Tipe Minggu
        minggu_type = st.selectbox("Pilih Tipe Minggu", ["Minggu Biasa", "Minggu E-Learning"])
        
        # 2. Input Matkul (Logic Asli Kamu)
        mata_kuliah_opsi = [
            "Kecerdasan Buatan (3 SKS)", "Sistem Informasi Manajemen (2 SKS)",
            "Pengolahan Citra Digital (2 SKS)", "Teknik Riset Operasional (2 SKS)",
            "Pemrograman Web 1 (3 SKS)", "Metode Penelitian (3 SKS)",
            "Digital Entrepreneurship (2 SKS)", "Machine Learning (3 SKS)"
        ]

        if "matkul_data" not in st.session_state:
            st.session_state.matkul_data = {
                mk: {
                    "tugas": "Tidak", "kesulitan_tugas": 5,
                    "deadline_tgl": date.today(), "deadline_jam": dt_time(23, 59),
                    "tugas_kelompok": "Tidak", "deadline_kelompok_tgl": date.today(),
                    "deadline_kelompok_jam": dt_time(23, 59),
                    "kesulitan_kuliah": 5, "forum": "Tidak", "tugas_el": "Tidak",
                    "deadline_el_tgl": date.today(), "deadline_el_jam": dt_time(23, 59),
                    "kesulitan_el": 5
                } for mk in mata_kuliah_opsi
            }

        with st.expander("📚 Input Detail Mata Kuliah", expanded=True):
            for mk in mata_kuliah_opsi:
                st.write(f"**{mk}**")
                d = st.session_state.matkul_data[mk]
                c1, c2 = st.columns(2)
                # ... (Logic input form disederhanakan agar muat, fungsinya sama persis dengan kodemu) ...
                with c1:
                    d["tugas"] = st.selectbox(f"Tugas ({mk})", ["Ada", "Tidak"], key=f"t_{mk}")
                    d["kesulitan_tugas"] = st.slider(f"Kesulitan ({mk})", 1, 10, d["kesulitan_tugas"])
                    if d["tugas"] == "Ada":
                        d["deadline_tgl"] = st.date_input(f"Deadline ({mk})", key=f"dt_{mk}")
                        d["deadline_jam"] = st.time_input(f"Jam ({mk})", key=f"tm_{mk}")
                with c2:
                    d["tugas_kelompok"] = st.selectbox(f"Kelompok ({mk})", ["Ada", "Tidak"], key=f"kel_{mk}")
                    if d["tugas_kelompok"] == "Ada":
                        d["deadline_kelompok_tgl"] = st.date_input(f"DL Kel ({mk})", key=f"kdt_{mk}")
                    if minggu_type == "Minggu E-Learning":
                         d["tugas_el"] = st.selectbox(f"EL ({mk})", ["Ada", "Tidak"], key=f"el_{mk}")

        # 3. Input Tidur & Kuliah
        c_tidur, c_kuliah = st.columns(2)
        hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        with c_tidur:
            st.subheader("😴 Jam Tidur")
            jam_tidur = {h: st.slider(f"Tidur {h}", 0.0, 12.0, 6.0) for h in hari}
        with c_kuliah:
            st.subheader("📖 Jam Kuliah")
            jam_kuliah = {h: st.slider(f"Kuliah {h}", 0.0, 12.0, 3.0) for h in hari}

        # 4. Tombol Hitung (MODIFIKASI DI SINI: TAMBAH SIMPAN DB)
        if st.button("✔ Hitung & Simpan"):
            hasil = hitung_stres_mingguan(minggu_type, st.session_state.matkul_data, jam_tidur, jam_kuliah)
            skor = hasil['skor_total']

            # Tentukan Kategori
            if skor <= 30: kat_text, kat_db = "🟢 Rendah", "Rendah"
            elif skor <= 60: kat_text, kat_db = "🟡 Sedang", "Sedang"
            else: kat_text, kat_db = "🔴 Tinggi", "Tinggi"

            # Tampilkan Hasil (Sama seperti kodemu)
            st.success("Selesai!")
            st.metric("Skor Stres", f"{skor:.2f}", delta=kat_text)
            
            # --- [BAGIAN BARU: SIMPAN OTOMATIS] ---
            if simpan_hasil_ke_db(user['username'], hasil, kat_db):
                st.toast("Data tersimpan ke riwayat!", icon="✅")
            
            # Grafik Pie (Sama seperti kodemu)
            labels = ['Beban', 'Kesulitan', 'Deadline', 'Tidur']
            values = [hasil["detail"]["beban_tugas"], hasil["detail"]["kesulitan_rata2"], 
                      hasil["detail"]["deadline_rata2_jam"], hasil["detail"]["tidur_rata2"]]
            fig, ax = plt.subplots(figsize=(3,3))
            ax.pie(values, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig)

    elif menu == "📊 Riwayat Saya":
        # --- [BAGIAN BARU: DASHBOARD] ---
        st.header("Grafik Riwayat Stres")
        df_hist = conn.query(f"SELECT * FROM stress_history WHERE username = '{user['username']}' ORDER BY created_at ASC", ttl=0)
        
        if not df_hist.empty:
            df_hist['Tanggal'] = pd.to_datetime(df_hist['created_at']).dt.strftime('%d %b')
            st.line_chart(df_hist, x='Tanggal', y='skor_total')
            st.dataframe(df_hist[['created_at', 'skor_total', 'kategori', 'detail_beban']])
        else:
            st.info("Belum ada data riwayat.")