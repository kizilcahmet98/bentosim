import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.aquarium import hud, sim, environment, menu
from bentosim.aquarium.config import DEFAULT_CFG
from bentosim.aquarium.themes import THEMES
from bentosim.core import cell_width


class HudLayoutTests(unittest.TestCase):
    def test_menu_headings_stay_inside_border_without_wrapping(self):
        for rows, width in ((8, 20), (12, 40), (24, 80)):
            with self.subTest(size=(rows, width)):
                win = mock.Mock()
                win.getmaxyx.return_value = (rows, width)
                menu.draw_menu_frame(win, rows, width, "realistic")
                headings = [call[0] for call in win.addstr.call_args_list
                            if call[0][0] in (1, 2, 3) and call[0][2] != "║"]
                self.assertEqual(len(headings), 3)
                self.assertIn("BENTOSIM", headings[0][2].replace(" ", ""))
                for _, x, text, _ in headings:
                    self.assertGreaterEqual(x, 1)
                    self.assertLessEqual(x + cell_width(text), width - 1)

    def test_title_and_controls_do_not_overlap_at_supported_widths(self):
        for width in (40, 60, 80, 120):
            for paused in (False, True):
                for theme_name in ("realistic", "premium"):
                    with self.subTest(width=width, paused=paused, theme=theme_name):
                        win = mock.Mock()
                        win.getmaxyx.return_value = (24, width)
                        with mock.patch.object(hud, "cp", side_effect=lambda c, **k: 7 if k.get("bold") else 9):
                            hud.draw_hud(win, 24, width, {"fish": 12}, 10,
                                         THEMES[theme_name], paused,
                                         {"hud": True, "color_theme": theme_name})
                        # İlk yazma yatay ayırıcıdır; sonraki iki başlık alanı ayrık olmalı.
                        fields = [call[0] for call in win.addstr.call_args_list
                                  if call[0][0] == 0][1:]
                        self.assertEqual(len(fields), 2)
                        occupied = set()
                        for _, x, text, _ in fields:
                            cells = set(range(x, x + len(text)))
                            self.assertFalse(occupied & cells)
                            self.assertGreaterEqual(x, 0)
                            self.assertLessEqual(x + len(text), width - 1)
                            occupied.update(cells)
                        title, status = fields[0][2], fields[1][2]
                        self.assertIn("BENTOSIM", title.replace(" ", ""))
                        if paused:
                            self.assertIn("DUR", status)
                            self.assertIn("[space]", status)
                        else:
                            self.assertIn("[q]", status)
                            self.assertIn("[m]", status)

    def test_tiny_terminals_do_not_receive_out_of_bounds_writes(self):
        for width in range(1, 20):
            for paused in (False, True):
                win = mock.Mock()
                win.getmaxyx.return_value = (24, width)
                with mock.patch.object(hud, "cp", return_value=0):
                    hud.draw_hud(win, 24, width, {}, 0, THEMES["realistic"],
                                 paused, {"hud": True})
                for (_, x, text, _), _ in win.addstr.call_args_list:
                    self.assertGreaterEqual(x, 0)
                    self.assertLessEqual(x + len(text), width - 1)

    def test_disabled_hud_does_not_draw(self):
        win = mock.Mock()
        with mock.patch.object(hud, "cp") as color:
            hud.draw_hud(win, 24, 80, {}, 0, THEMES["realistic"], False, {"hud": False})
        win.addstr.assert_not_called()
        color.assert_not_called()

    def test_scene_keeps_hud_surface_and_sand_on_separate_rows(self):
        for rows in (4, 5, 6, 7, 8, 12, 24):
            for enabled in (False, True):
                for theme_name in ("realistic", "premium"):
                    with self.subTest(rows=rows, hud=enabled, theme=theme_name):
                        theme = THEMES[theme_name]
                        cfg = DEFAULT_CFG.copy()
                        cfg.update(hud=enabled, color_theme=theme_name)
                        win = mock.Mock()
                        win.getmaxyx.return_value = (rows, 80)
                        win.getch.side_effect = [-1, ord(" "), ord("q")]
                        writes, frames = [], []
                        win.erase.side_effect = writes.clear
                        win.addstr.side_effect = lambda *args: writes.append(args)
                        win.refresh.side_effect = lambda: frames.append(writes[:])

                        def scene_color(rgb, **kwargs):
                            if rgb == theme["surface"]:
                                return 20
                            if rgb == theme["surf2"]:
                                return 21
                            return 30

                        with ExitStack() as stack:
                            for name in ("curs_set", "start_color", "use_default_colors"):
                                stack.enter_context(mock.patch.object(sim.curses, name))
                            stack.enter_context(mock.patch.object(sim.time, "sleep"))
                            stack.enter_context(mock.patch.object(sim.time, "monotonic", return_value=0))
                            stack.enter_context(mock.patch.object(sim.Fish, "draw"))
                            stack.enter_context(mock.patch.object(sim, "BottomDecor"))
                            for name in ("draw_water_bg", "draw_light_rays", "draw_seaweed"):
                                stack.enter_context(mock.patch.object(environment, name))
                            stack.enter_context(mock.patch.object(environment, "cp", side_effect=scene_color))
                            stack.enter_context(mock.patch.object(hud, "cp", side_effect=lambda c, **k: 7 if k.get("bold") else 9))
                            self.assertEqual(sim.run_sim(win, cfg), "quit")

                        self.assertEqual(len(frames), 2)  # Normal ve duraklatılmış kare.
                        for frame in frames:
                            hud_rows = {y for y, _, _, attr in frame if attr in (7, 9)}
                            surface_rows = {y for y, _, _, attr in frame if attr in (20, 21)}
                            sand_rows = {y for y, _, _, attr in frame if attr == 30}
                            self.assertFalse(hud_rows & surface_rows)
                            self.assertFalse(hud_rows & sand_rows)
                            self.assertFalse(surface_rows & sand_rows)
                            self.assertEqual(hud_rows, ({0, 1} if rows >= 7 else {0}) if enabled else set())
                            top = 2 if enabled and rows >= 7 else 1
                            self.assertEqual(surface_rows, {y for y in (top, top + 1) if y < rows - 3})


if __name__ == "__main__":
    unittest.main()
