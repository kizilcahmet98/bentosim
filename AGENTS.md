# Bentosim — Agent Instructions

## Working rules

- Stay within this repository. Do not inspect or modify user dotfiles, system configuration or sibling projects unless explicitly authorized by the user.
- Resolve paths relative to the repository root; do not hard-code a checkout path.
- Preserve existing user changes and keep edits focused on the requested task.
- Always use `apply_patch` for file changes.
- Reply in Turkish unless requested otherwise. Use English identifiers and preserve Turkish user-facing UI text.
- Preserve the GPL-3.0-or-later license.
- Keep this single repository-level agent guide aligned with the actual code and workflows.

## Project structure

Bentosim is a Python 3.7+ curses terminal simulation package. The implemented simulation is the aquarium. Runtime code uses the standard library; Windows support uses the optional `windows-curses` extra. Preserve Python 3.7 compatibility and the stdlib-only design unless a dependency is clearly justified.

- `bentosim/__main__.py`: module dispatcher and console entry point.
- `bentosim/core/colors.py`: RGB conversion, color-pair cache and blending.
- `bentosim/core/terminal.py`: safe terminal writes and interpolation.
- `bentosim/aquarium/cli.py`: arguments and curses/menu lifecycle.
- `bentosim/aquarium/config.py`: defaults, normalization and JSON persistence.
- `bentosim/aquarium/sim.py`: input handling, spawning, updates and rendering loop.
- `bentosim/aquarium/entities.py`: creature behavior and drawing.
- `bentosim/aquarium/environment.py`: water, lighting and seabed rendering.
- `bentosim/aquarium/art.py`: creature art and automatic mirroring.
- `bentosim/aquarium/themes.py`: palettes and theme names.
- `bentosim/aquarium/menu.py`, `hud.py`: settings UI and status display.
- `tests/test_aquarium_regressions.py`: unittest regression coverage.
- `tests/test_fish_count_bounds.py`: menu, keyboard, CLI and persistence checks for fish count bounds.
- `tests/test_simulation_timing.py`: controlled-clock checks for FPS independence, pause/resume, lifetimes and rendering delays.
- `tests/test_art_visuals.py`: creature shape, mirroring and terminal clipping regression checks.
- `tests/test_art_transparency.py`: patterned-background checks for transparent exterior/limb gaps and opaque body interiors.
- `tests/test_hud_layout.py`: header/control layout and narrow-terminal regression checks.
- `tests/test_terminal_width.py`: Unicode cell widths, clipping, combining marks, anchor alignment and emoji HUD bounds.
- `screenshots/`: demo assets and capture instructions.
- `pyproject.toml`: package metadata, compatibility and entry point.

Reusable terminal/engine helpers belong in `core/`; aquarium behavior belongs in `aquarium/`. Other simulation modules are not implemented.

## Development commands

Run from the repository root. Use `python3` if `python` is unavailable.

```sh
python -m bentosim --help
python -m bentosim aquarium --help
python -m bentosim aquarium
python -m bentosim aquarium --theme premium --fish 18 --fps 60
python -m bentosim aquarium --menu
python -m unittest discover -s tests
python -m compileall -q bentosim
```

Optional local installation: `python -m pip install -e .`; the installed entry point is `bentosim aquarium`. On Windows, install with `python -m pip install -e ".[windows]"`.

Interactive runs require a real terminal. The application reads `~/.config/bentosim/aquarium.json` and can save settings through the menu or `--reset`. For automated checks, mock configuration I/O or redirect `config.CFG_PATH` inside the repository. Do not access the user's real settings without authorization.

## Implementation conventions

- Use four-space indentation, snake_case functions/variables, PascalCase classes and uppercase constants.
- Keep behavior, rendering, art data and CLI concerns in their respective modules.
- Use `core.terminal.safeadd()` for clipped output. Preserve behavior in small terminals and during resizing.
- Use `core.cell_width()` / `clip_cells()` for terminal text layout instead of character-count slicing. Wide/fullwidth characters take two cells; ambiguous characters take one. These helpers cover current single-codepoint icons and combining marks, not full font-dependent emoji/ZWJ grapheme shaping. Keep sprite art cell-stable; the anchor uses an ASCII ring.
- HUD row reservation is defined by `hud.hud_height()`. Place surface layers below it and above the three sand rows; very short terminals omit statistics or surface layers that do not fit.
- Colors are RGB tuples converted by shared helpers. Call `reset_color_cache()` when switching themes.
- Define directional art in its right-facing form and derive left-facing art with `art._mirror()`. Preserve the public `FISH_DB` tuple shape. Escape backslashes in Python strings.
- Mirror multi-line art on a common padded canvas. `_mirror()` pads short rows; pass the whole multi-line shape rather than mirroring unequal rows separately. `FISH_DB` stores both directions at the same row width.
- Use `draw_art_shape()` for shapes needing transparent exterior/limb gaps with opaque body rows. Keep `solid_rows` limited to body interiors; preserve the swimming-area clipping in `draw_swimming_art()`.
- Keep per-frame paths efficient. Preserve monotonic frame timing and consistent movement across FPS settings.
- `SimulationClock` drives logic at a fixed 30 Hz; FPS controls rendering. Keep entity updates, spawn timers and bubble emission inside simulation steps. Rendering must not consume the behavior RNG. Simulation time freezes while paused; positions are not interpolated between ticks.
- New themes must provide the same keys as existing palettes and 12 RGB fish colors. Treat `THEMES` and `THEME_NAMES` as the source of truth.
- Current themes: `realistic` (default), `premium`, `pastel`, `tokyo`, `gruvbox`, `mono`.
- Normalize configuration through `normalize_cfg()`. Current bounds: fish count 1–28, FPS 5–60, speed 0.1–5.0. Keep CLI, menu and simulation consistent with `BOUNDS`.
- When adding a creature, check art, entities, spawning, configuration, menu and HUD integration.
- Register new simulation modules in `bentosim/__main__.py` and provide their CLI entry point.

## Verification and delivery

Use stdlib `unittest` for new logic and regression tests. Existing tests cover configuration normalization, small terminals, theme changes/palettes and fish behavior. Inspect them before extending coverage; test meaningful behavior rather than duplicating implementation.

Run relevant tests for code changes and the full suite when appropriate. Check syntax after editing Python files. Verify mirror invariants for art changes. For curses changes, manually check a small terminal, resizing, menu navigation and at least one theme switch when a real terminal is available. Report checks that could not be performed.

Documentation-only changes do not require running the simulation. Keep README examples aligned with the CLI. Use concise commit subjects. PR descriptions should explain the visible change and validation, with terminal captures for visual changes where practical.
