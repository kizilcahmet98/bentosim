# CLAUDE.md — Bentosim Project

> This file provides full development context for Claude. Upload it
> alongside the repo (or relevant files) to a new chat to continue work.

---

## 🚫 ABSOLUTE RULE — DO NOT LEAVE THE PROJECT DIRECTORY

**Working directory:** `/home/kizilcahmet98/dev/bentosim/`

Claude **must not** read, list, stat, write, or otherwise touch any
path outside this directory. This includes — but is not limited to —
`~/.ssh/`, `~/.config/`, `~/.gnupg/`, `/etc/`, `/tmp/`, the user's home
directory, sibling project directories, and any other location not
under the working tree above.

If a task seems to require something outside the project directory
(e.g., diagnosing git auth, reading dotfiles, checking system
binaries), **stop and ask the user first.** The user will explicitly
override this rule when they want it lifted.

This rule is permanent. Do **not** modify or relax it without an
explicit instruction from the user saying so.

---

## 🎯 Project Description

**Name:** Bentosim
**Vision:** Terminal-based visual simulation engine — a roof for multiple
modules (aquarium, space, ecosystem, etc.), all sharing a common core.
**Language:** Python 3.7+
**Dependencies:** None — stdlib only (curses, math, random, json, argparse, pathlib)
**License:** GNU General Public License v3.0 or later (free software;
derivative works must remain under GPLv3+)
**Target platforms:** Linux / macOS / WSL (Windows requires `windows-curses`)
**User-facing language:** Turkish (UI labels, menu items, HUD text)
**Code language:** English (function/variable names, code comments mostly Turkish)

### Module status

| Module | Status |
|--------|--------|
| `bentosim.aquarium` | ✅ shipped (was `akvaryum.py` v3.4) |
| `bentosim.space`    | 🔜 planned — space dogfights, asteroids, fly-bys |
| `bentosim.ecosystem`| 🔜 planned — predator/prey simulation |
| `bentosim.physics`  | 🔜 planned — particle systems, gravity |
| `bentosim.weather`  | 🔜 planned — storms, auroras |

---

## 📂 Repo Structure

```
bentosim/
├── bentosim/
│   ├── core/                  # paylaşımlı altyapı
│   │   ├── __init__.py        # public exports
│   │   ├── colors.py          # rgb256, cp, blend, reset_color_cache
│   │   └── terminal.py        # safeadd, lerp
│   ├── aquarium/              # Akvaryum modülü
│   │   ├── __init__.py
│   │   ├── art.py             # FISH_DB + büyük ASCII sanatları
│   │   ├── themes.py          # 6 tema, THEME_NAMES
│   │   ├── entities.py        # Entity, Fish, Shark, Whale, ... (11 sınıf)
│   │   ├── environment.py     # draw_water_bg, surface, light_rays, seaweed, sand
│   │   ├── menu.py            # full-screen TUI menü
│   │   ├── hud.py
│   │   ├── sim.py             # run_sim() — game loop
│   │   ├── config.py          # DEFAULT_CFG, load/save (~/.config/bentosim/aquarium.json)
│   │   └── cli.py             # argparse, run()
│   ├── __init__.py            # versiyon, paket meta
│   └── __main__.py            # 'python -m bentosim <module>' dispatcher
├── screenshots/               # demo görüntüleri / GIFs
├── .github/workflows/         # CI (ileride eklenecek)
├── LICENSE.md                 # GNU GPL v3.0
├── README.md                  # TR + EN bilingual
├── CLAUDE.md                  # bu dosya
├── pyproject.toml             # PyPI hazır
└── .gitignore
```

### Entry points

```bash
# CLI olarak (pyproject.toml -> [project.scripts])
bentosim aquarium

# Modül olarak
python -m bentosim aquarium
python -m bentosim aquarium --theme abyss --fish 18 --fps 60

# Doğrudan
python -c "from bentosim.aquarium import run; run()"
```

---

## 🏗️ Architecture Decisions

### 1. Modular package, NOT single file
Original `akvaryum.py` (1442 lines) was split into focused modules.
Each module < 700 lines. Split criteria: separation of art (data) /
behavior (entities) / drawing (environment) / control (sim, cli).

### 2. `core/` is the engine
Anything reusable across modules (color cache, safe terminal write,
math helpers) lives in `bentosim.core`. Aquarium imports from it.
Future modules (space, ecosystem) will too.

### 3. Color cache is module-level
`bentosim.core.colors` keeps `_pair_cache` and `_pair_id` as
module-level state. Theme switches call `reset_color_cache()`.
This is intentional — curses pair allocation is process-global,
so a single cache makes sense.

### 4. Zero dependencies
No `pip install` required for Linux/macOS. Windows users get a
hint to install `windows-curses` (offered as `[windows]` extra).

### 5. Symmetry rule (auto-mirrored)
Only right-facing (`_R`) ASCII art is hand-drawn; the left-facing
version is auto-derived at module load.
- Right-facing line ends with `>`
- Left side is computed via `_mirror()` in `art.py` — a translation
  table swaps directional chars (`(`↔`)`, `<`↔`>`, `/`↔`\`, `{`↔`}`,
  `«`↔`»`, etc.) and reverses each line.
- Shark gills: write `))` on the right; the mirror produces `((` on
  the left automatically.

When adding a new fish/creature, only the `_R` form is needed.
A mirror invariant test (`_mirror(r) == l`) is included in the test
recipe below.

### 6. ASCII backslash rule
For strings containing backslashes, ALWAYS use `\\` (escape):
```python
"  /\\  ",   # CORRECT
"  /\  ",    # WRONG — produces SyntaxWarning
```

### 7. ASCII art is auto-mirrored
Only `_R` (right-facing) is hand-drawn. `_L` is generated at module
load via `_mirror()` in `art.py`, which reverses each line and
translates directional characters. `FISH_DB` is built from a private
`_FISH_RAW` list of `(art_right, size, name)` tuples; the public
4-tuple shape `(art_right, art_left, size, name)` is preserved so
consumers in `entities.py` don't change. If a new directional glyph
appears in `_R` and isn't in `_MIRROR_MAP`, add it there.

### 8. Turn animation (cinematic)
Fish perform a 4-phase cinematic turn (~2.2 sec):
- Phase 1 (20-30 frames): Speed → 0
- Phase 2 (15-30 frames): Pause, flip direction at midpoint
- Phase 3 (20-30 frames): Accelerate in new direction

---

## 🎨 Aquarium Themes

256-color RGB system. Every theme MUST contain these keys:

```python
required_keys = [
    'surface', 'surf2', 'ray',           # water surface
    'mid_water', 'deep_water',           # background
    'sand', 'sand2', 'sand3',            # sand (3 tones)
    'plant', 'plant2',                   # seaweed
    'coral', 'coral2',                   # coral
    'bubble', 'jelly', 'shark',          # creatures
    'turtle', 'crab', 'whale', 'octo',
    'eel', 'ray_fish',
    'hud', 'title',                      # UI
    'star', 'treasure', 'rock',          # bottom objects
    'fish'                               # list of 12 RGB tuples
]
```

**Available themes:** ocean (default), deep, coral, abyss, bioluminescent, matrix.

---

## 🐠 Aquarium Entity System

### Entity base class
```python
class Entity:
    def __init__(self): self.dead = False
    def update(self, t, rows, cols, spd_mult): pass
    def draw(self, win, theme, t): pass
    def emit_bubble(self): return None
```

### Fish AI states
```python
ST_SWIM   = 0   # normal swimming
ST_SPRINT = 1   # fleeing from shark
ST_IDLE   = 2   # idle/pause
ST_TURN   = 3   # turning around (4 phases)
ST_SCHOOL = 4   # schooling mode
```

**Fish properties:** `nom_spd`, `target_dx`, `dx` (smooth lerp speed),
`phase`/`amp`/`freq` (sine wave), `can_turn` (85% chance), `school_center`,
`bcd` (bubble cooldown).

### Other entities
- **Shark:** Hunt AI (chases nearest fish)
- **Whale:** Slow, emits 5-bubble spout
- **Turtle:** SWIM/REST/RISE — periodic surface breathing
- **Crab:** Dash AI — sudden acceleration, direction changes
- **Octopus:** Ink mode (darkens when threatened)
- **Jellyfish:** Pulse animation, sway, frame transitions
- **Eel:** Long (2-5 segments), wavy swimming
- **MantaRay:** Slow, wing-flap simulation
- **Bubble:** Upward sway, wobble

---

## ⚙️ Configuration

```python
DEFAULT_CFG = {
    "color_theme": "ocean",
    "fish_count": 12,
    "shark": True, "whale": True, "turtle": True,
    "jellyfish": True, "crab": True, "octopus": True,
    "eel": True, "manta": True,
    "bubbles": True, "light_rays": True,
    "speed": 1.0, "fps": 30,
    "hud": True, "schooling": True,
}
```

Config file: `~/.config/bentosim/aquarium.json`

---

## 🎮 Keyboard (in-sim)

| Key | Action |
|-----|--------|
| `q` / `ESC` | Quit |
| `space` | Pause / Resume |
| `m` | Open TUI menu |
| `1`-`6` | Switch theme (instant) |
| `+` / `-` | Increase/decrease fish count |
| `f` | FPS cycle (15→20→30→45→60) |

---

## 🧪 Testing in sandbox (no real terminal)

```python
import sys, unittest.mock as mock
cm = mock.MagicMock()
cm.COLOR_PAIRS = 256
cm.A_BOLD = 1; cm.A_DIM = 2; cm.A_NORMAL = 0
cm.A_REVERSE = 4; cm.A_UNDERLINE = 8
cm.color_pair.return_value = 0
cm.error = Exception
cm.COLOR_BLACK = 0
with mock.patch.dict(sys.modules, {'curses': cm}):
    sys.path.insert(0, '.')   # repo root
    from bentosim.aquarium import entities, themes
    f = entities.Fish(80, 24, 1.0, themes.THEMES['ocean'])
    f.update(0.05, 24, 80, 1.0, [])
    print(f.x, f.y, f.right)
```

This pattern allows full unit testing of entity behavior, AI logic,
theme integrity, etc., without an actual terminal.

### Mirror invariant (run after editing `art.py`)

```python
with mock.patch.dict(sys.modules, {'curses': cm}):
    from bentosim.aquarium.art import (
        FISH_DB, SHARK_R, SHARK_L, WHALE_R, WHALE_L,
        TURTLE_R, TURTLE_L, RAY_R, RAY_L, EEL_R, EEL_L,
        CRAB_R, CRAB_L, _mirror,
    )
    for r, l, _, name in FISH_DB:
        assert _mirror(r) == l, f'FISH {name} asymmetric'
    for R, L, n in [(SHARK_R, SHARK_L, 'shark'),
                    (WHALE_R, WHALE_L, 'whale'),
                    (TURTLE_R, TURTLE_L, 'turtle'),
                    (RAY_R, RAY_L, 'ray'),
                    (EEL_R, EEL_L, 'eel')]:
        for i, line in enumerate(R):
            assert _mirror(line) == L[i], f'{n} line {i} asymmetric'
    for fi, frame in enumerate(CRAB_R):
        for li, line in enumerate(frame):
            assert _mirror(line) == CRAB_L[fi][li]
    print('OK')
```

---

## 🔮 Roadmap

| Module | Description |
|--------|-------------|
| 🌊 **aquarium** events | Storm, earthquake, big-wave mode (within aquarium) |
| 🌟 **aquarium** particles | Plankton, snow, light particles |
| 🚀 **space** module | Asteroids, dogfights, planets, stars |
| 🐺 **ecosystem** module | Predator/prey, food chains |
| ⚛️ **physics** module | Particle systems, gravity wells |
| 🌌 **weather** module | Storms, auroras, atmosphere |

---

## 💬 Suggested Opening Message for New Chat

```
Hi! I'd like to continue working on Bentosim, a terminal-based simulation
engine project. I've attached CLAUDE.md and the relevant source files.
Please review them and let me know when you're ready.

What I'd like to do: [WRITE NEW REQUEST HERE]
```

When Claude reads this file, it will understand the project's full
structure, design preferences, and development history.

**Note:** The user prefers Turkish for chat messages but is comfortable
with English documentation/code. Continue replying in Turkish unless
asked otherwise.

---

## 📝 Important Notes

- **Colors are stored as RGB tuples**, converted to curses 256-color palette via `core.colors.rgb256()`.
- **Theme switching:** call `reset_color_cache()` from `bentosim.core` after changing the theme. Without this, palette won't refresh.
- **Turkish characters:** All files are UTF-8; terminal must also be UTF-8.
- **HUD emojis:** 🐠🦈🪼🐢🦀🐋🐙〰〽💧 — all UTF-8.
- **`safeadd()`** is called many times per frame — keep it fast.
- **`bubbles` list** is capped at 100 entries.
- **Frame timing** uses `time.monotonic()` for stable FPS.
- **Each entity gets random `phase`, `amp`, `freq`** to avoid uniform-looking motion.

---

## 🔧 Common Tasks

### Adding a new fish
1. Add tuple to `aquarium/art.py::_FISH_RAW`: `(art_right, "S/M/L/X", "name")`
2. Right side must end with `>` (direction marker). `_L` is auto-derived.
3. Multi-line fish use `\n` separator
4. Run the mirror invariant test (see below) — `_mirror(r) == l` must hold for all entries.

### Adding a new theme
1. Add entry to `aquarium/themes.py::THEMES`
2. Provide ALL required color keys
3. `fish` must be a list of 12 RGB tuples
4. `THEME_NAMES` auto-generates

### Adding a new creature class
1. In `aquarium/art.py`, define only `XXX_R` (list of lines, or list-of-frames for animated).
   Then derive `XXX_L = [_mirror(line) for line in XXX_R]` (or nested comprehension for frames).
   Skip `_L` entirely if the creature has no horizontal direction (see `OCTOPUS_FRAMES`, `JELLY_FRAMES`).
2. Edit `aquarium/entities.py`
3. Inherit from `Entity`
4. Implement `update(self, t, rows, cols, spd_mult)`
5. Implement `draw(self, win, theme, t)`
6. Add to `sim.py::run_sim()` spawn loop and entity lists
7. Add to HUD stats dict + `icon_map` in `hud.py::draw_hud()`

### Adding a new top-level module (e.g., space)
1. Create `bentosim/space/` directory mirroring aquarium structure
2. Add a `cli.py` with `run(argv)` function
3. Register in `bentosim/__main__.py::main()` dispatcher
4. Update `pyproject.toml` if module needs new optional deps

---

*Last update: Bentosim v0.1.0 — initial modular release (refactored from akvaryum.py v3.4)*
