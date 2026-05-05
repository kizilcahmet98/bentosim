"""
Terminal yardımcı fonksiyonları — güvenli yazma, interpolasyon vs.
"""


def safeadd(win, y, x, txt, attr=0):
    """
    curses penceresine güvenli bir şekilde yazı ekler.

    Ekran sınırlarını aşan yazılar otomatik olarak kırpılır,
    yan etkileri yutulur (resize sırasında çökmemek için).
    """
    if not txt:
        return
    H, W = win.getmaxyx()
    if y < 0 or y >= H:
        return
    if x >= W - 1:
        return
    if x < 0:
        txt = txt[-x:]
        x = 0
    if not txt:
        return
    room = W - x - 1
    if room <= 0:
        return
    try:
        win.addstr(y, x, txt[:room], attr)
    except Exception:
        pass


def lerp(a, b, t):
    """Doğrusal interpolasyon — a ile b arasında t (0..1)."""
    return a + (b - a) * t
