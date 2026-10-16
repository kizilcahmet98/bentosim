"""bentosim.aquarium.config — varsayılan ayarlar + JSON yükle/kaydet."""

import json
from pathlib import Path

from .themes import THEME_NAMES


DEFAULT_CFG = {
    "color_theme": "realistic", "fish_count": 12,
    "shark": True, "whale": True, "turtle": True, "jellyfish": True,
    "crab": True, "octopus": True, "eel": True, "manta": True,
    "bubbles": True, "light_rays": True,
    "speed": 1.0, "fps": 30, "hud": True, "schooling": True,
}

CFG_PATH = Path.home() / ".config" / "bentosim" / "aquarium.json"

BOUNDS = {
    "fish_count": (1, 28),
    "fps": (5, 60),
    "speed": (0.1, 5.0),
}


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def normalize_cfg(data=None):
    """Config'i beklenen tip ve sınırlar içinde normalize eder."""
    cfg = DEFAULT_CFG.copy()
    if isinstance(data, dict):
        cfg.update(data)

    if cfg.get("color_theme") not in THEME_NAMES:
        cfg["color_theme"] = DEFAULT_CFG["color_theme"]

    for key in ("fish_count", "fps"):
        lo, hi = BOUNDS[key]
        try:
            cfg[key] = _clamp(int(cfg.get(key, DEFAULT_CFG[key])), lo, hi)
        except (TypeError, ValueError):
            cfg[key] = DEFAULT_CFG[key]

    lo, hi = BOUNDS["speed"]
    try:
        cfg["speed"] = _clamp(float(cfg.get("speed", DEFAULT_CFG["speed"])), lo, hi)
    except (TypeError, ValueError):
        cfg["speed"] = DEFAULT_CFG["speed"]

    for key, default in DEFAULT_CFG.items():
        if isinstance(default, bool):
            value = cfg.get(key, default)
            cfg[key] = value if isinstance(value, bool) else default

    return cfg


def load_cfg():
    if CFG_PATH.exists():
        try:
            d = json.loads(CFG_PATH.read_text())
            return normalize_cfg(d)
        except Exception:
            pass
    return normalize_cfg()


def save_cfg(cfg):
    CFG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CFG_PATH.write_text(json.dumps(normalize_cfg(cfg), indent=2, ensure_ascii=False))
