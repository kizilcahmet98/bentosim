"""
bentosim.aquarium.environment — çevre çizim fonksiyonları.

Su yüzeyi, ışık huzmeleri, deniz yosunu, kum, su efektleri.
Bu modül durumsuzdur (deniz yosunu konumları hariç — global cache).
"""

import math
import random

from ..core import cp, safeadd, blend


_sw_h: dict = {}


def init_seaweed(cols, rows):
    """Deniz yosunu konumları ve yükseklikleri rastgele üretir."""
    global _sw_h
    positions = [int(cols*f) for f in
                 [0.04, 0.11, 0.19, 0.28, 0.37, 0.47, 0.56, 0.65, 0.74, 0.83, 0.91, 0.97]]
    _sw_h = {px: random.randint(3, 8) for px in positions}


def draw_water_bg(win, rows, cols, t, theme):
    """Hafif su efekti — sadece birkaç satırda."""
    for row in [rows//3, rows//2, int(rows*0.65)]:
        c = blend(theme["mid_water"], theme["deep_water"], row/rows)
        attr = cp(tuple(int(x) for x in c), dim=True)
        line = "".join(["·" if math.sin(x*0.15+t*0.4+row*0.25) > 0.88 else " "
                        for x in range(cols-1)])
        safeadd(win, row, 0, line, attr)


def draw_surface(win, t, cols, theme):
    """Üstte iki katmanlı dalgalı su yüzeyi."""
    a1 = cp(theme["surface"], bold=True)
    a2 = cp(theme["surf2"])
    line = []
    for x in range(cols-1):
        v = (math.sin(x*0.17+t*1.7) + 0.4*math.sin(x*0.055+t*0.95) +
             0.2*math.sin(x*0.38+t*2.1))
        if v > 1.1:    line.append("≋")
        elif v > 0.5:  line.append("≈")
        elif v > -0.2: line.append("~")
        else:          line.append("─")
    safeadd(win, 1, 0, "".join(line), a1)
    line2 = []
    for x in range(cols-1):
        v = math.sin(x*0.12+t*1.1+0.8)
        line2.append("·" if v > 0.7 else " ")
    safeadd(win, 2, 0, "".join(line2), a2)


def draw_light_rays(win, rows, cols, t, theme):
    """Yüzeyden inen ışık huzmeleri (parça parça parıltı)."""
    attr = cp(theme["ray"], dim=True)
    positions = [int(cols*f) for f in [0.09, 0.23, 0.41, 0.59, 0.74, 0.88]]
    for px in positions:
        depth = int(rows*0.28 + math.sin(t*0.32+px*0.08)*rows*0.09)
        w_max = max(1, int(depth*0.07))
        for row in range(2, min(depth, rows-4)):
            fade = (1.0 - row/max(depth, 1))
            if random.random() < fade*0.10:
                safeadd(win, row, px, "│", attr)
            if row < depth//2 and random.random() < fade*0.06:
                for off in random.choices([-1, 1], [0.5, 0.5], k=random.randint(0, w_max)):
                    safeadd(win, row, px+off, "·", attr)


def draw_seaweed(win, rows, cols, t, theme):
    """Sallayan deniz yosunu — pozisyonlar global cache'te tutulur."""
    if not _sw_h:
        init_seaweed(cols, rows)
    at = cp(theme["plant"], bold=True)
    am = cp(theme["plant"])
    ad = cp(theme["plant2"], dim=True)
    for px, h in _sw_h.items():
        if px >= cols: continue
        for drow in range(h):
            row = rows-3-drow
            if row < 2: continue
            sway = math.sin(t*0.82+px*0.27+drow*0.95)
            ch = ")" if sway > 0.28 else ("(" if sway < -0.28 else "|")
            off = int(sway*1.4)
            a = at if drow == 0 else (am if drow < 3 else ad)
            safeadd(win, row, px+off, ch, a)


def draw_sand(win, rows, cols, t, theme):
    """Üç katmanlı kum: dalgalı çizgi + ▄ + █."""
    at = cp(theme["sand"])
    am = cp(theme["sand2"], bold=True)
    ab = cp(theme["sand3"], bold=True)
    ripple = []
    for x in range(cols-1):
        v = math.sin(x*0.19+t*0.20) + 0.45*math.sin(x*0.07+t*0.12)
        ripple.append("~" if v > 0.55 else ("." if v > -0.1 else "_"))
    safeadd(win, rows-3, 0, "".join(ripple), at)
    safeadd(win, rows-2, 0, "▄"*(cols-1), am)
    safeadd(win, rows-1, 0, "█"*(cols-1), ab)
