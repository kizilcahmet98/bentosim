"""
bentosim.aquarium.art — ASCII sanat veritabanı.

Sağ-yön (`_R`) tek kaynaktır; sol-yön (`_L`) modül yüklenirken
``_mirror()`` ile otomatik üretilir. Yeni canlı eklerken sadece sağ-yön
çizilir; ``_R`` satırları ``>`` ile bitmelidir (yön işareti).
"""

_MIRROR_MAP = str.maketrans({
    '(': ')', ')': '(', '<': '>', '>': '<',
    '/': '\\', '\\': '/', '[': ']', ']': '[',
    '{': '}', '}': '{', '«': '»', '»': '«',
    '‹': '›', '›': '‹', '`': '´', '´': '`',
    'b': 'd', 'd': 'b', 'p': 'q', 'q': 'p',
})


def _pad_art(art: str) -> str:
    """Satırları en geniş satıra tamamlayarak ortak bir tuval oluşturur."""
    lines = art.split('\n')
    width = max(map(len, lines))
    return '\n'.join(line.ljust(width) for line in lines)


def _mirror(art: str) -> str:
    """Ortak tuvalin yatay aynası; yönlü karakterleri eşleniğine takas eder.

    İki kez aynalama, girdinin ortak genişliğe tamamlanmış halini verir.
    """
    return '\n'.join(line.translate(_MIRROR_MAP)[::-1]
                     for line in _pad_art(art).split('\n'))


# ── Balıklar — sağ-yön tek kaynak ──
_FISH_RAW = [
    # ── Küçük ──
    ("><>",              "S", "küçük"),
    ("><'>",             "S", "parlak"),
    ("°><>",             "S", "gözlü"),
    ("><(~>",            "S", "kuyruklu"),
    ("><(>",             "S", "yuvarlak"),
    # ── Orta ──
    ("><(((*>",          "M", "klasik"),
    ("><((( º>",         "M", "iribaş"),
    ("~><(((*>",         "M", "dalgalı"),
    ("—><((( °>",        "M", "çizgili"),
    ("={(((*>",          "M", "zırhlı"),
    ("><·:·:>",          "M", "benekli"),
    ("≈><((°>",          "M", "akıntılı"),
    # ── Büyük (çok satır) ──
    ("    °    \n><((((( *>",   "L", "büyük"),
    ("  · · ·  \n>={{{{{(*>",   "L", "dev"),
    ("><≛≛≛≛≛º>\n   ~·~   ",    "L", "balina"),
    # ── Egzotik ──
    ("»=»=»>",           "X", "hızlı"),
    ("-~-~-*>",          "X", "yılan"),
    ("><(({°})>",        "X", "balon"),
    ("·´`·><*>",         "X", "parlayan"),
    (">·>·>·>",          "X", "şerit"),
]

FISH_DB = [(_pad_art(r), _mirror(r), sz, name) for r, sz, name in _FISH_RAW]


# ── Köpekbalığı ──
SHARK_R = [
    "                                         /\\",
    "          /\\                            /  \\",
    "         /  \\             _____________/    \\________",
    "        /    \\       _.-''                           `-._",
    "       /      \\__..-'                       )))))  o      `-.",
    "      <             __                     )))))        ___ _>",
    "       \\     __..--'  `--.._____________    \\_________.-'",
    "        \\   /                          \\    /",
    "         \\_/                            \\__/",
]
_SHARK_W = max(len(line) for line in SHARK_R)
SHARK_R = [line.ljust(_SHARK_W) for line in SHARK_R]
SHARK_L = [_mirror(line) for line in SHARK_R]


# ── Balina ──
WHALE_R = [
    "             \\     /                                         _________^______________",
    "              \\   /                            __..--------''                        ``----..___",
    "               \\_/                  __..-----''                                                 `--..",
    "      ><=====/ \\____      __..----''                                                                 `.",
    "             /       ``--------''                                          ____               o        )",
    "            /                                                                                         /",
    "           /   __..----..__________________________________________________________________________.-'",
    "          /  //               `---.                                      \\______/             \\____/",
    "         / //                      `-.                                    \\    /                   \\",
    "        / //                                                               \\__/                     \\_",
    "       / //",
    "        //",
]
_WHALE_W = max(len(line) for line in WHALE_R)
WHALE_R = [line.ljust(_WHALE_W) for line in WHALE_R]
WHALE_L = [_mirror(line) for line in WHALE_R]

# Menü paneli için tam silueti gösteren küçük çizimler.
SHARK_PREVIEW = [
    "          /\\",
    " ><______/  \\____",
    "  \\      ))) o  _>",
    "   `---._____.-'",
]
WHALE_PREVIEW = [
    "          __^___",
    " ><__..-''      `-.",
    "    `--.____ o    _)",
    "           \\___/-'",
]


# ── Deniz kaplumbağası ──
TURTLE_R = [
    "   .~~~.    ",
    "  (. o .)   ",
    "  |=====|-->",
    "   '---'    ",
    "  /| o |    ",
]
TURTLE_L = [_mirror(line) for line in TURTLE_R]


# ── Yengeç (animasyonlu) ──
CRAB_R = [
    [" /o/ ", " _|_ "],
    [" (o) ", " _|_ "],
]
CRAB_L = [[_mirror(line) for line in frame] for frame in CRAB_R]


# ── Ahtapot (yön ayrımı yok) ──
OCTOPUS_FRAMES = [
    [" ,---, ", "(. o .)", "|)   (|", "/v   v"],
    [" ,---, ", "(o . o)", "|(   )|", " v   v "],
]


# ── Deniz yılanı / yılan balığı ──
EEL_BODY_R = "≈§≈§≈§≈§"
EEL_HEAD_R = "º>"


def build_eel_art(segments, right=True):
    """Gövdeyi uzatır, tek kafayı ekler ve tüm şekli gerekirse aynalar."""
    art = EEL_BODY_R * segments + EEL_HEAD_R
    return art if right else _mirror(art)


EEL_R = [build_eel_art(1)]
EEL_L = [_mirror(line) for line in EEL_R]


# ── Işın balığı (manta ray) ──
RAY_R = [
    "   /\\ /\\ ",
    "  ( ·· )->",
    "  /----/  ",
    "    ||    ",
]
RAY_R = _pad_art('\n'.join(RAY_R)).split('\n')
RAY_L = _mirror('\n'.join(RAY_R)).split('\n')


# ── Denizanası (yön ayrımı yok) ──
JELLY_FRAMES = [
    [" ╭───╮ ", "(°·º·°)", " ╿╿╿╿╿ ", "  ╿ ╿  ", "  ╿   "],
    [" ╭───╮ ", "(·°·°·)", " ╿╿╿╿╿ ", " ╿  ╿  ", "   ╿  "],
    [" ╭───╮ ", "(º·°·º)", " ╿╿╿╿╿ ", "  ╿╿   ", "  ╿   "],
]


# ── Zemin dekorasyonu ──
CORAL_DB = [
    [" \\|/ ", " ─╫─ ", "  │  ", " ─┴─ "],   # çarpı mercan
    [" ╭╮╭ ", " ││╰ ", " ╰╯  "],               # çift dal
    ["  ψ  ", " ─┼─ ", "  │  "],               # trident
    [" ╭┬╮ ", " │││ ", " ╰┴╯ "],               # üçlü
    ["  *  ", " /│\\ ", "  │  ", " ─┴─ "],     # yıldız mercan
    [" ╭─╮ ", " │·│ ", " ╰─╯ ", "  │  "],      # boru mercan
    [" ≋≋≋ ", " ╭─╮ ", " │·│ ", " └─┘ "],      # yumuşak mercan
]

ANEMONE = [
    [" )(·)( ", " \\|||/ ", "  ╰╯   "],
    [" (·)(· ", " /|||\\  ", "  ╰╯   "],
]

STARFISH_ART = [
    "  ╲·│·╱  ",
    "──·(★)·──",
    "  ╱·│·╲  ",
]

TREASURE_ART = [
    " ╔═════╗ ",
    " ║ $$$ ║ ",
    " ║·····║ ",
    " ╚═════╝ ",
]

ROCK_ART   = ["  ╭───╮  ", " ╭╯ · ╰╮ ", " ╰─────╯ "]
SKULL_ART  = [" ╭─────╮ ", " │ ◉ ◉ │ ", " │  ▲  │ ", " ╰──┬──╯ ", "    │    "]
ANCHOR_ART = ["   O    ", "  ─┼─   ", "   │    ", "  ╭┴╮   ", " ╭╯ ╰╮  "]

BUBBLE_CHARS = ["·", "○", "◦", "°", "∘", "º", "⊙"]
