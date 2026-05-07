# Repository Guidelines

## Project Structure & Module Organization

Bentosim is a Python 3.7+ terminal simulation package with zero runtime dependencies beyond the standard library. Source code lives in `bentosim/`. Shared engine utilities are in `bentosim/core/`, including color and terminal helpers. The shipped aquarium module is in `bentosim/aquarium/`: `cli.py` handles arguments, `sim.py` runs the curses loop, `entities.py` contains simulation actors, `environment.py` draws the scene, `themes.py` defines palettes, and `art.py` stores ASCII art. `bentosim/__main__.py` dispatches `python -m bentosim <module>`. Screenshots and demo assets belong in `screenshots/`.

## Build, Test, and Development Commands

- `python -m bentosim aquarium` runs the aquarium directly from the checkout.
- `python -m bentosim aquarium --theme abyss --fish 18 --fps 60` smoke-tests CLI options.
- `python -m pip install -e .` installs the package locally and exposes the `bentosim` console script.
- `bentosim aquarium --menu` runs the installed entry point with the full-screen settings menu.
- `python -m compileall bentosim` performs a quick syntax check without adding dependencies.
- On Windows, install curses support with `python -m pip install -e ".[windows]"`.

## Coding Style & Naming Conventions

Use four-space indentation and standard Python naming: `snake_case` for functions and variables, `PascalCase` for classes, and uppercase constants such as `DEFAULT_CFG` or `THEME_NAMES`. Keep package code in English identifiers; user-facing aquarium text is Turkish. Preserve the stdlib-only design unless a dependency is clearly justified. For ASCII art, define right-facing forms and let `art.py` mirror them; escape backslashes as `\\`.

## Testing Guidelines

No automated test suite is currently committed. For new pure logic, add tests under `tests/` using `unittest` so the zero-dependency policy holds, and run `python -m unittest discover tests`. Prioritize tests for mirror invariants in `art.py`, config bounds, and reusable helpers in `bentosim/core/`. For curses behavior, include a manual smoke check with a small terminal and at least one theme change.

## Commit & Pull Request Guidelines

Recent commits use short, descriptive subjects, sometimes in Turkish, for example `Lisans ve README.md düzeltmesi` and `Bentosim v0.1.0 — modular aquarium simulation`. Keep the first line concise and focused on the visible change. Pull requests should include a summary, manual test commands run, linked issues when applicable, and screenshots or terminal captures for visual changes.

## Agent-Specific Instructions

Stay within the repository tree. Do not inspect user dotfiles, system config, or sibling projects unless explicitly asked. Do not relax license terms; Bentosim is GPL-3.0-or-later.
