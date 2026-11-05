import unittest
from contextlib import ExitStack
from unittest import mock

from bentosim.aquarium import cli, entities, sim
from bentosim.aquarium.config import DEFAULT_CFG


SPECIES = {
    "fish": (entities.Fish, "fish"),
    "shark": (entities.Shark, "shark"),
    "whale": (entities.Whale, "whale"),
    "jellyfish": (entities.Jellyfish, "jelly"),
    "turtle": (entities.Turtle, "turtle"),
    "crab": (entities.Crab, "crab"),
    "octopus": (entities.Octopus, "octo"),
    "eel": (entities.Eel, "eel"),
    "manta": (entities.MantaRay, "manta"),
    "bubble": (entities.Bubble, "bubble"),
}


class DebugSpeciesTests(unittest.TestCase):
    def test_cli_passes_each_species_separately_from_settings(self):
        for species in SPECIES:
            with self.subTest(species=species):
                cfg = DEFAULT_CFG.copy()
                with mock.patch.object(cli, "load_cfg", return_value=cfg), \
                        mock.patch.object(cli, "save_cfg") as save, \
                        mock.patch.object(cli.curses, "wrapper") as wrapper, \
                        mock.patch("builtins.print"):
                    cli.run(["--debug-species", species])
                self.assertEqual(wrapper.call_args[0][4], species)
                self.assertEqual(wrapper.call_args[0][1], DEFAULT_CFG)
                self.assertEqual(cfg, DEFAULT_CFG)
                save.assert_not_called()

    def test_invalid_or_conflicting_debug_arguments_do_not_load_settings(self):
        for args in (["--debug-species"], ["--debug-species", "missing"],
                     ["--debug-species", "shark", "--debug-whales"]):
            with self.subTest(args=args), \
                    mock.patch.object(cli, "load_cfg") as load, \
                    mock.patch("sys.stderr"):
                with self.assertRaises(SystemExit) as error:
                    cli.run(args)
                self.assertEqual(error.exception.code, 2)
                load.assert_not_called()

    def test_three_creatures_are_drawn_on_first_frame_even_when_disabled(self):
        for species, (cls, stat) in SPECIES.items():
            for size in ((12, 40), (30, 120), (60, 240)):
                for right in (False, True):
                    with self.subTest(species=species, size=size, right=right):
                        cfg = {k: False if isinstance(v, bool) else v
                               for k, v in DEFAULT_CFG.items()}
                        cfg["fish_count"] = 1
                        before = cfg.copy()
                        screen = mock.MagicMock()
                        screen.getmaxyx.return_value = size
                        screen.getch.side_effect = [-1, ord("q")]
                        drawn = []
                        original_draw = cls.draw

                        def draw(creature, win, theme, t):
                            self.assertEqual(t, 0)
                            win.addstr.reset_mock()
                            original_draw(creature, win, theme, t)
                            self.assertTrue(any(call[0][2].strip()
                                                for call in win.addstr.call_args_list))
                            drawn.append(creature)

                        with ExitStack() as stack:
                            for name in ("curs_set", "start_color", "use_default_colors"):
                                stack.enter_context(mock.patch.object(sim.curses, name))
                            stack.enter_context(mock.patch.object(sim, "env"))
                            stack.enter_context(mock.patch.object(sim, "BottomDecor"))
                            stack.enter_context(mock.patch.object(entities, "cp", return_value=0))
                            stack.enter_context(mock.patch.object(cls, "draw", new=draw))
                            stack.enter_context(mock.patch.object(sim.random, "random",
                                                                 return_value=0.9 if right else 0.1))
                            stack.enter_context(mock.patch.object(sim.time, "monotonic", return_value=0))
                            stack.enter_context(mock.patch.object(sim.time, "sleep"))
                            hud = stack.enter_context(mock.patch.object(sim, "draw_hud"))
                            self.assertEqual(sim.run_sim(screen, cfg, debug_species=species), "quit")
                        self.assertEqual(len(drawn), 3)
                        self.assertEqual(hud.call_args[0][3][stat], 3)
                        self.assertEqual(len({(e.x, e.y) for e in drawn}), 3)
                        self.assertEqual(cfg, before)

    def test_selection_survives_menu_and_reset_without_being_saved(self):
        for start_menu in (False, True):
            cfg = DEFAULT_CFG.copy()
            screen = mock.Mock()
            with mock.patch.object(cli, "run_sim", side_effect=["menu", "quit"]) as run, \
                    mock.patch.object(cli, "run_menu", return_value=cfg), \
                    mock.patch.object(cli, "save_cfg") as save:
                cli._curses_main(screen, cfg, start_menu, debug_species="shark")
            self.assertEqual(run.call_args_list,
                             [mock.call(screen, cfg, debug_whales=0,
                                        debug_species="shark")] * 2)
            self.assertEqual(save.call_count, 2 if start_menu else 1)
            self.assertTrue(all(call == mock.call(DEFAULT_CFG) for call in save.call_args_list))

        with mock.patch.object(cli, "load_cfg", return_value=DEFAULT_CFG.copy()), \
                mock.patch.object(cli, "save_cfg") as save, \
                mock.patch.object(cli.curses, "wrapper"), mock.patch("builtins.print"):
            cli.run(["--reset", "--debug-species", "whale"])
        save.assert_called_once_with(DEFAULT_CFG)


if __name__ == "__main__":
    unittest.main()
