# engine_stress.py
import numpy as np
from engine_utils import hitung_selisih_deadline, skala_boolean, normalisasi

class FuzzyStressTsukamoto:

    def __init__(self):

        # Membership function input
        self.inputs = {
            "beban_tugas": {
                "rendah": [0, 0, 2, 4],
                "sedang": [3, 5, 7],
                "tinggi": [6, 8, 10, 10]
            },
            "kesulitan": {
                "rendah": [0, 0, 3, 5],
                "sedang": [4, 6, 8],
                "tinggi": [7, 9, 10, 10]
            },
            "deadline": {
                "longgar": [48, 72, 96, 120],
                "sedang": [24, 48, 72],
                "mefet": [0, 0, 12, 24]
            },
            "jam_tidur": {
                "cukup": [6, 7, 8, 9],
                "kurang": [0, 0, 5, 6]
            }
        }

        # Output Tsukamoto (monoton)
        self.output = {
            "stres_rendah": 25,
            "stres_sedang": 50,
            "stres_tinggi": 75
        }

        # Rules final dan valid semuanya
        self.rules = [
            ("beban_tugas", "rendah", "kesulitan", "rendah", "stres_rendah"),
            ("beban_tugas", "rendah", "kesulitan", "sedang", "stres_sedang"),

            ("beban_tugas", "sedang", "kesulitan", "tinggi", "stres_tinggi"),
            ("beban_tugas", "tinggi", "kesulitan", "tinggi", "stres_tinggi"),

            ("deadline", "mefet", "kesulitan", "sedang", "stres_tinggi"),
            ("deadline", "sedang", "kesulitan", "rendah", "stres_sedang"),

            ("jam_tidur", "kurang", "kesulitan", "tinggi", "stres_tinggi"),
            ("jam_tidur", "cukup", "kesulitan", "rendah", "stres_rendah")
        ]

    # ==========================
    # MEMBERSHIP FUNCTIONS FIX
    # ==========================

    def trapmf(self, x, p):
        a, b, c, d = p
        # Lindungi dari pembagian nol
        if b == a:
            left = 1 if x <= b else 0
        else:
            left = (x - a) / (b - a)

        if d == c:
            right = 1 if x >= c else 0
        else:
            right = (d - x) / (d - c)

        return max(min(left, 1, right), 0)

    def trimf(self, x, p):
        a, b, c = p
        if b == a:
            left = 1 if x == a else 0
        else:
            left = (x - a) / (b - a)

        if c == b:
            right = 1 if x == b else 0
        else:
            right = (c - x) / (c - b)

        return max(min(left, right), 0)

    def fuzzify(self, x, mf):
        return self.trapmf(x, mf) if len(mf) == 4 else self.trimf(x, mf)

    # ==========================
    #      HITUNG STRES
    # ==========================

    def hitung_stres(self, total_beban, total_kesulitan, deadline_avg, jam_tidur_avg):

        data = {
            "beban_tugas": total_beban,
            "kesulitan": total_kesulitan,
            "deadline": deadline_avg,
            "jam_tidur": jam_tidur_avg
        }

        alpha, z = [], []

        for v1, s1, v2, s2, out in self.rules:
            μ1 = self.fuzzify(data[v1], self.inputs[v1][s1])
            μ2 = self.fuzzify(data[v2], self.inputs[v2][s2])
            a = min(μ1, μ2)

            alpha.append(a)
            z.append(self.output[out])

        if sum(alpha) == 0:
            return 50

        return sum(a * zi for a, zi in zip(alpha, z)) / sum(alpha)


# =====================================================
#        ENGINE UNTUK UI (FINAL)
# =====================================================

def hitung_stres_mingguan(minggu_type, matkul_data, jam_tidur, jam_kuliah):

    total_beban = 0
    total_kesulitan = 0
    total_deadline = 0

    for mk, d in matkul_data.items():

        if d["tugas"] == "Ada":
            total_beban += 1
            total_deadline += hitung_selisih_deadline(d["deadline_tgl"], d["deadline_jam"])

        if d["tugas_kelompok"] == "Ada":
            total_beban += 1
            total_deadline += hitung_selisih_deadline(d["deadline_kelompok_tgl"], d["deadline_kelompok_jam"])

        total_kesulitan += d["kesulitan_tugas"]

        if minggu_type == "Minggu E-Learning":
            total_kesulitan += d["kesulitan_el"]

    avg_deadline = total_deadline / max(1, total_beban)
    avg_kesulitan = total_kesulitan / len(matkul_data)

    avg_tidur = sum(jam_tidur.values()) / 5

    engine = FuzzyStressTsukamoto()
    skor = engine.hitung_stres(total_beban, avg_kesulitan, avg_deadline, avg_tidur)

    return {
        "skor_total": skor,
        "detail": {
            "beban_tugas": total_beban,
            "kesulitan_rata2": avg_kesulitan,
            "deadline_rata2_jam": avg_deadline,
            "tidur_rata2": avg_tidur
        }
    }
