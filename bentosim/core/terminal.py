"""
Terminal yardımcı fonksiyonları — güvenli yazma, interpolasyon vs.
"""

import unicodedata
from functools import lru_cache


@lru_cache(maxsize=1024)
def _cell_width(ch):
    if unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def cell_width(text):
    """Tek satırlık metnin hücre genişliği; belirsiz genişlikler bir sayılır.

    Standart W/F karakterler iki, birleşen işaretler sıfır hücredir.
    Fonta özel emoji/ZWJ birleşimleri için tam grapheme çözümleyici değildir.
    """
    if text.isascii():
        return len(text)
    return sum(_cell_width(ch) for ch in text)


def clip_cells(text, width, start=0):
    """Hücre aralığını kırpar; yarım geniş glif ve sahipsiz aksan üretmez."""
    if width <= 0:
        return ""
    start = max(0, start)
    if text.isascii():
        return text[start:start + width]
    result = []
    position = used = 0
    keep_marks = False
    for ch in text:
        size = _cell_width(ch)
        if not size:
            if keep_marks:
                result.append(ch)
            continue
        end = position + size
        if end <= start:
            keep_marks = False
        elif position < start:
            # Sol kenarda yarım kalan glifin görünen hücresini boş bırak.
            padding = min(end - start, width)
            result.append(" " * padding)
            used += padding
            keep_marks = False
        else:
            if used + size > width:
                break
            result.append(ch)
            used += size
            keep_marks = True
        position = end
    return "".join(result)


def safeadd(win, y, x, txt, attr=0):
    """
    curses penceresine güvenli bir şekilde yazı ekler.

    Ekran sınırlarını aşan yazılar hücre genişliğine göre kırpılır,
    yan etkileri yutulur (resize sırasında çökmemek için).
    """
    if not txt:
        return
    H, W = win.getmaxyx()
    if y < 0 or y >= H:
        return
    if x >= W - 1:
        return
    start = max(0, -x)
    x = max(0, x)
    room = W - x - 1
    if room <= 0:
        return
    txt = clip_cells(txt, room, start)
    if not txt:
        return
    try:
        win.addstr(y, x, txt, attr)
    except Exception:
        pass


def lerp(a, b, t):
    """Doğrusal interpolasyon — a ile b arasında t (0..1)."""
    return a + (b - a) * t
