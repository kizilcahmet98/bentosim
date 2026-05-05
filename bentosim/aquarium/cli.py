"""bentosim.aquarium.cli — komut satırı girişi (argparse)."""

import argparse
import curses

from .config import load_cfg, save_cfg, DEFAULT_CFG
from .menu import run_menu
from .sim import run_sim
from .themes import THEME_NAMES


def _curses_main(stdscr, cfg, start_menu):
    if start_menu:
        cfg = run_menu(stdscr, cfg)
    while True:
        r = run_sim(stdscr, cfg)
        if r == "menu":
            cfg = run_menu(stdscr, cfg)
            save_cfg(cfg)
        else:
            break


def run(argv=None):
    p = argparse.ArgumentParser(
        prog="bentosim aquarium",
        description="Bentosim — Terminal Akvaryumu",
    )
    p.add_argument("--menu",   action="store_true", help="Açılışta menüyü göster")
    p.add_argument("--theme",  choices=THEME_NAMES, help="Renk teması")
    p.add_argument("--fish",   type=int, help="Maksimum balık sayısı")
    p.add_argument("--fps",    type=int, help="FPS limiti (5-60)")
    p.add_argument("--speed",  type=float, help="Hız çarpanı (0.1-5.0)")
    p.add_argument("--reset",  action="store_true", help="Yapılandırmayı sıfırla")
    args = p.parse_args(argv)

    cfg = load_cfg()
    if args.reset:        cfg = DEFAULT_CFG.copy()
    if args.theme:        cfg["color_theme"] = args.theme
    if args.fish:         cfg["fish_count"]  = max(1, min(28, args.fish))
    if args.fps:          cfg["fps"]         = max(5, min(60, args.fps))
    if args.speed:        cfg["speed"]       = max(0.1, min(5.0, args.speed))

    try:
        curses.wrapper(_curses_main, cfg, args.menu)
    except KeyboardInterrupt:
        pass
    print("\n🐠  Güle güle, akvaryum!")


if __name__ == "__main__":
    run()
