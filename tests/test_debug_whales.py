import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.aquarium import cli, entities, sim
from bentosim.aquarium.config import DEFAULT_CFG


class DebugWhaleTests(unittest.TestCase):
    def test_cli_debug_count_is_temporary_and_defaults_to_four(self):
        for args, expected in (([], 0), (["--debug-whales"], 4),
                               (["--debug-whales", "3"], 3),
                               (["--debug-whales", "5"], 5)):
            with self.subTest(args=args):
                cfg = DEFAULT_CFG.copy()
                with mock.patch.object(cli, "load_cfg", return_value=cfg), \
                        mock.patch.object(cli, "save_cfg") as save, \
                        mock.patch.object(cli.curses, "wrapper") as wrapper, \
                        mock.patch("builtins.print"):
                    cli.run(args)
                self.assertEqual(wrapper.call_args[0][3], expected)
                self.assertEqual(wrapper.call_args[0][1], DEFAULT_CFG)
                self.assertEqual(cfg, DEFAULT_CFG)
                save.assert_not_called()

    def test_first_frame_has_requested_visible_whales_without_simulation_steps(self):
        for count in (0, 3, 4, 5):
            for right in (False, True):
                with self.subTest(count=count, right=right):
                    cfg = DEFAULT_CFG.copy()
                    cfg["whale"] = False
                    original_cfg = cfg.copy()
                    screen = mock.MagicMock()
                    screen.getmaxyx.return_value = (30, 120)
                    screen.getch.side_effect = [-1, ord("q")]
                    drawn = []

                    def record_draw(whale, win, theme, t):
                        nose = whale.right_edge - 1 if whale.right else whale.left_edge
                        self.assertTrue(0 <= int(whale.x) + nose < 119)
                        self.assertTrue(4 <= whale.y <= 30 - 3 - whale.H)
                        self.assertEqual(t, 0)
                        drawn.append(whale)

                    with ExitStack() as stack:
                        for name in ("curs_set", "start_color", "use_default_colors"):
                            stack.enter_context(mock.patch.object(sim.curses, name))
                        stack.enter_context(mock.patch.object(sim, "env"))
                        stack.enter_context(mock.patch.object(sim, "BottomDecor"))
                        stack.enter_context(mock.patch.object(sim.Fish, "draw"))
                        stack.enter_context(mock.patch.object(entities.Whale, "draw", new=record_draw))
                        stack.enter_context(mock.patch.object(sim.random, "random", return_value=0.9 if right else 0.1))
                        stack.enter_context(mock.patch.object(sim.time, "monotonic", return_value=0))
                        stack.enter_context(mock.patch.object(sim.time, "sleep"))
                        hud = stack.enter_context(mock.patch.object(sim, "draw_hud"))
                        self.assertEqual(sim.run_sim(screen, cfg, debug_whales=count), "quit")
                    self.assertEqual(len(drawn), count)
                    self.assertEqual(hud.call_args[0][3]["whale"], count)
                    self.assertEqual(cfg, original_cfg)

    def test_debug_survives_menu_without_entering_saved_settings(self):
        cfg = DEFAULT_CFG.copy()
        screen = mock.Mock()
        with mock.patch.object(cli, "run_sim", side_effect=["menu", "quit"]) as run_sim, \
                mock.patch.object(cli, "run_menu", return_value=cfg), \
                mock.patch.object(cli, "save_cfg") as save:
            cli._curses_main(screen, cfg, False, debug_whales=4)
        self.assertEqual(run_sim.call_args_list,
                         [mock.call(screen, cfg, debug_whales=4)] * 2)
        save.assert_called_once_with(DEFAULT_CFG)


if __name__ == "__main__":
    unittest.main()
