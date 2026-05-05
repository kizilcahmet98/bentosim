"""bentosim.aquarium.sim — ana simülasyon döngüsü."""

import curses
import random
import time

from ..core import reset_color_cache
from . import environment as env
from .entities import (
    Fish, Shark, Whale, Jellyfish, Turtle, Crab, Octopus,
    Eel, MantaRay, Bubble, BottomDecor,
)
from .themes import THEMES, THEME_NAMES
from .hud import draw_hud


def run_sim(stdscr, cfg):
    # Globalleri sıfırla — tema değiştiğinde / yeniden başlatıldığında
    env._sw_h = {}
    reset_color_cache()

    curses.curs_set(0)
    stdscr.nodelay(True)
    frame_ms = max(16, int(1000 / max(5, cfg.get("fps", 30))))
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass

    theme = THEMES[cfg.get("color_theme", "ocean")]
    rows, cols = stdscr.getmaxyx()
    spd = cfg.get("speed", 1.0)

    school_c = (cols//2, rows//2) if cfg.get("schooling") else None

    fishes  = [Fish(cols, rows, spd, theme, school_c)
               for _ in range(min(cfg.get("fish_count", 12), max(3, cols//9)))]
    sharks  = []; whales = []; jellies = []; turtles = []
    crabs   = []; octos = []; eels = []; mantas = []; bubbles = []
    bottom  = BottomDecor(cols, rows)
    env.init_seaweed(cols, rows)

    t = 0.0
    paused = False

    timers = {
        "fish":(40, 60),     "shark":(260, 560),  "whale":(700, 1500),
        "jelly":(70, 190),   "turtle":(160, 420), "crab":(90, 250),
        "octo":(200, 520),   "eel":(130, 350),    "manta":(220, 600),
    }
    cds = {k: random.randint(*v) for k, v in timers.items()}
    bub_cd = 0

    while True:
        t0 = time.monotonic()
        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27): return "quit"
        if key == ord(' '):                 paused = not paused
        if key in (ord('m'), ord('M')):     return "menu"

        # Anlık tema: 1-6
        for ki, tn in enumerate(THEME_NAMES, 1):
            if key == ord(str(ki)):
                cfg["color_theme"] = tn
                theme = THEMES[tn]
                reset_color_cache()
                curses.start_color()
                try: curses.use_default_colors()
                except curses.error: pass

        if key == ord('+') and cfg["fish_count"] < 28:
            cfg["fish_count"] += 1
        if key == ord('-') and cfg["fish_count"] > 2:
            cfg["fish_count"] -= 1
        if key == ord('f'):
            fps_opts = [15, 20, 30, 45, 60]
            cur = cfg.get("fps", 30)
            idx = fps_opts.index(cur) if cur in fps_opts else 2
            cfg["fps"] = fps_opts[(idx+1) % len(fps_opts)]
            frame_ms = max(16, int(1000/cfg["fps"]))

        new_r, new_c = stdscr.getmaxyx()
        if (new_r, new_c) != (rows, cols):
            rows, cols = new_r, new_c
            bottom = BottomDecor(cols, rows)
            env.init_seaweed(cols, rows)
            stdscr.clear()

        if paused:
            stats = {k: len(v) for k, v in
                     [("fish", fishes), ("shark", sharks), ("whale", whales),
                      ("jelly", jellies), ("turtle", turtles), ("crab", crabs),
                      ("octo", octos), ("eel", eels), ("manta", mantas), ("bubble", bubbles)]}
            draw_hud(stdscr, rows, cols, stats, t, theme, True, cfg)
            stdscr.refresh()
            time.sleep(0.08)
            continue

        stdscr.erase()

        # ── Çevre ──
        env.draw_water_bg(stdscr, rows, cols, t, theme)
        env.draw_surface(stdscr, t, cols, theme)
        if cfg.get("light_rays"):
            env.draw_light_rays(stdscr, rows, cols, t, theme)
        env.draw_seaweed(stdscr, rows, cols, t, theme)
        bottom.draw(stdscr, theme, t)
        env.draw_sand(stdscr, rows, cols, t, theme)

        # ── Güncelle & Çiz ──
        all_e = (fishes + sharks + whales + jellies + turtles +
                 crabs + octos + eels + mantas + bubbles)
        for e in all_e:
            if isinstance(e, Fish):
                e.update(t, rows, cols, spd, sharks)
            elif isinstance(e, Shark):
                e.update(t, rows, cols, spd, fishes)
            elif isinstance(e, Bubble):
                e.update(t, rows, cols, spd)
            else:
                e.update(t, rows, cols, spd)
            if not e.dead:
                e.draw(stdscr, theme, t)

        # Balina fıskiyesi
        for w in whales:
            for b in w.emit_spout():
                bubbles.append(b)

        # Balık & kaplumbağa kabarcıkları
        if cfg.get("bubbles"):
            bub_cd -= 1
            if bub_cd <= 0:
                srcs = [e for e in fishes + turtles if hasattr(e, "emit_bubble")]
                if srcs:
                    b = random.choice(srcs).emit_bubble()
                    if b: bubbles.append(b)
                bub_cd = random.randint(4, 12)
            bubbles = bubbles[-100:]

        # Temizle
        fishes  = [e for e in fishes  if not e.dead]
        sharks  = [e for e in sharks  if not e.dead]
        whales  = [e for e in whales  if not e.dead]
        jellies = [e for e in jellies if not e.dead]
        turtles = [e for e in turtles if not e.dead]
        crabs   = [e for e in crabs   if not e.dead]
        octos   = [e for e in octos   if not e.dead]
        eels    = [e for e in eels    if not e.dead]
        mantas  = [e for e in mantas  if not e.dead]
        bubbles = [e for e in bubbles if not e.dead]

        # Spawn
        spd = cfg.get("speed", 1.0)
        for name, (lo, hi) in timers.items():
            cds[name] -= 1
            if cds[name] > 0: continue
            cds[name] = random.randint(lo, hi)
            if name == "fish" and len(fishes) < cfg.get("fish_count", 12):
                fishes.append(Fish(cols, rows, spd, theme, school_c))
            elif name == "shark" and cfg.get("shark") and len(sharks) < 2:
                sharks.append(Shark(cols, rows, spd))
            elif name == "whale" and cfg.get("whale") and len(whales) < 1:
                whales.append(Whale(cols, rows, spd))
            elif name == "jelly" and cfg.get("jellyfish") and len(jellies) < 6:
                jellies.append(Jellyfish(cols, rows))
            elif name == "turtle" and cfg.get("turtle") and len(turtles) < 3:
                turtles.append(Turtle(cols, rows, spd))
            elif name == "crab" and cfg.get("crab") and len(crabs) < 4:
                crabs.append(Crab(cols, rows, spd))
            elif name == "octo" and cfg.get("octopus") and len(octos) < 2:
                octos.append(Octopus(cols, rows))
            elif name == "eel" and cfg.get("eel") and len(eels) < 3:
                eels.append(Eel(cols, rows, spd))
            elif name == "manta" and cfg.get("manta") and len(mantas) < 2:
                mantas.append(MantaRay(cols, rows, spd))

        # Schooling güncelle
        if cfg.get("schooling") and fishes:
            cx = sum(f.x for f in fishes) / len(fishes)
            cy = sum(f.base_y for f in fishes) / len(fishes)
            school_c = (cx, cy)
            for f in fishes:
                f.school_center = school_c

        stats = {k: len(v) for k, v in
                 [("fish", fishes), ("shark", sharks), ("whale", whales),
                  ("jelly", jellies), ("turtle", turtles), ("crab", crabs),
                  ("octo", octos), ("eel", eels), ("manta", mantas), ("bubble", bubbles)]}
        draw_hud(stdscr, rows, cols, stats, t, theme, False, cfg)
        stdscr.refresh()
        t += 0.05
        elapsed = time.monotonic() - t0
        sleep = frame_ms/1000 - elapsed
        if sleep > 0:
            time.sleep(sleep)
    return "quit"
