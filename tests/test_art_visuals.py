import math
import unittest
from unittest import mock

from bentosim.aquarium import art, entities, environment
from bentosim.aquarium.themes import THEMES
from bentosim.core import rgb256


class MirrorAlignmentVisualTests(unittest.TestCase):
    def test_multiline_mirroring_uses_one_axis_including_empty_rows(self):
        self.assertEqual(art._mirror(" >\n>\n"), "< \n <\n  ")
        self.assertEqual(art._mirror(art._mirror(" >\n>\n")), " >\n> \n  ")
        self.assertEqual(art._mirror(""), "")

    def test_manta_and_large_fish_have_correct_left_decoration_positions(self):
        self.assertEqual(art.RAY_L[0], "  /\\ /\\   ")
        expected_tops = {"büyük": "     °    ", "dev": "   · · ·  "}
        for index, (_, left, _, name) in enumerate(art.FISH_DB):
            if name not in expected_tops:
                continue
            with self.subTest(fish=name):
                self.assertEqual(left.split("\n")[0], expected_tops[name])
                with mock.patch.object(entities.random, "randrange", side_effect=[index, 0]), \
                        mock.patch.object(entities.random, "random", return_value=0.9):
                    fish = entities.Fish(80, 24, 1.0, THEMES["realistic"])
                old_size = (fish.W, fish.H)
                fish._do_turn()
                self.assertEqual(fish.lines[0], expected_tops[name])
                self.assertEqual((fish.W, fish.H), old_size)

    def test_all_directional_shapes_keep_rectangular_mirror_invariants(self):
        shapes = [(name, right, left) for right, left, _, name in art.FISH_DB]
        for name in ("SHARK", "WHALE", "TURTLE", "RAY", "EEL"):
            shapes.append((name, "\n".join(getattr(art, name + "_R")),
                           "\n".join(getattr(art, name + "_L"))))
        for index, (right, left) in enumerate(zip(art.CRAB_R, art.CRAB_L)):
            shapes.append(("crab frame {}".format(index), "\n".join(right), "\n".join(left)))
        for name, right, left in shapes:
            with self.subTest(shape=name):
                width = max(map(len, right.split("\n")))
                self.assertTrue(all(len(line) == width for line in right.split("\n")))
                self.assertTrue(all(len(line) == width for line in left.split("\n")))
                self.assertEqual(art._mirror(right), left)
                self.assertEqual(art._mirror(left), right)


class LargeCreatureSilhouetteVisualTests(unittest.TestCase):
    def test_whale_is_larger_than_shark_and_masks_cover_its_whole_shape(self):
        width, height = len(art.WHALE_R[0]), len(art.WHALE_R)
        self.assertGreaterEqual(width, 100)
        self.assertEqual(height, 16)
        self.assertGreater(width, len(art.SHARK_R[0]))
        self.assertEqual(art.WHALE_R[7].index("<"), 1)
        vertical_mirror = str.maketrans({"/": "\\", "\\": "/"})
        for row in range(3, 7):
            self.assertEqual(art.WHALE_R[row][:10].translate(vertical_mirror),
                             art.WHALE_R[14 - row][:10])
        self.assertEqual(sum(line.count(")") for line in art.WHALE_R), 1)
        self.assertNotIn("|", "\n".join(art.WHALE_R))
        self.assertEqual(sum(line.count("^") for line in art.WHALE_R), 1)
        for lines, spans in ((art.WHALE_R, entities.WHALE_SPANS_R),
                              (art.WHALE_L, entities.WHALE_SPANS_L)):
            self.assertEqual(len(spans), height)
            for row, (line, ranges) in enumerate(zip(lines, spans)):
                covered = set()
                for start, end in ranges:
                    self.assertTrue(0 <= start < end <= width)
                    covered.update(range(start, end))
                for col, ch in enumerate(line):
                    if ch != " ":
                        self.assertIn(col, covered, (row, col, ch))

    def test_masks_cover_outline_and_keep_body_solid_with_clear_fin_gaps(self):
        width = len(art.SHARK_R[0])
        self.assertGreaterEqual(width, 60)
        self.assertGreaterEqual(len(art.SHARK_R), 8)
        self.assertIn(")))))", "\n".join(art.SHARK_R))
        for right, lines, spans in ((True, art.SHARK_R, entities.SHARK_SPANS_R),
                                     (False, art.SHARK_L, entities.SHARK_SPANS_L)):
            with self.subTest(right=right):
                self.assertEqual(len(lines), len(spans))
                for row, (line, ranges) in enumerate(zip(lines, spans)):
                    covered = set()
                    for start, end in ranges:
                        self.assertTrue(0 <= start < end <= width)
                        covered.update(range(start, end))
                    for col, ch in enumerate(line):
                        if ch != " ":
                            self.assertIn(col, covered, (row, col, ch))
                gap = 20 if right else width - 1 - 20
                body = 30 if right else width - 1 - 30
                self.assertEqual(lines[1][gap], " ")
                self.assertFalse(any(start <= gap < end for start, end in spans[1]))
                self.assertEqual(lines[5][body], " ")
                self.assertTrue(any(start <= body < end for start, end in spans[5]))

    def test_rendered_large_creatures_keep_outline_and_clip_in_small_windows(self):
        cases = [(cls, right, gap, body)
                 for cls, gap, body in ((entities.Shark, (1, 20), (5, 30)),
                                        (entities.Whale, (1, 20), (6, 40)))
                 for right in (False, True)]
        for cls, right, gap, body in cases:
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                creature = cls(100, 24, 1.0)
            for rows, cols in ((24, 100), (12, 40)):
                for x in (-10, 2, 60):
                    for theme_name in ("realistic", "premium"):
                        with self.subTest(creature=cls.__name__, right=right,
                                          size=(rows, cols), x=x, theme=theme_name):
                            cells = [list("#" * cols) for _ in range(rows)]
                            win = mock.Mock()
                            win.getmaxyx.return_value = (rows, cols)

                            def addstr(row, col, text, attr=0):
                                cells[row][col:col + len(text)] = text

                            win.addstr.side_effect = addstr
                            creature.x, creature.y = x, 2
                            with mock.patch.object(entities, "cp", return_value=0):
                                creature.draw(win, THEMES[theme_name], 0)
                            for row, line in enumerate(creature.lines):
                                for col, ch in enumerate(line):
                                    if ch != " " and row + 2 < rows - 3 and 0 <= x + col < cols - 1:
                                        self.assertEqual(cells[row + 2][x + col], ch)
                            for (row, col), expected in ((gap, "#"), (body, " ")):
                                if not right:
                                    col = creature.W - 1 - col
                                if row + 2 < rows - 3 and 0 <= x + col < cols - 1:
                                    self.assertEqual(cells[row + 2][x + col], expected)
                            self.assertTrue(all(ch == "#" for line in cells[-3:] for ch in line))


class EelVisualTests(unittest.TestCase):
    def make_eel(self, segments, right):
        with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1), \
                mock.patch.object(entities.random, "randint", side_effect=[segments, 3]):
            return entities.Eel(80, 24, 1.0)

    def test_long_eel_has_one_head_and_mirrors_as_a_whole(self):
        for segments in range(2, 6):
            with self.subTest(segments=segments):
                right = self.make_eel(segments, True)
                left = self.make_eel(segments, False)
                self.assertEqual(right.art.count("º"), 1)
                self.assertEqual(left.art.count("º"), 1)
                self.assertEqual(right.art.count(">"), 1)
                self.assertEqual(left.art.count("<"), 1)
                self.assertTrue(right.art.endswith("º>"))
                self.assertTrue(left.art.startswith("<º"))
                self.assertEqual(right.art.count("§"), 4 * segments)
                self.assertEqual(right.W, 8 * segments + 2)
                self.assertEqual(left.W, right.W)
                self.assertEqual(left.art, art._mirror(right.art))

    def test_drawing_preserves_shape_and_clips_at_both_edges(self):
        for segments in range(2, 6):
            for right in (False, True):
                for theme_name in ("realistic", "premium"):
                    for x in (-3, 3, 20):
                        with self.subTest(segments=segments, right=right, theme=theme_name, x=x):
                            eel = self.make_eel(segments, right)
                            eel.x, eel.y = x, 2
                            win = mock.Mock()
                            win.getmaxyx.return_value = (8, 24)
                            with mock.patch.object(entities, "cp", return_value=7) as color:
                                eel.draw(win, THEMES[theme_name], 0)
                            # 24 sütunlu pencerede son sütun safeadd tarafından ayrılır.
                            expected = "".join(
                                ch for i, ch in enumerate(eel.art) if 0 <= x + i < 23)
                            win.addstr.assert_called_once_with(2, max(0, x), expected, 7)
                            color.assert_called_once_with(THEMES[theme_name]["eel"], bold=True)


class WhaleSpoutVisualTests(unittest.TestCase):
    def test_spout_is_centered_over_blowhole_in_both_directions(self):
        for right in (False, True):
            for x in (-10.5, 10.25, 70.5):
                for scatter in (-1.5, 0, 1.5):
                    with self.subTest(right=right, x=x, scatter=scatter):
                        with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                            whale = entities.Whale(80, 24, 1.0)
                        whale.x, whale.y = x, 6.5
                        whale.spout_cd = 0
                        with mock.patch.object(entities.random, "uniform", return_value=scatter):
                            bubbles = whale.emit_spout()

                        blowhole = next((col, row) for row, line in enumerate(whale.lines)
                                        for col, ch in enumerate(line) if ch == "^")
                        self.assertEqual(len(bubbles), 5)
                        self.assertEqual([b.x for b in bubbles],
                                         [x + blowhole[0] + dx + scatter for dx in range(-2, 3)])
                        self.assertTrue(all(b.y == whale.y + blowhole[1] - 1 for b in bubbles))
                        self.assertEqual(whale.emit_spout(), [])

    def test_spout_waits_until_cooldown_expires(self):
        whale = entities.Whale(80, 24, 1.0)
        whale.spout_cd = 1
        with mock.patch.object(entities, "Bubble") as bubble:
            self.assertEqual(whale.emit_spout(), [])
            bubble.assert_not_called()


class TurtleBubbleVisualTests(unittest.TestCase):
    def test_bubble_starts_above_mouth_in_both_directions(self):
        for right in (False, True):
            for x in (-3.5, 10.25, 75.5):
                for scatter in (-1.5, 0, 1.5):
                    with self.subTest(right=right, x=x, scatter=scatter):
                        with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                            turtle = entities.Turtle(80, 24, 1.0)
                        turtle.x, turtle.y = x, 6.5
                        turtle.bcd = 0
                        with mock.patch.object(entities.random, "uniform", return_value=scatter):
                            bubble = turtle.emit_bubble()
                        mouth = ">" if right else "<"
                        col, row = next((col, row) for row, line in enumerate(turtle.lines)
                                        for col, ch in enumerate(line) if ch == mouth)
                        self.assertEqual(bubble.x, x + col + scatter)
                        self.assertEqual(bubble.y, turtle.y + row - 1)
                        self.assertIsNone(turtle.emit_bubble())

    def test_bubble_waits_until_cooldown_expires(self):
        turtle = entities.Turtle(80, 24, 1.0)
        turtle.bcd = 1
        with mock.patch.object(entities, "Bubble") as bubble:
            self.assertIsNone(turtle.emit_bubble())
            bubble.assert_not_called()


class JellyfishPulseVisualTests(unittest.TestCase):
    def test_pulse_changes_visible_colors_in_every_theme_and_frame(self):
        jelly = entities.Jellyfish(80, 24)
        jelly.x, jelly.y = 3, 2
        for name, theme in THEMES.items():
            for frame in range(len(art.JELLY_FRAMES)):
                with self.subTest(theme=name, frame=frame):
                    jelly.frame = frame
                    phases = []
                    for phase in (-math.pi / 2, math.pi / 2, 3 * math.pi / 2):
                        jelly.pulse_t = phase
                        win = mock.Mock()
                        win.getmaxyx.return_value = (12, 40)
                        with mock.patch.object(entities, "cp", return_value=0) as color:
                            jelly.draw(win, theme, 0)
                        head = color.call_args_list[0][0][0]
                        tentacles = color.call_args_list[2][0][0]
                        for rgb in (head, tentacles):
                            self.assertTrue(all(0 <= c <= base <= 255
                                                for c, base in zip(rgb, theme["jelly"])))
                        self.assertTrue(all(t <= h for t, h in zip(tentacles, head)))
                        self.assertEqual(color.call_args_list[0][1], {"bold": True})
                        self.assertEqual(color.call_args_list[2][1], {"dim": True})
                        drawn = {(y - int(jelly.y), x + offset - int(jelly.x)): ch
                                 for (y, x, text, attr), _ in win.addstr.call_args_list
                                 for offset, ch in enumerate(text)}
                        expected = {(row, col): ch
                                    for row, line in enumerate(art.JELLY_FRAMES[frame])
                                    for col, ch in enumerate(line) if ch != " "}
                        self.assertEqual(drawn, expected)
                        phases.append((head, tentacles))
                    self.assertEqual(phases[0], phases[2])
                    for part in (0, 1):
                        self.assertLess(sum(phases[0][part]), sum(phases[1][part]))
                        self.assertNotEqual(rgb256(*phases[0][part]), rgb256(*phases[1][part]))

    def test_pulse_uses_a_bounded_palette_without_mutating_simulation(self):
        jelly = entities.Jellyfish(80, 24)
        win = mock.Mock()
        win.getmaxyx.return_value = (24, 80)
        colors = set()

        def color(rgb, **kwargs):
            colors.add((rgb, tuple(sorted(kwargs.items()))))
            return 0

        with mock.patch.object(entities, "cp", side_effect=color):
            for step in range(300):
                jelly.pulse_t = step * 2 * math.pi / 300
                before = vars(jelly).copy()
                jelly.draw(win, THEMES["realistic"], 0)
                self.assertEqual(vars(jelly), before)
        self.assertGreater(len(colors), 2)
        self.assertLessEqual(len(colors), 10)


class SwimmingBoundsVisualTests(unittest.TestCase):
    CLASSES = (entities.Shark, entities.Whale, entities.Turtle)

    def test_all_fish_preserve_sand_and_state_when_resized_without_update(self):
        for idx in range(len(art.FISH_DB)):
            for right in (False, True):
                with mock.patch.object(entities.random, "randrange", side_effect=[idx, 0]), \
                        mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                    fish = entities.Fish(80, 32, 1.0, THEMES["realistic"])
                fish.x, fish.y = 2, 25
                before = vars(fish).copy()
                for rows, cols in ((24, 80), (12, 40), (4, 10), (32, 80)):
                    with self.subTest(shape=idx, right=right, size=(rows, cols)):
                        win = mock.Mock()
                        win.getmaxyx.return_value = (rows, cols)
                        with mock.patch.object(entities, "cp", return_value=0):
                            fish.draw(win, THEMES["realistic"], 0)
                        for call in win.addstr.call_args_list:
                            y, x, text, attr = call[0]
                            self.assertGreaterEqual(y, 2)
                            self.assertLess(y, rows - 3)
                        if rows >= fish.H + 5:
                            self.assertTrue(win.addstr.called)
                        self.assertEqual(vars(fish), before)

    def test_spawned_and_updated_creatures_stay_above_sand(self):
        cases = [(cls, right) for cls in self.CLASSES for right in (False, True)]
        for cls, right in cases:
            height = len(getattr(art, cls.__name__.upper() + "_R"))
            for rows in (height + 5, 24, 40):
                with self.subTest(creature=cls.__name__, rows=rows, right=right):
                    # En derin doğma konumunu seç.
                    with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1), \
                            mock.patch.object(entities.random, "randint", side_effect=lambda lo, hi: hi):
                        creature = cls(100, rows, 1.0)
                    height = len(creature.lines)
                    self.assertGreaterEqual(creature.y, 2)
                    self.assertLessEqual(int(creature.y) + height, rows - 3)
                    for depth in (-100, 100):
                        creature.base_y = creature.y = depth
                        if isinstance(creature, entities.Shark):
                            creature.target_y = depth
                        for t in (0, 10, 100):
                            creature.update(t, rows, 100, 1.0)
                            self.assertGreaterEqual(creature.y, 2)
                            self.assertLessEqual(int(creature.y) + height, rows - 3)

    def test_resizing_never_draws_swimmers_over_sand(self):
        class Grid:
            def __init__(self, rows, cols):
                self.rows, self.cols = rows, cols
                self.cells = [list(" " * cols) for _ in range(rows)]

            def getmaxyx(self):
                return self.rows, self.cols

            def addstr(self, y, x, text, attr=0):
                for i, ch in enumerate(text):
                    self.cells[y][x + i] = ch

        cases = [(cls, right) for cls in self.CLASSES for right in (False, True)]
        for cls, right in cases:
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                creature = cls(100, 40, 1.0)
            creature.x, creature.y = 2, 25
            for theme_name in ("realistic", "premium"):
                for rows, cols in ((24, 100), (12, 40), (8, 30), (4, 10), (32, 100)):
                    with self.subTest(creature=cls.__name__, rows=rows, theme=theme_name, right=right):
                        grid = Grid(rows, cols)
                        with mock.patch.object(environment, "cp", return_value=0), \
                                mock.patch.object(entities, "cp", return_value=0):
                            environment.draw_sand(grid, rows, cols, 0, THEMES[theme_name])
                            sand = [line[:] for line in grid.cells[-3:]]
                            # Güncelleme olmadan çiz: duraklatma ve yüksek FPS'te resize.
                            creature.draw(grid, THEMES[theme_name], 0)
                        self.assertEqual(grid.cells[-3:], sand)
                        self.assertTrue(all(ch == " " for line in grid.cells[:min(2, rows - 3)]
                                            for ch in line))
                        if rows >= len(creature.lines) + 5:
                            self.assertTrue(any(ch != " " for line in grid.cells[2:-3] for ch in line))

    def test_crab_stays_on_seabed(self):
        crab = entities.Crab(80, 24, 1.0)
        for rows in (24, 12, 32):
            crab.update(0, rows, 80, 1.0)
            self.assertEqual(crab.y, rows - 4)
            win = mock.Mock()
            win.getmaxyx.return_value = (rows, 80)
            with mock.patch.object(entities, "cp", return_value=0):
                crab.draw(win, THEMES["realistic"], 0)
            self.assertEqual([call[0][0] for call in win.addstr.call_args_list],
                             [rows - 4, rows - 3])


if __name__ == "__main__":
    unittest.main()
