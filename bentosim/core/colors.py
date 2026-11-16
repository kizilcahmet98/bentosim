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
    """Palet çiftini paylaşır; biçim bayraklarını renk numarasından ayırır."""
    fi, bi = rgb256(*fg), rgb256(*bg) if bg is not None else -1
    key = (fi, bi)
    if key not in _pair_cache:
        # Bazı curses sürümleri binlerce çift bildirirken color_pair() yalnızca
        # 8 bit ayırır: 256 ve üstü numaralar standout/reverse bitlerine taşar.
        limit = min(curses.COLOR_PAIRS - 1, curses.pair_number(curses.A_COLOR))
        pid = _pair_id[0]
        if pid <= limit:
            try:
                curses.init_pair(pid, fi, bi)
            except curses.error:
                curses.init_pair(pid, fi, curses.COLOR_BLACK)
            _pair_cache[key] = curses.color_pair(pid)
            _pair_id[0] += 1
        else:
            # Kullanımdaki çifti yeniden tanımlama: ekrandaki eski hücrelerin
            # rengi de değişir. Aynı arka planda en yakın mevcut rengi kullan.
            a = _closest_pair(fi, bi)
            if bold: a |= curses.A_BOLD
            if dim:  a |= curses.A_DIM
            return a
    a = _pair_cache[key]
    if bold: a |= curses.A_BOLD
    if dim:  a |= curses.A_DIM
    return a


def _palette_rgb(index):
    """rgb256() tarafından üretilen küp/gri palet rengini RGB'ye açar."""
    if index >= 232:
        return (8 + 10 * (index - 232),) * 3
    index -= 16
    levels = (0, 95, 135, 175, 215, 255)
    return tuple(levels[channel] for channel in
                 (index // 36, index // 6 % 6, index % 6))


def _closest_pair(fg, bg):
    target = _palette_rgb(fg)
    best_attr, best_distance = 0, float("inf")
    for (cached_fg, cached_bg), attr in _pair_cache.items():
        if cached_bg != bg:
            continue
        distance = sum((a - b) ** 2 for a, b in zip(target, _palette_rgb(cached_fg)))
        if distance < best_distance:
            best_attr, best_distance = attr, distance
    return best_attr


def blend(c1, c2, t):
    """İki RGB rengi arasında doğrusal interpolasyon."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def reset_color_cache():
    """Tema değişiminde çağrılır — cache ve pair sayacını sıfırlar."""
    _pair_cache.clear()
    _pair_id[0] = 1
