"""bentosim.aquarium.hud — üst başlık + alt istatistikler."""

from ..core import cp, safeadd


def draw_hud(win, rows, cols, stats, t, theme, paused, cfg):
    if not cfg.get("hud", True):
        return
    ta = cp(theme["title"], bold=True)
    ha = cp(theme["hud"], dim=True)

    safeadd(win, 0, 0, "─"*(cols-1), ha)
    title = " ◈ B E N T O S I M  ·  A K V A R Y U M  v0.1 ◈ "
    safeadd(win, 0, max(0, cols//2-len(title)//2), title, ta)

    status = (" ⏸ DURAKLATILDI [space] " if paused else
              " [q]çık [space]dur [m]menü [1-6]tema ")
    safeadd(win, 0, max(0, cols-len(status)-1), status, ha)

    parts = []
    icon_map = {"fish":"🐠", "shark":"🦈", "whale":"🐋", "jelly":"🪼",
                "turtle":"🐢", "crab":"🦀", "octo":"🐙", "eel":"〰",
                "manta":"〽", "bubble":"💧"}
    for k, icon in icon_map.items():
        n = stats.get(k, 0)
        if n > 0: parts.append(f"{icon}{n}")
    info = "  " + "  ".join(parts) + f"  tema:{cfg.get('color_theme','?')}  t:{int(t):05d}"
    safeadd(win, rows-3, 0, info[:cols-1], ha)
