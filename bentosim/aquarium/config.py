"""bentosim.aquarium.config — varsayılan ayarlar + JSON yükle/kaydet."""

import json
from pathlib import Path


DEFAULT_CFG = {
    "color_theme": "ocean", "fish_count": 12,
    "shark": True, "whale": True, "turtle": True, "jellyfish": True,
    "crab": True, "octopus": True, "eel": True, "manta": True,
    "bubbles": True, "light_rays": True,
    "speed": 1.0, "fps": 30, "hud": True, "schooling": True,
}

CFG_PATH = Path.home() / ".config" / "bentosim" / "aquarium.json"


def load_cfg():
    if CFG_PATH.exists():
        try:
            d = json.loads(CFG_PATH.read_text())
            c = DEFAULT_CFG.copy()
            c.update(d)
            return c
        except Exception:
            pass
    return DEFAULT_CFG.copy()


def save_cfg(cfg):
    CFG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CFG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
