# engine_utils.py
from datetime import datetime

def skala_boolean(value: str) -> int:
    """Ada/Tidak -> 1/0"""
    return 1 if value == "Ada" else 0

def hitung_selisih_deadline(tanggal, jam):
    """Jam menuju deadline"""
    if not tanggal or not jam:
        return 0
    deadline = datetime.combine(tanggal, jam)
    now = datetime.now()
    selisih = (deadline - now).total_seconds() / 3600
    return max(selisih, 0)

def normalisasi(x, xmin, xmax):
    if xmax == xmin:
        return 0
    return max(0, min(1, (x - xmin) / (xmax - xmin)))
