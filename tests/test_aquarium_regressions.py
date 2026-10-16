import random
import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.aquarium import cli, sim
from bentosim.core import rgb256
from bentosim.aquarium.config import DEFAULT_CFG, normalize_cfg
from bentosim.aquarium.entities import BottomDecor, Bubble, Fish, Whale, draw_art_opaque
from bentosim.aquarium.themes import THEMES, THEME_NAMES


class ConfigNormalizationTests(unittest.TestCase):
    def test_invalid_values_fall_back_or_clamp(self):
        cfg = normalize_cfg({
            "color_theme": "missing",
            "fish_count": "999",
            "fps": "1",
            "speed": "bad",
            "shark": "yes",
        })

        self.assertEqual(cfg["color_theme"], DEFAULT_CFG["color_theme"])
        self.assertIn(DEFAULT_CFG["color_theme"], THEME_NAMES)
        self.assertEqual(cfg["fish_count"], 28)
        self.assertEqual(cfg["fps"], 5)
        self.assertEqual(cfg["speed"], DEFAULT_CFG["speed"])
        self.assertEqual(cfg["shark"], DEFAULT_CFG["shark"])


class MenuInputTests(unittest.TestCase):
    def test_menu_waits_for_input_and_simulation_resumes_nonblocking(self):
        for start_menu in (False, True):
            for size in ((12, 40), (24, 80)):
                with self.subTest(start_menu=start_menu, size=size):
                    win = mock.MagicMock()
                    win.getmaxyx.return_value = size
                    input_mode = {"nonblocking": False}
                    reads = []
                    keys = []
                    if start_menu:
                        keys.extend([cli.curses.KEY_RIGHT, 10])
                    keys.extend([ord("m"), cli.curses.KEY_RIGHT, 10, ord("q")])
                    key_iter = iter(keys)

                    def set_mode(nonblocking):
                        input_mode["nonblocking"] = nonblocking

                    def read_key():
                        key = next(key_iter)
                        reads.append((key, input_mode["nonblocking"]))
                        return key

                    win.nodelay.side_effect = set_mode
                    win.getch.side_effect = read_key
                    cfg = DEFAULT_CFG.copy()
                    with mock.patch.object(cli.curses, "curs_set"), \
                            mock.patch.object(cli.curses, "start_color"), \
                            mock.patch.object(cli.curses, "use_default_colors"), \
                            mock.patch.object(cli, "save_cfg") as save_cfg:
                        cli._curses_main(win, cfg, start_menu)

                    for key, nonblocking in reads:
                        self.assertEqual(nonblocking, key in (ord("m"), ord("q")))
                    self.assertEqual(len(reads), len(keys))
                    self.assertEqual(save_cfg.call_count, 2 if start_menu else 1)
                    theme_changes = 2 if start_menu else 1
                    self.assertEqual(cfg["color_theme"], THEME_NAMES[theme_changes])


class BubbleSettingTests(unittest.TestCase):
    def test_whale_spout_respects_bubble_setting(self):
        for enabled in (False, True):
            with self.subTest(bubbles=enabled):
                cfg = DEFAULT_CFG.copy()
                cfg["bubbles"] = enabled
                cfg["fish_count"] = 1
                whale = Whale(80, 24, 1.0)
                whale.spout_cd = 1
                win = mock.MagicMock()
                win.getmaxyx.return_value = (24, 80)
                win.getch.side_effect = [-1, -1, ord("q")]

                def spawn_delay(lo, hi):
                    return 1 if (lo, hi) == (700, 1500) else hi

                with ExitStack() as stack:
                    for name in ("curs_set", "start_color", "use_default_colors"):
                        stack.enter_context(mock.patch.object(sim.curses, name))
                    stack.enter_context(mock.patch.object(sim, "env"))
                    stack.enter_context(mock.patch.object(sim, "BottomDecor"))
                    stack.enter_context(mock.patch.object(sim, "Whale", return_value=whale))
                    stack.enter_context(mock.patch.object(sim.random, "randint", side_effect=spawn_delay))
                    stack.enter_context(mock.patch.object(sim.time, "sleep"))
                    stack.enter_context(mock.patch.object(
                        sim.time, "monotonic", side_effect=[
                            0, 1 / 30, 1 / 30, 2 / 30, 2 / 30, 3 / 30,
                        ]))
                    for entity in (Fish, Whale, Bubble):
                        stack.enter_context(mock.patch.object(entity, "draw"))
                    hud = stack.enter_context(mock.patch.object(sim, "draw_hud"))
                    self.assertEqual(sim.run_sim(win, cfg), "quit")

                stats = hud.call_args[0][3]
                self.assertEqual(stats["whale"], 1)
                self.assertEqual(stats["bubble"], 5 if enabled else 0)
                self.assertEqual(whale.spout_cd <= 0, not enabled)


class SmallTerminalTests(unittest.TestCase):
    def test_bottom_decor_allows_very_narrow_terminal(self):
        for cols in range(1, 14):
            with self.subTest(cols=cols):
                decor = BottomDecor(cols, 8)
                for _, px, _, _ in decor.items:
                    self.assertGreaterEqual(px, 0)
                    self.assertLess(px, cols)

    def test_bottom_decor_is_sparse_and_non_overlapping(self):
        random.seed(32)
        decor = BottomDecor(160, 32)

        self.assertLessEqual(len(decor.items), 8)
        spans = []
        for _, px, _, art in decor.items:
            width = max(len(line) for line in art)
            for start, end in spans:
                self.assertTrue(px >= end + 3 or px + width <= start - 3)
            spans.append((px, px + width))


class ThemeChangeTests(unittest.TestCase):
    def test_fish_retheme_updates_existing_color(self):
        random.seed(4)
        fish = Fish(80, 24, 1.0, THEMES["realistic"])
        old = fish.rgb

        fish.retheme(THEMES["tokyo"])

        self.assertNotEqual(fish.rgb, old)
        self.assertIn(fish.rgb, THEMES["tokyo"]["fish"])


class ThemePaletteTests(unittest.TestCase):
    def test_themes_keep_required_shape_and_terminal_variety(self):
        required_keys = set(next(iter(THEMES.values())).keys())

        for name, theme in THEMES.items():
            with self.subTest(theme=name):
                self.assertEqual(set(theme.keys()), required_keys)
                self.assertEqual(len(theme["fish"]), 12)
                self.assertGreaterEqual(len({rgb256(*rgb) for rgb in theme["fish"]}), 8)

                for key, value in theme.items():
                    colors = value if key == "fish" else [value]
                    for rgb in colors:
                        self.assertEqual(len(rgb), 3)
                        self.assertTrue(all(0 <= channel <= 255 for channel in rgb))


class FishBehaviorTests(unittest.TestCase):
    def test_fish_speed_multiplier_is_not_baked_into_nominal_speed(self):
        random.seed(12)
        fish = Fish(120, 30, 3.0, THEMES["realistic"])
        _, hi = Fish.SPD[fish.size_cat]

        self.assertLessEqual(fish.nom_spd, hi)

    def test_fish_sprint_has_size_scaled_cap(self):
        random.seed(18)
        fish = Fish(120, 30, 1.0, THEMES["realistic"])
        speed = 5.0
        fish.state = fish.ST_SPRINT
        fish.ai_tick(0, 30, 120, speed, [])

        self.assertLessEqual(abs(fish.target_dx), fish.max_dx * speed)

    def test_fish_faces_away_from_nearby_shark(self):
        class SharkStub:
            x = 60
            y = 10
            right = False

        random.seed(24)
        fish = Fish(120, 30, 1.0, THEMES["realistic"])
        fish.x = 50
        fish.y = 10
        fish.right = True
        fish._set_art()

        fish.ai_tick(0, 30, 120, 1.0, [SharkStub()])

        self.assertFalse(fish.right)
        self.assertEqual(fish.state, fish.ST_SPRINT)

    def test_opaque_art_draw_does_not_write_space_runs(self):
        class FakeWin:
            def __init__(self):
                self.calls = []

            def getmaxyx(self):
                return (20, 80)

            def addstr(self, y, x, text, attr=0):
                self.calls.append((y, x, text, attr))

        win = FakeWin()
        draw_art_opaque(win, 2, 3, ["  °  ", "><((( º>"], 7)

        self.assertEqual(
            win.calls,
            [(2, 5, "°", 7), (3, 3, "><(((", 7), (3, 9, "º>", 7)],
        )
        self.assertTrue(all(" " not in text for _, _, text, _ in win.calls))


if __name__ == "__main__":
    unittest.main()
