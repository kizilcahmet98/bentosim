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


def _mirror(art: str) -> str:
    """``_R`` metnini ``_L``'ye çevirir: her satırı ters çevirir, yönlü
    karakterleri (parantez, slash, ok vs.) eşleniğine takas eder."""
    return '\n'.join(line.translate(_MIRROR_MAP)[::-1]
                     for line in art.split('\n'))


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

FISH_DB = [(r, _mirror(r), sz, name) for r, sz, name in _FISH_RAW]


# ── Köpekbalığı ──
SHARK_R = [
    r"        |\.                                                       ",
    r"        | \\                                  /\                  ",
    r"        |  \\                   _____________/  \____________     ",
    r"        |   \\___       __..---''                           `--._ ",
    r"        |      ``------''              ___       |||||   o     _.-'>",
    r"        |   __..---''`--..___________/   \________________..-'    ",
    r"        |  //_.--'               \______/        \___/            ",
    r"        | //                       \/          \__/                ",
    r"        |//                                                        ",
]
_SHARK_W = max(len(line) for line in SHARK_R)
SHARK_R = [line.ljust(_SHARK_W) for line in SHARK_R]
SHARK_L = [_mirror(line) for line in SHARK_R]


# ── Balina ──
WHALE_R = [
    r"          \   /                              __^__",
    r"           \_/                   __..---'''       `---..__",
    r"    ><=====/ \___        __..-'''                       `-.",
    r"          /      ``------''          ___            o      )",
    r"         /   __..---..__________________________________.-'",
    r"        /  //          `--.        \____/        \___/",
    r"       / //               `-.       \/            \_",
    r"      / //",
    r"       //",
]
_WHALE_W = max(len(line) for line in WHALE_R)
WHALE_R = [line.ljust(_WHALE_W) for line in WHALE_R]
WHALE_L = [_mirror(line) for line in WHALE_R]


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
EEL_R = ["≈§≈§≈§≈§º>"]
EEL_L = [_mirror(line) for line in EEL_R]


# ── Işın balığı (manta ray) ──
RAY_R = [
    "   /\\ /\\ ",
    "  ( ·· )->",
    "  /----/  ",
    "    ||    ",
]
RAY_L = [_mirror(line) for line in RAY_R]


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
ANCHOR_ART = ["   ⚓    ", "  ─┼─   ", "   │    ", "  ╭┴╮   ", " ╭╯ ╰╮  "]

BUBBLE_CHARS = ["·", "○", "◦", "°", "∘", "º", "⊙"]
