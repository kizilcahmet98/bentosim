import unittest
from unittest import mock

from bentosim.aquarium import art, entities
from bentosim.aquarium.themes import THEMES


class PatternedScreen:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        # Sütun ve satıra göre değişen çizgiler, diğer obje/dekor izlerini temsil eder.
        self.cells = [[".:|><"[(x + 2 * y) % 5] for x in range(cols)]
                      for y in range(rows)]

    def getmaxyx(self):
        return self.rows, self.cols

    def addstr(self, y, x, text, attr=0):
        for col, ch in enumerate(text, x):
            self.cells[y][col] = ch


class ArtTransparencyTests(unittest.TestCase):
    def test_turtle_shell_and_flippers_stay_solid_with_clear_limb_gaps(self):
        water_cells = ((0, 0), (0, 15), (2, 0), (2, 15), (2, 17),
                       (3, 5), (3, 6), (3, 13), (3, 14), (3, 16))
        solid_cells = ((1, 3), (1, 4), (1, 9), (1, 11))
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                turtle = entities.Turtle(90, 30, 1.0)
            turtle.x, turtle.y = 3, 3
            for frame, theme_name, theme in (
                    (frame, name, theme) for frame in range(len(art.TURTLE_FRAMES_R))
                    for name, theme in THEMES.items()):
                turtle._set_frame(frame)
                before_state = vars(turtle).copy()
                with self.subTest(right=right, frame=frame, theme=theme_name):
                    screen = PatternedScreen(30, 90)
                    before = [row[:] for row in screen.cells]
                    with mock.patch.object(entities, "cp", return_value=0):
                        turtle.draw(screen, theme, 0)
                    for row, col in water_cells + solid_cells:
                        draw_col = col if right else turtle.W - 1 - col
                        self.assertEqual(turtle.lines[row][draw_col], " ")
                        expected = before[3 + row][3 + draw_col] if (row, col) in water_cells else " "
                        self.assertEqual(screen.cells[3 + row][3 + draw_col], expected,
                                         (row, col))
                    # Yukarı dönen paletin altında kalan su/dekor görünür olur.
                    for col in range(5, 13 if frame == 2 else 7):
                        draw_col = col if right else turtle.W - 1 - col
                        self.assertEqual(screen.cells[6][3 + draw_col], before[6][3 + draw_col])
                    # Eski sarkan yüzgecin alt satırları artık su/dekor alanıdır.
                    for row in (4, 5):
                        self.assertEqual(screen.cells[3 + row], before[3 + row])
                    self.assertEqual(vars(turtle), before_state)

    def test_skull_below_turtle_head_remains_whole_in_both_directions(self):
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                turtle = entities.Turtle(90, 30, 1.0)
            turtle.x, turtle.y = 10, 3
            width = max(map(len, art.SKULL_ART))
            x = 10 + (14 if right else turtle.W - 14 - width)
            y = 3 + 2
            decor = entities.BottomDecor.__new__(entities.BottomDecor)
            decor.items = [("skull", x, y, art.SKULL_ART)]
            for frame, theme_name, theme in (
                    (frame, name, theme) for frame in range(len(art.TURTLE_FRAMES_R))
                    for name, theme in THEMES.items()):
                turtle._set_frame(frame)
                with self.subTest(right=right, frame=frame, theme=theme_name):
                    screen = PatternedScreen(30, 90)
                    with mock.patch.object(entities, "cp", return_value=0):
                        decor.draw(screen, theme, 0)
                        before = [row[x:x + width] for row in screen.cells[y:y + len(art.SKULL_ART)]]
                        turtle.draw(screen, theme, 0)
                    self.assertEqual([row[x:x + width] for row in screen.cells[y:y + len(art.SKULL_ART)]], before)

    def test_shark_tail_and_swept_fin_gaps_preserve_background(self):
        water_cells = ((1, 20), (4, 16), (8, 16), (9, 18),
                       (9, 50), (10, 30), (10, 51), (11, 20))
        solid_cells = ((3, 7), (2, 35), (5, 30), (7, 30), (9, 43), (10, 42))
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                shark = entities.Shark(90, 30, 1.0)
            shark.x, shark.y = 3, 3
            for theme_name, theme in THEMES.items():
                with self.subTest(right=right, theme=theme_name):
                    screen = PatternedScreen(30, 90)
                    before = [row[:] for row in screen.cells]
                    with mock.patch.object(entities, "cp", return_value=0):
                        shark.draw(screen, theme, 0)
                    for row, col in water_cells + solid_cells:
                        draw_col = col if right else shark.W - 1 - col
                        self.assertEqual(shark.lines[row][draw_col], " ")
                        expected = before[3 + row][3 + draw_col] if (row, col) in water_cells else " "
                        self.assertEqual(screen.cells[3 + row][3 + draw_col], expected,
                                         (row, col))

    def test_skull_below_shark_head_remains_whole_in_both_directions(self):
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                shark = entities.Shark(90, 30, 1.0)
            shark.x, shark.y = 3, 3
            width = max(map(len, art.SKULL_ART))
            x = 3 + (50 if right else shark.W - 50 - width)
            y = 3 + 9
            decor = entities.BottomDecor.__new__(entities.BottomDecor)
            decor.items = [("skull", x, y, art.SKULL_ART)]
            for theme_name, theme in THEMES.items():
                with self.subTest(right=right, theme=theme_name):
                    screen = PatternedScreen(30, 90)
                    with mock.patch.object(entities, "cp", return_value=0):
                        decor.draw(screen, theme, 0)
                        before = [row[x:x + width] for row in screen.cells[y:y + len(art.SKULL_ART)]]
                        shark.draw(screen, theme, 0)
                    self.assertEqual([row[x:x + width] for row in screen.cells[y:y + len(art.SKULL_ART)]], before)

    def test_whale_fin_gaps_preserve_background_but_body_and_fin_stay_solid(self):
        water_cells = ((12, 3), (13, 3), (12, 20), (12, 60),
                       (13, 20), (13, 60), (14, 20), (14, 60))
        solid_cells = ((6, 60), (13, 77), (4, 5))
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                whale = entities.Whale(120, 30, 1.0)
            whale.x, whale.y = 3, 3
            for theme_name, theme in THEMES.items():
                with self.subTest(right=right, theme=theme_name):
                    screen = PatternedScreen(30, 120)
                    before = [row[:] for row in screen.cells]
                    with mock.patch.object(entities, "cp", return_value=0):
                        whale.draw(screen, theme, 0)
                    for row, col in water_cells + solid_cells:
                        draw_col = col if right else whale.W - 1 - col
                        self.assertEqual(whale.lines[row][draw_col], " ")
                        expected = before[3 + row][3 + draw_col] if (row, col) in water_cells else " "
                        self.assertEqual(screen.cells[3 + row][3 + draw_col], expected,
                                         (row, col))

    def test_skull_under_whale_fin_gap_remains_whole(self):
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                whale = entities.Whale(140, 35, 1.0)
            whale.x, whale.y = 3, 35 - 4 - whale.H
            decor = entities.BottomDecor.__new__(entities.BottomDecor)
            decor.items = [("skull", 50, 27, art.SKULL_ART)]
            for theme_name, theme in THEMES.items():
                with self.subTest(right=right, theme=theme_name):
                    screen = PatternedScreen(35, 140)
                    with mock.patch.object(entities, "cp", return_value=0):
                        decor.draw(screen, theme, 0)
                        before = [row[50:59] for row in screen.cells[27:32]]
                        whale.draw(screen, theme, 0)
                    self.assertEqual([row[50:59] for row in screen.cells[27:32]], before)

    def test_whale_under_chin_preserves_background_in_both_directions(self):
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                whale = entities.Whale(120, 30, 1.0)
            whale.x, whale.y = 3, 3
            for theme_name in ("realistic", "premium"):
                with self.subTest(right=right, theme=theme_name):
                    screen = PatternedScreen(30, 120)
                    before = [row[:] for row in screen.cells]
                    with mock.patch.object(entities, "cp", return_value=0):
                        whale.draw(screen, THEMES[theme_name], 0)
                    for row in range(12, 16):
                        for col in range(81, whale.W):
                            draw_col = col if right else whale.W - 1 - col
                            self.assertEqual(screen.cells[3 + row][3 + draw_col],
                                             before[3 + row][3 + draw_col],
                                             (row, col))

    def test_outside_and_limb_gaps_preserve_background_but_bodies_are_solid(self):
        # Sadece bu boş hücreler gövdenin parçası; diğer boşluklar şeffaf olmalı.
        cases = [
            (entities.Crab, art.CRAB_R, set()),
            (entities.Octopus, art.OCTOPUS_FRAMES, {(1, 2), (1, 4)}),
            (entities.Jellyfish, art.JELLY_FRAMES, set()),
            (entities.MantaRay, [art.RAY_R], {
                (1, 8), (2, 9), (2, 10), (2, 11), (2, 12),
                (3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14), (3, 16),
                (4, 9), (4, 10), (4, 11), (4, 12), (5, 8),
            }),
        ]
        directional = (entities.Turtle, entities.Crab, entities.MantaRay)
        for cls, frames, body_spaces in cases:
            for right in ((False, True) if cls in directional else (True,)):
                with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                    creature = cls(80, 24, 1.0) if cls in directional else cls(80, 24)
                for frame_index, right_lines in enumerate(frames):
                    if hasattr(creature, "frame"):
                        creature.frame = frame_index
                    lines = right_lines
                    spaces = body_spaces
                    if not right:
                        width = max(map(len, right_lines))
                        lines = [line.translate(art._MIRROR_MAP)[::-1] for line in right_lines]
                        spaces = {(row, width - 1 - col) for row, col in body_spaces}
                    for rows, cols in ((24, 80), (12, 20)):
                        for x in (-3, 3, cols - 4):
                            for theme_name in ("realistic", "premium"):
                                with self.subTest(creature=cls.__name__, right=right,
                                                  frame=frame_index, size=(rows, cols),
                                                  x=x, theme=theme_name):
                                    creature.x, creature.y = x, 3
                                    draw_x, draw_y = x, 3
                                    if cls is entities.Crab:
                                        # Yengecin görsel konumu yeniden boyutlandırmada
                                        # mevcut pencerenin zeminine ve kenarlarına bağlıdır.
                                        draw_x = max(1, min(cols - 10, x))
                                        draw_y = rows - 4
                                    else:
                                        draw_y = int(entities.clamp_swim_y(creature.y, rows, len(lines)))
                                    screen = PatternedScreen(rows, cols)
                                    expected = [line[:] for line in screen.cells]
                                    for row, line in enumerate(lines):
                                        if cls is not entities.Crab and draw_y + row >= rows - 3:
                                            continue
                                        for col, ch in enumerate(line):
                                            if ch == " " and (row, col) not in spaces:
                                                continue
                                            if 0 <= draw_x + col < cols - 1:
                                                expected[draw_y + row][draw_x + col] = ch
                                    with mock.patch.object(entities, "cp", return_value=0):
                                        creature.draw(screen, THEMES[theme_name], 0)
                                    self.assertEqual(screen.cells, expected)

    def test_coral_below_manta_rear_wing_remains_whole(self):
        coral = art.CORAL_DB[1]
        width = max(map(len, coral))
        for right in (False, True):
            with mock.patch.object(entities.random, "random", return_value=float(right)):
                manta = entities.MantaRay(90, 30, 1.0)
            manta.x, manta.y = 10, 3
            x = 10 if right else 10 + manta.W - width
            y = 7
            decor = entities.BottomDecor.__new__(entities.BottomDecor)
            decor.items = [("coral", x, y, coral)]
            for theme_name, theme in THEMES.items():
                with self.subTest(right=right, theme=theme_name):
                    screen = PatternedScreen(30, 90)
                    with mock.patch.object(entities, "cp", return_value=0):
                        decor.draw(screen, theme, 0)
                        before = [row[x:x + width] for row in screen.cells[y:y + len(coral)]]
                        manta.draw(screen, theme, 0)
                    self.assertEqual([row[x:x + width] for row in screen.cells[y:y + len(coral)]], before)


if __name__ == "__main__":
    unittest.main()
