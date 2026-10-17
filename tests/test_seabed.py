import random
import unittest
from unittest import mock

from bentosim.aquarium import environment, entities, art
from bentosim.aquarium.themes import THEMES


class Grid:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.cells = [list(" " * cols) for _ in range(rows)]

    def getmaxyx(self):
        return self.rows, self.cols

    def addstr(self, y, x, text, attr=0):
        assert 0 <= y < self.rows
        assert 0 <= x and x + len(text) < self.cols
        for col, ch in enumerate(text, x):
            self.cells[y][col] = ch


class SandTests(unittest.TestCase):
    def test_sand_is_still_across_time_and_preserves_behavior_randomness(self):
        state = random.getstate()
        for theme in THEMES.values():
            frames = []
            for t in (0, 2, 60):
                screen = Grid(24, 80)
                with mock.patch.object(environment, "cp", return_value=0):
                    environment.draw_sand(screen, 24, 80, t, theme)
                frames.append(screen.cells)
            self.assertEqual(frames[0], frames[1])
            self.assertEqual(frames[0], frames[2])
        self.assertEqual(random.getstate(), state)

    def test_sand_stays_in_bottom_three_rows_and_leaves_texture_gaps(self):
        for rows, cols in ((1, 1), (2, 10), (4, 20), (12, 40), (24, 80)):
            with self.subTest(size=(rows, cols)):
                screen = Grid(rows, cols)
                with mock.patch.object(environment, "cp", return_value=0):
                    environment.draw_sand(screen, rows, cols, 0, THEMES["realistic"])
                self.assertTrue(all(ch == " " for line in screen.cells[:max(0, rows-3)] for ch in line))
                if cols >= 20:
                    for line in screen.cells[-2:]:
                        self.assertIn(" ", line[:-1])
                        self.assertTrue(any(ch != " " for ch in line[:-1]))


class CrabTests(unittest.TestCase):
    def test_ending_repeated_dashes_restores_normal_speed(self):
        for speed in (0.1, 0.5, 1.0, 2.0, 5.0):
            for right in (False, True):
                with self.subTest(speed=speed, right=right):
                    with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                        crab = entities.Crab(80, 24, speed)
                    normal_dx = crab.dx
                    for _ in range(3):
                        crab.dash_cd, crab.dir_cd = 1, 1000
                        with mock.patch.object(entities.random, "randint", return_value=2):
                            crab.update(0, 24, 80, speed)
                        self.assertAlmostEqual(crab.dx, normal_dx * 3)
                        self.assertTrue(crab.dashing)
                        crab.update(0, 24, 80, speed)
                        self.assertFalse(crab.dashing)
                        self.assertAlmostEqual(crab.dx, normal_dx)

    def test_feet_follow_resized_ground_without_mutating_paused_state(self):
        crab = entities.Crab(80, 24, 1.0)
        crab.x = 60
        before = vars(crab).copy()
        for rows, cols in ((32, 80), (12, 20), (24, 80)):
            screen = Grid(rows, cols)
            with mock.patch.object(entities, "cp", return_value=0):
                crab.draw(screen, THEMES["realistic"], 0)
            feet = "".join(screen.cells[rows-3])
            self.assertIn("_|_", feet)
            self.assertEqual(vars(crab), before)


class SwimmingResizeTests(unittest.TestCase):
    def test_remaining_swimmers_preserve_sand_and_paused_state_in_all_frames(self):
        cases = [(entities.Jellyfish, True, frame) for frame in range(len(art.JELLY_FRAMES))]
        cases += [(entities.Octopus, True, frame) for frame in range(len(art.OCTOPUS_FRAMES))]
        cases += [(cls, right, None) for cls in (entities.Eel, entities.MantaRay)
                  for right in (False, True)]
        for cls, right, frame in cases:
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                creature = cls(100, 40) if cls in (entities.Jellyfish, entities.Octopus) else cls(100, 40, 1.0)
            if frame is not None:
                creature.frame = frame
            for y in (7, 25):
                creature.x, creature.y = 2, y
                before = vars(creature).copy()
                for rows, cols in ((24, 100), (12, 40), (8, 30), (4, 10), (32, 100)):
                    for theme_name in ("realistic", "premium"):
                        with self.subTest(creature=cls.__name__, right=right,
                                          frame=frame, y=y, size=(rows, cols), theme=theme_name):
                            screen = Grid(rows, cols)
                            with mock.patch.object(environment, "cp", return_value=0), \
                                    mock.patch.object(entities, "cp", return_value=0):
                                environment.draw_sand(screen, rows, cols, 0, THEMES[theme_name])
                                sand = [line[:] for line in screen.cells[-3:]]
                                creature.draw(screen, THEMES[theme_name], 0)
                            self.assertEqual(screen.cells[-3:], sand)
                            self.assertTrue(all(ch == " " for line in screen.cells[:min(2, rows-3)] for ch in line))
                            if rows >= 12:
                                self.assertTrue(any(ch != " " for line in screen.cells[2:-3] for ch in line))
                            self.assertEqual(vars(creature), before)


class DecorTests(unittest.TestCase):
    def test_coral_branch_gap_preserves_actual_seaweed(self):
        screen = Grid(16, 40)
        with mock.patch.object(environment, "_sw_h", {12: 4}), \
                mock.patch.object(environment, "cp", return_value=0), \
                mock.patch.object(entities, "cp", return_value=0):
            environment.draw_seaweed(screen, 16, 40, 0, THEMES["realistic"])
            plant = screen.cells[11][11]
            self.assertNotEqual(plant, " ")
            decor = entities.BottomDecor(40, 16)
            decor.items = [("coral", 10, 9, art.CORAL_DB[0])]
            decor.draw(screen, THEMES["realistic"], 0)
            self.assertEqual(screen.cells[11][11], plant)

    def test_decor_exteriors_are_clear_and_closed_interiors_stay_solid(self):
        cases = [("coral", lines) for lines in art.CORAL_DB]
        cases += [("anemone", lines) for lines in art.ANEMONE]
        cases += [("star", art.STARFISH_ART), ("anchor", art.ANCHOR_ART),
                  ("treasure", art.TREASURE_ART), ("rock", art.ROCK_ART),
                  ("skull", art.SKULL_ART)]
        for kind, lines in cases:
            for theme in THEMES.values():
                with self.subTest(kind=kind, lines=lines):
                    screen = Grid(24, 40)
                    screen.cells = [list("#" * 40) for _ in range(24)]
                    decor = entities.BottomDecor(40, 24)
                    decor.items = [(kind, 10, 10, lines)]
                    with mock.patch.object(entities, "cp", return_value=0):
                        decor.draw(screen, theme, 0)
                    self.assertEqual(screen.cells[10][10], "#")
                    if kind in ("treasure", "rock", "skull"):
                        interior_col = 3 if kind == "rock" else 2
                        self.assertEqual(screen.cells[11][10+interior_col], " ")

    def test_decor_fits_between_surface_and_sand(self):
        for rows in (10, 11, 12, 24):
            for water_top in (3, 4):
                for _ in range(30):
                    decor = entities.BottomDecor(80, rows, water_top=water_top)
                    for kind, x, y, lines in decor.items:
                        self.assertGreaterEqual(y, water_top)
                        self.assertEqual(y + len(lines), rows - 3)

    def test_tall_seaweed_preserves_surface_in_short_windows(self):
        for rows in (10, 11, 12):
            for top in (3, 4):
                screen = Grid(rows, 40)
                with mock.patch.object(environment, "_sw_h", {12: 8}), \
                        mock.patch.object(environment, "cp", return_value=0):
                    environment.draw_seaweed(screen, rows, 40, 0, THEMES["realistic"], top=top)
                self.assertTrue(all(ch == " " for line in screen.cells[:top] for ch in line))
                self.assertTrue(any(ch != " " for line in screen.cells[top:rows-3] for ch in line))


if __name__ == "__main__":
    unittest.main()
