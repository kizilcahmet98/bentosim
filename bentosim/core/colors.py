"""
256-renk motoru — RGB → curses pair eşleştirmesi.

Tema değiştirilince ``reset_color_cache()`` çağrılmalıdır.
"""

import curses

_pair_cache: dict = {}
_pair_id = [1]


def rgb256(r, g, b) -> int:
    """RGB değerlerini xterm-256 paletine yuvarlar."""
    if r == g == b:
        if r < 8:   return 16
        if r > 248: return 231
        return round((r - 8) / 247 * 24) + 232
    return 16 + 36 * round(r/255*5) + 6 * round(g/255*5) + round(b/255*5)


def cp(fg, bg=None, bold=False, dim=False):
    """RGB tuple'ından curses attribute üretir, sonucu önbelleğe alır."""
    key = (fg, bg, bold, dim)
    if key in _pair_cache:
        return _pair_cache[key]
    pid = _pair_id[0]
    _pair_id[0] += 1
    if pid >= curses.COLOR_PAIRS:
        pid = ((pid - 1) % (curses.COLOR_PAIRS - 1)) + 1
    fi = rgb256(*fg)
    bi = rgb256(*bg) if bg else -1
    try:
        curses.init_pair(pid, fi, bi)
    except curses.error:
        curses.init_pair(pid, fi, curses.COLOR_BLACK)
    a = curses.color_pair(pid)
    if bold: a |= curses.A_BOLD
    if dim:  a |= curses.A_DIM
    _pair_cache[key] = a
    return a


def blend(c1, c2, t):
    """İki RGB rengi arasında doğrusal interpolasyon."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def reset_color_cache():
    """Tema değişiminde çağrılır — cache ve pair sayacını sıfırlar."""
    _pair_cache.clear()
    _pair_id[0] = 1
