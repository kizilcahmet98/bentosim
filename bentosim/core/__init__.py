"""
bentosim.core — paylaşımlı altyapı.

Tüm Bentosim modülleri (aquarium, gelecekteki space, vb.) buradaki
renk motoru, terminal yardımcıları ve matematik araçlarını kullanır.
"""

from .colors import rgb256, cp, blend, reset_color_cache
from .terminal import safeadd, lerp

__all__ = [
    "rgb256", "cp", "blend", "reset_color_cache",
    "safeadd", "lerp",
]
