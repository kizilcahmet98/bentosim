import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.aquarium import entities, sim
from bentosim.aquarium.config import DEFAULT_CFG
from bentosim.aquarium.themes import THEMES


class Screen:
    def __init__(self, cols):
        self.cols = cols
        self.visible = False

    def getmaxyx(self):
        return 24, self.cols

    def addstr(self, y, x, text, attr=0):
        self.visible = self.visible or bool(text.strip())


class LargeCreatureLifecycleTests(unittest.TestCase):
    def test_both_directions_enter_on_first_step_at_all_speed_settings(self):
        for cls in (entities.Shark, entities.Whale):
            for right in (False, True):
                for speed in (0.1, 1.0, 5.0):
                    for cols in (40, 80, 120):
                        with self.subTest(creature=cls.__name__, right=right, speed=speed, cols=cols):
                            with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1), \
                                    mock.patch.object(entities.random, "uniform", side_effect=lambda lo, hi: lo):
                                creature = cls(cols, 24, speed)
                            screen = Screen(cols)
                            with mock.patch.object(entities, "cp", return_value=0):
                                creature.draw(screen, THEMES["realistic"], 0)
                                self.assertFalse(screen.visible)
                                creature.update(1 / 30, 24, cols, speed)
                                self.assertFalse(creature.dead)
                                creature.draw(screen, THEMES["realistic"], 1 / 30)
                            self.assertTrue(screen.visible)

    def test_slot_is_released_exactly_when_last_visible_part_exits(self):
        for cls in (entities.Shark, entities.Whale):
            for right in (False, True):
                for cols in (40, 80, 120):
                    with self.subTest(creature=cls.__name__, right=right, cols=cols):
                        with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                            creature = cls(cols, 24, 1.0)
                        creature.dx = 2.0 if right else -2.0
                        entered = False
                        with mock.patch.object(entities, "cp", return_value=0):
                            for tick in range(250):
                                creature.update(tick / 30, 24, cols, 1.0)
                                screen = Screen(cols)
                                creature.draw(screen, THEMES["realistic"], tick / 30)
                                if screen.visible:
                                    entered = True
                                    self.assertFalse(creature.dead)
                                elif entered:
                                    self.assertTrue(creature.dead)
                                    break
                            else:
                                self.fail("Creature did not complete its visible pass")

    def test_exited_whale_allows_replacement_and_disabled_setting_blocks_spawns(self):
        for enabled in (False, True):
            for right in (False, True):
                with self.subTest(enabled=enabled, right=right):
                    cfg = DEFAULT_CFG.copy()
                    cfg.update(fish_count=1, whale=enabled, shark=False)
                    win = mock.MagicMock()
                    win.getmaxyx.return_value = (24, 80)
                    win.getch.side_effect = [-1, -1, -1, ord("q")]

                    def near_exit(*args):
                        with mock.patch.object(entities.random, "random", return_value=0.9 if right else 0.1):
                            whale = entities.Whale(*args)
                        glyphs = [col for line in whale.lines for col, ch in enumerate(line) if ch != " "]
                        whale.x = 78 - min(glyphs) if right else -max(glyphs)
                        whale.dx = 1.0 if right else -1.0
                        return whale

                    def spawn_delay(lo, hi):
                        return 1 if (lo, hi) == (700, 1500) else hi

                    with ExitStack() as stack:
                        for name in ("curs_set", "start_color", "use_default_colors"):
                            stack.enter_context(mock.patch.object(sim.curses, name))
                        stack.enter_context(mock.patch.object(sim, "env"))
                        stack.enter_context(mock.patch.object(sim, "BottomDecor"))
                        stack.enter_context(mock.patch.object(sim, "Whale", side_effect=near_exit))
                        spawn = sim.Whale
                        stack.enter_context(mock.patch.object(sim.random, "randint", side_effect=spawn_delay))
                        stack.enter_context(mock.patch.object(sim.time, "sleep"))
                        stack.enter_context(mock.patch.object(sim.time, "monotonic", side_effect=[
                            0, 1/30, 1/30, 2/30, 2/30, 3/30, 3/30, 4/30,
                        ]))
                        for cls in (entities.Fish, entities.Whale, entities.Bubble):
                            stack.enter_context(mock.patch.object(cls, "draw"))
                        hud = stack.enter_context(mock.patch.object(sim, "draw_hud"))
                        self.assertEqual(sim.run_sim(win, cfg), "quit")
                        self.assertEqual(spawn.call_count, 3 if enabled else 0)
                        self.assertTrue(all(call[0][3]["whale"] == int(enabled)
                                            for call in hud.call_args_list))


if __name__ == "__main__":
    unittest.main()
