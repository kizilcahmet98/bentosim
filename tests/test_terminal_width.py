import unicodedata
import unittest
from unittest import mock

from bentosim.aquarium import art, hud
from bentosim.aquarium.themes import THEMES
from bentosim.core import terminal


class TerminalWidthTests(unittest.TestCase):
    def test_width_counts_ascii_turkish_combining_and_wide_glyphs(self):
        for text, expected in (("", 0), ("ABC", 3), ("Türkçe", 6),
                               ("e\u0301", 1), ("水", 2), ("Ａ", 2),
                               ("🐠12", 4), ("⚓", 2), ("\u0301", 0)):
            with self.subTest(text=text):
                self.assertEqual(terminal.cell_width(text), expected)

    def test_cell_clipping_handles_mixed_widths_and_combining_marks(self):
        cases = [
            ("ABC", 2, 1, "BC"),
            ("🐠AB", 3, 0, "🐠A"),
            ("🐠AB", 3, 1, " AB"),
            ("A🐠B", 2, 2, " B"),
            ("e\u0301A", 1, 0, "e\u0301"),
            ("e\u0301A", 1, 1, "A"),
            ("水\u0301A", 2, 1, " A"),
            ("\u0301A", 1, 0, "A"),
            ("🐠", 1, 0, ""),
            ("ABC", 0, 0, ""),
            ("🐠AB", 3, 10, ""),
        ]
        for text, width, start, expected in cases:
            with self.subTest(text=text, width=width, start=start):
                actual = terminal.clip_cells(text, width, start)
                self.assertEqual(actual, expected)
                self.assertLessEqual(terminal.cell_width(actual), width)

    def test_right_clip_keeps_only_whole_wide_characters(self):
        win = mock.Mock()
        win.getmaxyx.return_value = (4, 6)
        terminal.safeadd(win, 1, 0, "🐠12🐋34", 7)
        win.addstr.assert_called_once_with(1, 0, "🐠12", 7)

    def test_partial_wide_character_at_left_keeps_following_cells_aligned(self):
        win = mock.Mock()
        win.getmaxyx.return_value = (4, 8)
        terminal.safeadd(win, 1, -1, "🐠AB", 7)
        win.addstr.assert_called_once_with(1, 0, " AB", 7)

    def test_combining_mark_stays_with_visible_base_character(self):
        win = mock.Mock()
        win.getmaxyx.return_value = (4, 2)
        terminal.safeadd(win, 1, 0, "e\u0301🐠", 7)
        win.addstr.assert_called_once_with(1, 0, "e\u0301", 7)
        win.reset_mock()
        terminal.safeadd(win, 1, -1, "e\u0301A", 7)
        win.addstr.assert_called_once_with(1, 0, "A", 7)

    def test_wide_character_is_omitted_if_only_one_cell_remains(self):
        win = mock.Mock()
        win.getmaxyx.return_value = (4, 2)
        terminal.safeadd(win, 1, 0, "🐠", 7)
        win.addstr.assert_not_called()

    def test_anchor_ring_aligns_with_shaft_without_a_wide_glyph(self):
        self.assertEqual(art.ANCHOR_ART[0].strip(), "O")
        self.assertEqual(art.ANCHOR_ART[0].index("O"), art.ANCHOR_ART[2].index("│"))
        self.assertTrue(all(unicodedata.east_asian_width(ch) not in ("W", "F")
                            for line in art.ANCHOR_ART for ch in line))

    def test_emoji_statistics_fit_physical_terminal_cells(self):
        stats = {name: 12 for name in ("fish", "shark", "whale", "jelly", "turtle",
                                      "crab", "octo", "eel", "manta", "bubble")}
        for width in (10, 20, 40, 80, 120):
            for paused in (False, True):
                with self.subTest(width=width, paused=paused):
                    win = mock.Mock()
                    win.getmaxyx.return_value = (24, width)
                    with mock.patch.object(hud, "cp", return_value=0):
                        hud.draw_hud(win, 24, width, stats, 10,
                                     THEMES["realistic"], paused,
                                     {"hud": True, "color_theme": "realistic"})
                    for (_, x, text, _), _ in win.addstr.call_args_list:
                        physical_width = sum(2 if unicodedata.east_asian_width(ch) in ("W", "F")
                                             else 1 for ch in text)
                        self.assertLessEqual(x + physical_width, width - 1)


if __name__ == "__main__":
    unittest.main()
