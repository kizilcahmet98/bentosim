"""
bentosim.aquarium.menu — tam ekran TUI menü.

[m] tuşuyla simülasyon içinden de açılabilir, ayrıca ``--menu``
flagıyla başta da gösterilebilir.
"""

import curses

from ..core import cp
from .themes import THEMES, THEME_NAMES
from .config import DEFAULT_CFG
from .art import (
    SHARK_R, WHALE_R, TURTLE_R, RAY_R, EEL_R,
    CRAB_R, OCTOPUS_FRAMES, JELLY_FRAMES,
)


# Canlı toggle'ları için önizleme: (art lines, tema renk anahtarı)
PREVIEW_ART = {
    "shark":     (SHARK_R,           "shark"),
    "whale":     (WHALE_R,           "whale"),
    "turtle":    (TURTLE_R,          "turtle"),
    "jellyfish": (JELLY_FRAMES[0],   "jelly"),
    "crab":      (CRAB_R[0],         "crab"),
    "octopus":   (OCTOPUS_FRAMES[0], "octo"),
    "eel":       (EEL_R,             "eel"),
    "manta":     (RAY_R,             "ray_fish"),
}


def draw_menu_frame(win, rows, cols, theme_name):
    win.erase()
    H, W = win.getmaxyx()
    border_attr = curses.A_BOLD
    win.addstr(0, 0, "╔"+"═"*(W-2)+"╗" if W > 2 else "", border_attr)
    win.addstr(H-2, 0, "╚"+"═"*(W-2)+"╝" if W > 2 else "", border_attr)
    for r in range(1, H-2):
        try:
            win.addstr(r, 0, "║")
            win.addstr(r, W-1, "║")
        except Exception:
            pass

    title = "B E N T O S I M  ·  A K V A R Y U M   v0.1"
    sub   = "Ayarlar & Yapılandırma"
    try:
        win.addstr(1, max(1, (W-len(title))//2), title, curses.A_BOLD)
        win.addstr(2, max(1, (W-len(sub))//2),   sub,   curses.A_DIM)
        sep_w = min(W-4, max(len(title), 30))
        win.addstr(3, max(1, (W-sep_w)//2), "─"*sep_w, curses.A_DIM)
    except curses.error:
        pass


def run_menu(stdscr, cfg):
    rows, cols = stdscr.getmaxyx()
    curses.curs_set(0)

    menu_items = [
        ("Renk Teması",   "color_theme",  THEME_NAMES,           "Görsel renk paleti"),
        ("Balık Sayısı",  "fish_count",   list(range(3, 30)),    "Maksimum balık sayısı"),
        ("Köpekbalığı",   "shark",        [True, False],         "Köpekbalığı etkin mi?"),
        ("Balina",        "whale",        [True, False],         "Balina etkin mi?"),
        ("Kaplumbağa",    "turtle",       [True, False],         "Kaplumbağa etkin mi?"),
        ("Denizanası",    "jellyfish",    [True, False],         "Denizanası etkin mi?"),
        ("Yengeç",        "crab",         [True, False],         "Yengeç etkin mi?"),
        ("Ahtapot",       "octopus",      [True, False],         "Ahtapot etkin mi?"),
        ("Yılan Balığı",  "eel",          [True, False],         "Yılan balığı etkin mi?"),
        ("Işın Balığı",   "manta",        [True, False],         "Manta ray etkin mi?"),
        ("Kabarcıklar",   "bubbles",      [True, False],         "Kabarcık animasyonu"),
        ("Işık Huzmeleri","light_rays",   [True, False],         "Yüzeyden inen ışık"),
        ("Hız Çarpanı",   "speed",        [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0],
                                                                 "Tüm canlıların hız çarpanı"),
        ("FPS Limiti",    "fps",          [15, 20, 30, 45, 60],  "Kare hızı (düşükse CPU tasarrufu)"),
        ("HUD Göster",    "hud",          [True, False],         "Bilgi çubuğunu göster"),
        ("Sürü Modu",     "schooling",    [True, False],         "Balıklar grup halinde yüzer"),
    ]

    sel = 0
    top = 0
    def val_str(k, v):
        if isinstance(v, bool): return "✓ Açık " if v else "✗ Kapalı"
        if k == "speed":        return f"{v:.1f}×"
        return str(v)

    while True:
        rows, cols = stdscr.getmaxyx()
        stdscr.erase()
        draw_menu_frame(stdscr, rows, cols, cfg.get("color_theme", "ocean"))

        panel_w = min(52, cols-4)
        start_r = 5
        list_h = max(1, rows - start_r - 4)

        # Seçili öğeyi pencereye sığdır
        if sel < top:
            top = sel
        elif sel >= top + list_h:
            top = sel - list_h + 1
        top = max(0, min(top, max(0, len(menu_items) - list_h)))

        end = min(len(menu_items), top + list_h)
        for di, i in enumerate(range(top, end)):
            label, key, opts, desc = menu_items[i]
            r = start_r + di
            val = val_str(key, cfg.get(key, opts[0]))
            is_sel = (i == sel)
            if is_sel:
                marker = "▶"
                la = curses.A_REVERSE | curses.A_BOLD
            else:
                marker = " "
                la = curses.A_NORMAL
            line = f" {marker} {label:<24} {val:<12}"
            try:
                stdscr.addstr(r, 2, line[:panel_w-2], la)
            except curses.error:
                pass

        # Daha fazla öğe varsa kaydırma göstergesi
        try:
            if top > 0:
                stdscr.addstr(start_r-1, panel_w-2, "▲", curses.A_DIM)
            if end < len(menu_items):
                stdscr.addstr(start_r+list_h, panel_w-2, "▼", curses.A_DIM)
        except curses.error:
            pass

        # Sağ panel — yalnızca sığarsa
        right_x = panel_w + 4
        box_w = 22
        if cols >= right_x + box_w + 1:
            _, key, opts, desc = menu_items[sel]
            try:
                stdscr.addstr(start_r-1, right_x, "┌"+"─"*(box_w-2)+"┐", curses.A_DIM)
                stdscr.addstr(start_r,   right_x, f"│ {'Açıklama:':<{box_w-4}} │", curses.A_DIM)
                words = desc.split()
                line_buf = ""
                rr = start_r + 1
                for w in words:
                    if len(line_buf)+len(w)+1 > box_w-4:
                        stdscr.addstr(rr, right_x, f"│ {line_buf:<{box_w-4}} │", curses.A_DIM)
                        line_buf = w; rr += 1
                    else:
                        line_buf = (line_buf+" "+w).strip()
                if line_buf:
                    stdscr.addstr(rr, right_x, f"│ {line_buf:<{box_w-4}} │", curses.A_DIM)
                    rr += 1
                stdscr.addstr(rr, right_x, f"│ {'':<{box_w-4}} │", curses.A_DIM); rr += 1
                stdscr.addstr(rr, right_x, f"│ {'Seçenekler:':<{box_w-4}} │", curses.A_DIM); rr += 1
                max_opts = max(1, rows - 4 - rr)
                visible = max(1, min(6, max_opts, len(opts)))
                cur_v = cfg.get(key, opts[0])
                try: cur_idx = opts.index(cur_v)
                except ValueError: cur_idx = 0
                o_top = max(0, min(cur_idx - visible // 2,
                                   len(opts) - visible))
                for vi in range(visible):
                    o = opts[o_top + vi]
                    mark = "▸ " if o == cur_v else "  "
                    indicator = " "
                    if vi == 0 and o_top > 0:                        indicator = "▲"
                    elif vi == visible-1 and o_top+visible < len(opts): indicator = "▼"
                    stdscr.addstr(rr, right_x,
                        f"│ {mark}{str(o):<{box_w-7}}{indicator} │",
                        curses.A_DIM)
                    rr += 1
                if rr < rows - 3:
                    stdscr.addstr(rr, right_x, "└"+"─"*(box_w-2)+"┘", curses.A_DIM)
                    rr += 1

                # Canlı toggle'ında ASCII önizleme
                if key in PREVIEW_ART:
                    art, theme_key = PREVIEW_ART[key]
                    if rr + 1 + len(art) <= rows - 3:
                        rr += 1
                        stdscr.addstr(rr, right_x, "Önizleme:", curses.A_BOLD)
                        rr += 1
                        theme = THEMES[cfg.get("color_theme", "ocean")]
                        col_attr = cp(theme[theme_key], bold=True)
                        avail_cols = max(1, cols - right_x - 1)
                        for line in art:
                            if rr >= rows - 3:
                                break
                            stdscr.addstr(rr, right_x, line[:avail_cols], col_attr)
                            rr += 1
            except curses.error:
                pass

        hints = " ↑↓ seç   ←→ değiştir   Enter/ESC başlat   r varsayılan "
        try:
            stdscr.addstr(rows-3, 2, hints[:cols-4], curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key in (27, 10, 13, ord('q'), ord('Q'), ord('m'), ord('M')):
            break
        elif key == ord('r'):
            cfg.update(DEFAULT_CFG.copy())
        elif key == curses.KEY_UP:
            sel = (sel - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            sel = (sel + 1) % len(menu_items)
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT):
            lbl, k, opts, _ = menu_items[sel]
            cur = cfg.get(k, opts[0])
            if cur in opts:
                idx = opts.index(cur)
                d = 1 if key == curses.KEY_RIGHT else -1
                cfg[k] = opts[(idx+d) % len(opts)]
            else:
                cfg[k] = opts[0]
    return cfg
