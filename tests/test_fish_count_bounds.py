import json
import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.aquarium import cli, config, menu, sim


class FishCountBoundsTests(unittest.TestCase):
    def test_menu_cycles_valid_counts_and_preserves_saved_value(self):
        lo, hi = config.BOUNDS["fish_count"]
        cfg = config.DEFAULT_CFG.copy()
        cfg["fish_count"] = lo
        win = mock.MagicMock()
        win.getmaxyx.return_value = (24, 60)
        keys = iter([menu.curses.KEY_DOWN] +
                    [menu.curses.KEY_RIGHT] * (hi - lo + 1) + [10])
        seen = []

        def read_key():
            seen.append(cfg["fish_count"])
            return next(keys)

        win.getch.side_effect = read_key
        with mock.patch.object(menu.curses, "curs_set"):
            menu.run_menu(win, cfg)

        self.assertEqual(set(seen), set(range(lo, hi + 1)))
        self.assertEqual(cfg["fish_count"], lo)
        with mock.patch.object(config, "CFG_PATH") as path:
            for count in set(seen):
                cfg["fish_count"] = count
                config.save_cfg(cfg)
                saved = path.write_text.call_args[0][0]
                self.assertEqual(json.loads(saved)["fish_count"], count)
                path.read_text.return_value = saved
                self.assertEqual(config.load_cfg()["fish_count"], count)

    def test_simulation_keyboard_respects_both_bounds(self):
        lo, hi = config.BOUNDS["fish_count"]
        cases = [(lo, "-", lo), (lo + 1, "-", lo),
                 (hi - 1, "+", hi), (hi, "+", hi)]
        for initial, key, expected in cases:
            with self.subTest(initial=initial, key=key):
                cfg = config.DEFAULT_CFG.copy()
                cfg["fish_count"] = initial
                win = mock.MagicMock()
                win.getmaxyx.return_value = (24, 80)
                # Duraklatılmış simülasyonda da aynı klavye kontrolleri kullanılır.
                win.getch.side_effect = [ord(" "), ord(key), ord("q")]
                with ExitStack() as stack:
                    for name in ("curs_set", "start_color", "use_default_colors"):
                        stack.enter_context(mock.patch.object(sim.curses, name))
                    stack.enter_context(mock.patch.object(sim, "draw_hud"))
                    stack.enter_context(mock.patch.object(sim, "env"))
                    stack.enter_context(mock.patch.object(sim, "BottomDecor"))
                    stack.enter_context(mock.patch.object(sim.Fish, "draw"))
                    stack.enter_context(mock.patch.object(sim.time, "sleep"))
                    self.assertEqual(sim.run_sim(win, cfg), "quit")
                self.assertEqual(cfg["fish_count"], expected)

    def test_cli_clamps_counts_to_shared_bounds(self):
        lo, hi = config.BOUNDS["fish_count"]
        for value, expected in ((lo - 1, lo), (lo, lo), (hi, hi), (hi + 1, hi)):
            with self.subTest(value=value):
                with mock.patch.object(cli, "load_cfg", return_value=config.DEFAULT_CFG.copy()), \
                        mock.patch.object(cli.curses, "wrapper") as wrapper, \
                        mock.patch("builtins.print"):
                    cli.run(["--fish", str(value)])
                self.assertEqual(wrapper.call_args[0][1]["fish_count"], expected)


if __name__ == "__main__":
    unittest.main()
