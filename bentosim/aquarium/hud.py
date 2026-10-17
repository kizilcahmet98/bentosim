"""bentosim.aquarium.hud — üst başlık ve istatistik satırı."""

from .. import __version__
from ..core import cp, safeadd, cell_width, clip_cells


def hud_height(rows, enabled=True):
    """Küçük terminalde yüzey ve kum için yer bırakan HUD yüksekliği."""
    if not enabled or rows < 4:
        return 0
    return 2 if rows >= 7 else 1


def draw_hud(win, rows, cols, stats, t, theme, paused, cfg):
    height = hud_height(rows, cfg.get("hud", True))
    if not height:
        return
    ta = cp(theme["title"], bold=True)
    ha = cp(theme["hud"], dim=True)

    safeadd(win, 0, 0, "─"*(cols-1), ha)
    width = max(0, cols - 1)
    statuses = (("DURAKLATILDI [space]devam", "DURDU [space]", "||") if paused else
                ("[q]çık [space]dur [m]menü [1-6]tema", "[q]çık [m]menü", "[q]"))
    # Önce temel başlık ve kontrolleri sığdır, kalan alanda başlığı genişlet.
    status = next((s for s in statuses if cell_width(s) + 1 + cell_width("BENTOSIM") <= width),
                  clip_cells(statuses[-1], width))
    status_x = width - cell_width(status)
    title_room = max(0, status_x - 1)
    titles = (f"◈ B E N T O S I M  ·  A K V A R Y U M  v{__version__} ◈",
              f"BENTOSIM · AKVARYUM v{__version__}", "BENTOSIM")
    title = next((s for s in titles if cell_width(s) <= title_room), "")
    safeadd(win, 0, max(0, (title_room - cell_width(title)) // 2), title, ta)
    safeadd(win, 0, status_x, status, ha)

    if height < 2:
        return

    parts = []
    icon_map = {"fish":"🐠", "shark":"🦈", "whale":"🐋", "jelly":"🪼",
                "turtle":"🐢", "crab":"🦀", "octo":"🐙", "eel":"〰",
                "manta":"〽", "bubble":"💧"}
    for k, icon in icon_map.items():
        n = stats.get(k, 0)
        if n > 0: parts.append(f"{icon}{n}")
    info = "  " + "  ".join(parts) + f"  tema:{cfg.get('color_theme','?')}  t:{int(t):05d}"
    safeadd(win, 1, 0, info, ha)
