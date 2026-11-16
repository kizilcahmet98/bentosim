import random
import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.core import colors
from bentosim.aquarium.entities import Fish, Whale
from bentosim.aquarium.themes import THEMES


class ColorPairTests(unittest.TestCase):
    def setUp(self):
        colors.reset_color_cache()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(colors.reset_color_cache)
        self.stack.enter_context(mock.patch.object(colors.curses, "COLOR_PAIRS", 32767,
                                                  create=True))
        self.stack.enter_context(mock.patch.object(colors.curses, "A_COLOR", 0xff00))
        self.stack.enter_context(mock.patch.object(colors.curses, "pair_number",
                                                  side_effect=lambda a: (a & 0xff00) >> 8))
        # macOS'ta gözlenen davranış: 256 -> A_STANDOUT, 1024 -> A_REVERSE.
        self.pair_attr = self.stack.enter_context(mock.patch.object(
            colors.curses, "color_pair", side_effect=lambda pid: pid << 8))
        self.init_pair = self.stack.enter_context(mock.patch.object(colors.curses, "init_pair"))

    def test_palette_equivalents_and_styles_share_one_pair(self):
        plain = colors.cp((100, 150, 200))
        bold = colors.cp((101, 151, 201), bold=True)
        dim = colors.cp((100, 150, 200), dim=True)
        both = colors.cp((101, 151, 201), bold=True, dim=True)

        self.assertEqual(bold, plain | colors.curses.A_BOLD)
        self.assertEqual(dim, plain | colors.curses.A_DIM)
        self.assertEqual(both, plain | colors.curses.A_BOLD | colors.curses.A_DIM)
        self.assertEqual(colors.cp((100, 150, 200)), plain)
        self.init_pair.assert_called_once_with(1, colors.rgb256(100, 150, 200), -1)

    def test_long_color_animation_never_adds_reverse_or_standout(self):
        allowed = colors.curses.A_COLOR | colors.curses.A_BOLD | colors.curses.A_DIM
        for tick in range(1100):
            attr = colors.cp((tick % 256, tick // 256, 64),
                             bold=tick % 2 == 0, dim=tick % 3 == 0)
            self.assertEqual(attr & ~allowed, 0, "tick={}".format(tick))
        self.assertLessEqual(self.init_pair.call_count, 255)
        self.assertTrue(all(1 <= call[0][0] <= 255
                            for call in self.init_pair.call_args_list))

    def test_fish_and_whale_keep_default_background_after_color_churn(self):
        self.addCleanup(random.setstate, random.getstate())
        random.seed(73)
        for tick in range(1100):
            colors.cp((tick % 256, tick // 256, 64))
        theme = THEMES["realistic"]
        for creature in (Fish(180, 40, 1.0, theme), Whale(180, 40, 1.0)):
            creature.x, creature.y = 3, 5
            win = mock.Mock()
            win.getmaxyx.return_value = (40, 180)
            creature.draw(win, theme, 0)
            self.assertTrue(win.addstr.call_args_list)
            for call in win.addstr.call_args_list:
                attr = call[0][3]
                allowed = colors.curses.A_COLOR | colors.curses.A_BOLD
                self.assertEqual(attr & ~allowed, 0)
                pid = (attr & colors.curses.A_COLOR) >> 8
                self.assertEqual(self.init_pair.call_args_list[pid - 1][0][2], -1)

    def test_full_palette_keeps_existing_cells_and_default_background(self):
        original = colors.cp((255, 0, 0))
        for index in range(16):
            colors.cp((index // 6 * 51, index % 6 * 51, 255), bg=(0, 0, 0))
        # Bütün xterm küp/gri renklerini isteyerek 255 kullanılabilir çifti doldur.
        for red in range(6):
            for green in range(6):
                for blue in range(6):
                    colors.cp((red * 51, green * 51, min(255, blue * 51 + 1)))
        for gray in range(8, 249, 10):
            colors.cp((gray, gray, gray))
        self.assertEqual(self.init_pair.call_count, 255)
        definitions = self.init_pair.call_args_list[:]

        self.assertEqual(colors.cp((255, 0, 0)), original)
        fallback = colors.cp((248, 248, 248), bold=True)
        self.assertEqual(fallback & ~colors.curses.A_COLOR, colors.curses.A_BOLD)
        self.assertEqual(self.init_pair.call_args_list, definitions)
        pid = (fallback & colors.curses.A_COLOR) >> 8
        self.assertEqual(definitions[pid - 1][0][2], -1)

    def test_small_pair_budget_uses_nearest_foreground_with_same_background(self):
        with mock.patch.object(colors.curses, "COLOR_PAIRS", 4):
            red = colors.cp((255, 0, 0))
            blue = colors.cp((0, 0, 255))
            black_bg = colors.cp((255, 0, 0), bg=(0, 0, 0))
            self.assertEqual(colors.cp((204, 0, 0)), red)
            self.assertEqual(colors.cp((0, 0, 204)), blue)
            self.assertEqual(colors.cp((204, 0, 0), bg=(0, 0, 0)), black_bg)
            # Yeni arka plan için yer yoksa yabancı bir arka plan kullanma.
            self.assertEqual(colors.cp((0, 255, 0), bg=(255, 255, 255)), 0)
        self.assertEqual(self.init_pair.call_count, 3)

    def test_no_pair_slots_keeps_only_requested_styles(self):
        with mock.patch.object(colors.curses, "COLOR_PAIRS", 1):
            self.assertEqual(colors.cp((255, 0, 0), bold=True), colors.curses.A_BOLD)
        self.init_pair.assert_not_called()

    def test_reset_redefines_colors_for_the_new_theme(self):
        colors.cp((255, 0, 0), bold=True)
        colors.reset_color_cache()
        self.assertEqual(colors.cp((0, 0, 255)), 1 << 8)
        self.assertEqual(self.init_pair.call_args_list,
                         [mock.call(1, 196, -1), mock.call(1, 21, -1)])

    def test_default_background_falls_back_when_terminal_rejects_it(self):
        self.init_pair.side_effect = [colors.curses.error(), None]
        plain = colors.cp((255, 0, 0))
        self.assertEqual(colors.cp((255, 0, 0), bold=True), plain | colors.curses.A_BOLD)
        self.assertEqual(self.init_pair.call_args_list,
                         [mock.call(1, 196, -1), mock.call(1, 196, colors.curses.COLOR_BLACK)])


if __name__ == "__main__":
    unittest.main()
