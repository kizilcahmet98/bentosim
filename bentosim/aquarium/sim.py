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
from .hud import draw_hud, hud_height
from .config import BOUNDS


class SimulationClock:
    """Çizim hızından bağımsız, saniyede 30 sabit simülasyon adımı."""

    STEP = 1.0 / 30

    def __init__(self, now):
        self.previous = now
        self.remainder = 0.0
        self.paused = False

    def advance(self, now, paused=False):
        elapsed = max(0.0, now - self.previous)
        self.previous = now
        was_paused = self.paused
        self.paused = paused
        if paused or was_paused:
            return 0
        self.remainder += elapsed
        steps = int((self.remainder + 1e-9) / self.STEP)
        self.remainder = max(0.0, self.remainder - steps * self.STEP)
        return steps


def run_sim(stdscr, cfg, debug_whales=0):
    # Globalleri sıfırla — tema değiştiğinde / yeniden başlatıldığında
    env._sw_h = {}
    reset_color_cache()

    curses.curs_set(0)
    stdscr.nodelay(True)
    frame_seconds = 1.0 / max(5, cfg.get("fps", 30))
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass

    theme = THEMES[cfg.get("color_theme", "realistic")]
    rows, cols = stdscr.getmaxyx()
    water_top = max(1, hud_height(rows, cfg.get("hud", True))) + 2
    spd = cfg.get("speed", 1.0)

    school_c = (cols//2, rows//2) if cfg.get("schooling") else None

    fishes  = [Fish(cols, rows, spd, theme, school_c)
               for _ in range(min(cfg.get("fish_count", 12), max(3, cols//9)))]
    sharks  = []; whales = []; jellies = []; turtles = []
    crabs   = []; octos = []; eels = []; mantas = []; bubbles = []
    bottom  = BottomDecor(cols, rows, water_top=water_top)
    env.init_seaweed(cols, rows)

    # Yalnızca bu çalıştırma için: balinalar ilk karede suyun içinde görünür.
    for index in range(debug_whales):
        whale = Whale(cols, rows, spd)
        nose = whale.right_edge - 1 if whale.right else whale.left_edge
        whale.x = max(0, cols - 2) * (index + 1) / (debug_whales + 1) - nose
        max_y = max(water_top, rows - 3 - whale.H)
        whale.base_y = water_top + (max_y - water_top) * index / max(1, debug_whales - 1)
        whale.y = whale.base_y
        whales.append(whale)

    t = 0.0
    paused = False

    timers = {
        "fish":(40, 60),     "shark":(260, 560),  "whale":(700, 1500),
        "jelly":(70, 190),   "turtle":(160, 420), "crab":(90, 250),
        "octo":(200, 520),   "eel":(130, 350),    "manta":(220, 600),
    }
    cds = {k: random.randint(*v) for k, v in timers.items()}
    bub_cd = 0
    ticks = 0
    clock = SimulationClock(time.monotonic())

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
                for f in fishes:
                    f.retheme(theme)
                reset_color_cache()
                curses.start_color()
                try: curses.use_default_colors()
                except curses.error: pass

        if key == ord('+') and cfg["fish_count"] < BOUNDS["fish_count"][1]:
            cfg["fish_count"] += 1
        if key == ord('-') and cfg["fish_count"] > BOUNDS["fish_count"][0]:
            cfg["fish_count"] -= 1
            fishes = fishes[:cfg["fish_count"]]
        if key == ord('f'):
            fps_opts = [15, 20, 30, 45, 60]
            cur = cfg.get("fps", 30)
            idx = fps_opts.index(cur) if cur in fps_opts else 2
            cfg["fps"] = fps_opts[(idx+1) % len(fps_opts)]
            frame_seconds = 1.0 / cfg["fps"]

        new_r, new_c = stdscr.getmaxyx()
        if (new_r, new_c) != (rows, cols):
            rows, cols = new_r, new_c
            water_top = max(1, hud_height(rows, cfg.get("hud", True))) + 2
            bottom = BottomDecor(cols, rows, water_top=water_top)
            env.init_seaweed(cols, rows)
            stdscr.clear()

        for _ in range(clock.advance(t0, paused)):
            # Hareket, AI, ömür ve doğma sayaçları aynı sabit adımla ilerler.
            all_e = (fishes + sharks + whales + jellies + turtles +
                     crabs + octos + eels + mantas + bubbles)
            for e in all_e:
                if isinstance(e, Fish):
                    e.update(t, rows, cols, spd, sharks)
                elif isinstance(e, Shark):
                    e.update(t, rows, cols, spd, fishes)
                else:
                    e.update(t, rows, cols, spd)

            # Balina, balık ve kaplumbağa kabarcıkları
            if cfg.get("bubbles"):
                for w in whales:
                    bubbles.extend(w.emit_spout())
                bub_cd -= 1
                if bub_cd <= 0:
                    srcs = [e for e in fishes + turtles if hasattr(e, "emit_bubble")]
                    if srcs:
                        b = random.choice(srcs).emit_bubble()
                        if b: bubbles.append(b)
                    bub_cd = random.randint(4, 12)
                bubbles = bubbles[-100:]

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

            if cfg.get("schooling") and fishes:
                cx = sum(f.x for f in fishes) / len(fishes)
                cy = sum(f.base_y for f in fishes) / len(fishes)
                school_c = (cx, cy)
                for f in fishes:
                    f.school_center = school_c
            ticks += 1
            t = ticks * clock.STEP

        # Çizim FPS'e bağlıdır; simülasyon durumunu değiştirmez.
        stdscr.erase()
        env.draw_water_bg(stdscr, rows, cols, t, theme)
        env.draw_surface(stdscr, t, cols, theme,
                         top=max(1, hud_height(rows, cfg.get("hud", True))))
        if cfg.get("light_rays"):
            env.draw_light_rays(stdscr, rows, cols, t, theme)
        env.draw_seaweed(stdscr, rows, cols, t, theme, top=water_top)
        bottom.draw(stdscr, theme, t)
        env.draw_sand(stdscr, rows, cols, t, theme)
        for e in (fishes + sharks + whales + jellies + turtles +
                  crabs + octos + eels + mantas + bubbles):
            e.draw(stdscr, theme, t)

        stats = {k: len(v) for k, v in
                 [("fish", fishes), ("shark", sharks), ("whale", whales),
                  ("jelly", jellies), ("turtle", turtles), ("crab", crabs),
                  ("octo", octos), ("eel", eels), ("manta", mantas), ("bubble", bubbles)]}
        draw_hud(stdscr, rows, cols, stats, t, theme, paused, cfg)
        stdscr.refresh()
        elapsed = time.monotonic() - t0
        sleep = (0.08 if paused else frame_seconds) - elapsed
        if sleep > 0:
            time.sleep(sleep)
    return "quit"
