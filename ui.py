# ui.py
import streamlit as st
from datetime import datetime, date, time
from engine_stress import hitung_stres_mingguan

st.set_page_config(page_title="Sistem Pengukuran Stres", layout="wide")
st.title("📘 Sistem Pengukuran Tingkat Stres Mahasiswa")

# Identitas
st.subheader("🧑‍🎓 Identitas Mahasiswa")
nama = st.text_input("Nama Mahasiswa")
nim = st.text_input("NIM Mahasiswa")

st.write("---")

minggu_type = st.selectbox("Pilih Tipe Minggu", ["Minggu Biasa", "Minggu E-Learning"])
st.write("---")

# MATKUL
mata_kuliah_opsi = [
    "Kecerdasan Buatan (3 SKS)",
    "Sistem Informasi Manajemen (2 SKS)",
    "Pengolahan Citra Digital (2 SKS)",
    "Teknik Riset Operasional (2 SKS)",
    "Pemrograman Web 1 (3 SKS)",
    "Metode Penelitian (3 SKS)",
    "Digital Entrepreneurship (2 SKS)",
    "Machine Learning (3 SKS)"
]

if "matkul_data" not in st.session_state:
    st.session_state.matkul_data = {
        mk: {
            "tugas": "Tidak",
            "kesulitan_tugas": 5,
            "deadline_tgl": date.today(),
            "deadline_jam": time(23, 59),

            "tugas_kelompok": "Tidak",
            "deadline_kelompok_tgl": date.today(),
            "deadline_kelompok_jam": time(23, 59),

            "kesulitan_kuliah": 5,

            "forum": "Tidak",
            "tugas_el": "Tidak",
            "deadline_el_tgl": date.today(),
            "deadline_el_jam": time(23, 59),
            "kesulitan_el": 5
        }
        for mk in mata_kuliah_opsi
    }

st.subheader("📚 Data Mata Kuliah")

for mk in mata_kuliah_opsi:
    st.write(f"### 📘 {mk}")
    d = st.session_state.matkul_data[mk]

    col1, col2 = st.columns(2)
    with col1:
        d["tugas"] = st.selectbox(f"Tugas ({mk})", ["Ada", "Tidak"], key=f"t_{mk}")
        d["kesulitan_tugas"] = st.slider(f"Kesulitan Tugas ({mk})", 1, 10, d["kesulitan_tugas"])

        if d["tugas"] == "Ada":
            d["deadline_tgl"] = st.date_input(f"Deadline Tanggal ({mk})", key=f"tgl_{mk}")
            d["deadline_jam"] = st.time_input(f"Deadline Jam ({mk})", key=f"jam_{mk}")

        d["tugas_kelompok"] = st.selectbox(f"Tugas Kelompok ({mk})", ["Ada", "Tidak"], key=f"kel_{mk}")
        if d["tugas_kelompok"] == "Ada":
            d["deadline_kelompok_tgl"] = st.date_input(f"DL Kelompok Tgl ({mk})", key=f"ktgl_{mk}")
            d["deadline_kelompok_jam"] = st.time_input(f"DL Kelompok Jam ({mk})", key=f"kjam_{mk}")

    with col2:
        d["kesulitan_kuliah"] = st.slider(f"Kesulitan Kuliah ({mk})", 1, 10, d["kesulitan_kuliah"])

        if minggu_type == "Minggu E-Learning":
            d["tugas_el"] = st.selectbox(f"Tugas E-Learning ({mk})", ["Ada", "Tidak"], key=f"el_{mk}")
            d["kesulitan_el"] = st.slider(f"Kesulitan EL ({mk})", 1, 10, d["kesulitan_el"])

            if d["tugas_el"] == "Ada":
                d["deadline_el_tgl"] = st.date_input(f"DL EL Tgl ({mk})", key=f"etgl_{mk}")
                d["deadline_el_jam"] = st.time_input(f"DL EL Jam ({mk})", key=f"ejam_{mk}")

    st.write("---")

# Jam tidur & kuliah
hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]

st.subheader("😴 Jam Tidur")
jam_tidur = {h: st.slider(f"Jam tidur {h}", 0.0, 12.0, 6.0) for h in hari}

st.subheader("📖 Jam Kuliah")
jam_kuliah = {h: st.slider(f"Jam kuliah {h}", 0.0, 12.0, 3.0) for h in hari}

# HITUNG
# Tombol simpan
if st.button("✔ Simpan dan Hitung Stres"):
    
    hasil = hitung_stres_mingguan(
        minggu_type,
        st.session_state.matkul_data,
        jam_tidur,
        jam_kuliah
    )

    skor_total = hasil['skor_total']

    # ======== KATEGORI TEKS BERDASARKAN SKOR ========
    if skor_total <= 30:
        kategori = "🟢 **Stres Rendah** — kamu berada di zona aman."
    elif skor_total <= 60:
        kategori = "🟡 **Stres Sedang** — tetap jaga manajemen waktu ya."
    else:
        kategori = "🔴 **Stres Tinggi** — segera atur ulang jadwal & istirahat."

    # ======== OUTPUT ========
    st.success("Perhitungan selesai! 🔥")

    st.write(f"## 🔥 Total Stres: **{skor_total:.2f} / 100**")
    st.write(f"### {kategori}")

    # Detail angka
    st.write("## 🧩 Detail Perhitungan")
    st.json(hasil["detail"])

    # ======== GRAFIK — PIE CHART ========
    import matplotlib.pyplot as plt

    labels = ['Beban Tugas', 'Kesulitan', 'Deadline', 'Tidur']
    values = [
        hasil["detail"]["beban_tugas"],
        hasil["detail"]["kesulitan_rata2"],
        hasil["detail"]["deadline_rata2_jam"],
        hasil["detail"]["tidur_rata2"]
    ]

    fig, ax = plt.subplots(figsize=(5,5))
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title("Kontribusi Stres Mingguan")

    st.pyplot(fig)

