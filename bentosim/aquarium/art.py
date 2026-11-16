"""
bentosim.aquarium.art — ASCII sanat veritabanı.

Sağ-yön (`_R`) tek kaynaktır; sol-yön (`_L`) modül yüklenirken
``_mirror()`` ile otomatik üretilir. Yeni canlı eklerken sadece sağ-yön
çizilir. Küçük balıklarda ``>`` yönü belirtir; diğer canlılarda başın
konumu siluetin yönünü belirler.
"""

import math

_MIRROR_MAP = str.maketrans({
    '(': ')', ')': '(', '<': '>', '>': '<',
    '/': '\\', '\\': '/', '[': ']', ']': '[',
    '{': '}', '}': '{', '«': '»', '»': '«',
    '‹': '›', '›': '‹', '`': '´', '´': '`',
    'b': 'd', 'd': 'b', 'p': 'q', 'q': 'p',
})
# Braille çizgisinin hücre içindeki iki nokta sütunu da yön değiştirmeli.
_MIRROR_MAP.update({
    0x2800 + mask: 0x2800 + (((mask & 0x07) << 3) | ((mask & 0x38) >> 3)
                            | ((mask & 0x40) << 1) | ((mask & 0x80) >> 1))
    for mask in range(256)
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
    "                                   /\\",
    "    \\                             /  \\",
    "     \\`.                         /    \\",
    "      \\  \\              __..----'      \\__",
    "       \\   \\__     __..-'                 `--..__",
    "        \\    __..-'                              `--..__",
    "         )                                   /////    o `--._",
    "        /   __..--.                                   ___..--/",
    "       /  _.-'      `--..___                     \\____..--'",
    "      /.-'                  `--..______/        /",
    "                                      /    _.-'",
    "                                    /_.-'",
]
_SHARK_W = max(len(line) for line in SHARK_R)
SHARK_R = [line.ljust(_SHARK_W) for line in SHARK_R]
SHARK_L = _mirror("\n".join(SHARK_R)).split("\n")


# ── Balina ──
WHALE_R = [
    "                                                            __________^______________",
    "                                                __..------''                         ``---..___",
    "                                       __..---''                                               `--.",
    "     /\\                         __..-''                                                            `-.",
    "    /  \\                  __..-'                                                                      \\",
    "   /    \\            _..-'                                                                             \\",
    "  /      \\_______..-'                                                      ____              o         )",
    " <                                                                                                     /",
    "  \\      /___                                                                                         /",
    "   \\    /    __..--..__                                                                            .-'",
    "    \\  /               `--..___                                                                .-'",
    "     \\/                        `--..______________________________________________________..-'",
    "                                                                         \\______/",
    "                                                                          \\    /",
    "                                                                           \\  /",
    "                                                                            \\/",
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
    "   _..----.._",
    "-/   /__\\    \\_(·)",
    "  `-.____,---/",
    "  /_'  (____/",
]
TURTLE_R = _pad_art("\n".join(TURTLE_R)).split("\n")
TURTLE_L = _mirror("\n".join(TURTLE_R)).split("\n")

# Baş ve kabuk sabit; ön palet aynı erişimle sabit omuzdan yukarı döner.
# Kalkmış palet karın çizgisinin önünden geçer; arka yüzgeç sabit kalır.
TURTLE_FRAMES_R = [
    TURTLE_R,
    _pad_art("\n".join(TURTLE_R[:2] + [
        "  `-.____..--/", "  /_'  `.___/"])).split("\n"),
    _pad_art("\n".join(TURTLE_R[:2] + [
        "  `-.__(_____/", "  /_'"])).split("\n"),
]
TURTLE_FRAMES_L = [_mirror("\n".join(frame)).split("\n")
                   for frame in TURTLE_FRAMES_R]

TURTLE_PREVIEW = [
    "   _..---.._",
    "-/_________\\_(·)",
    "  /_'  (___/",
]
TURTLE_PREVIEW = _pad_art("\n".join(TURTLE_PREVIEW)).split("\n")


# ── Yengeç (animasyonlu) ──
CRAB_R = [
    [
        " _         _ ",
        "/ )  · ·  ( \\",
        "\\(_.(---)._)/",
        " _/ /   \\ \\_ ",
    ],
    [
        " _         _ ",
        "/ )  · ·  ( \\",
        "\\(_.(---)._)/",
        " /_/     \\_\\ ",
    ],
]
CRAB_R = [_pad_art("\n".join(frame)).split("\n") for frame in CRAB_R]
CRAB_L = [_mirror("\n".join(frame)).split("\n") for frame in CRAB_R]


# ── Ahtapot (yön ayrımı yok) ──
OCTOPUS_BODY = [
    "      .---.      ",
    "     (     )     ",
    "      \\· ·/      ",
    "   _.-'   '-._   ",
]
OCTOPUS_FRAMES = [
    OCTOPUS_BODY + [
        " _/ / /| |\\ \\ \\_ ",
        "( _/ / | | \\ \\_ )",
        " \\_) \\_) (_/ (_/ ",
    ],
    OCTOPUS_BODY + [
        " _/ / /| |\\ \\ \\_ ",
        "(_/ / / / / \\  _)",
        "\\_) \\_) (_/ (_/  ",
    ],
    OCTOPUS_BODY + [
        " _/ / /| |\\ \\ \\_ ",
        "(_  / \\ \\ \\ \\ \\_)",
        "  \\_) \\_) (_/ (_/",
    ],
]
OCTOPUS_PREVIEW = [
    "      .---.      ",
    "     ( · · )     ",
    "   _.-'   '-._   ",
    " _/ / /| |\\ \\ \\_ ",
    "(_/ (_/ \\_) \\_)  ",
]


# ── Deniz yılanı / yılan balığı ──
EEL_HEAD_R = "º>"
EEL_TAIL_R = "~"
EEL_WAVE_FRAMES = 48
_EEL_DOTS = ((1, 2, 4, 64), (8, 16, 32, 128))


def _eel_wave_body(body_width, phase):
    """Üç terminal satırında, iki nokta kalınlığında kesintisiz ince eğri."""
    masks = [[0] * body_width for _ in range(3)]
    pixel_width = body_width * 2
    for x in range(pixel_width):
        distance = (pixel_width - 1 - x) / (pixel_width - 1)
        wave = math.sin(math.pi * 2 * (distance - phase / EEL_WAVE_FRAMES))
        y = int(round(5 + 3.4 * wave * math.sin(math.pi * distance)))
        for dot_y in (y, y + 1):
            masks[dot_y // 4][x // 2] |= _EEL_DOTS[x % 2][dot_y % 4]
    return ["".join(chr(0x2800 + mask) if mask else " " for mask in row)
            for row in masks]


def build_eel_art(segments, right=True, phase=None):
    """Kesintisiz ince dalga gövdesini tek küçük başla birlikte aynalar."""
    width = 18 + 6 * (segments - 1)
    body_width = width - len(EEL_TAIL_R) - len(EEL_HEAD_R)
    if phase is None:
        art = EEL_TAIL_R + "≈" * body_width + EEL_HEAD_R
    else:
        body = _eel_wave_body(body_width, phase)
        lines = [" " + body[0] + "  ", EEL_TAIL_R + body[1] + EEL_HEAD_R,
                 " " + body[2] + "  "]
        art = "\n".join(lines)
    return art if right else _mirror(art)


def build_eel_frames(segments, right=True):
    """Baş/kuyruk ve genişlik sabitken gövdedeki dalgayı ilerletir."""
    return [build_eel_art(segments, right, phase) for phase in range(EEL_WAVE_FRAMES)]


EEL_R = build_eel_art(1).split("\n")
EEL_L = _mirror("\n".join(EEL_R)).split("\n")


# ── Işın balığı (manta ray) ──
RAY_R = [
    "       _.",
    "       \\ `-._",
    "        \\    `--._",
    "~--..___(      · _)",
    "        /    _..-'",
    "       / _.-'",
    "       `'",
]
RAY_R = _pad_art('\n'.join(RAY_R)).split('\n')
RAY_L = _mirror('\n'.join(RAY_R)).split('\n')

# Baş/kuyruk ve kanat kökleri sabit; kanatlar aynı yatay erişimle bükülür.
RAY_FRAMES_R = [
    RAY_R,
    _pad_art('\n'.join([
        "",
        "       _..-._",
        RAY_R[2],
        RAY_R[3],
        RAY_R[4],
        "       `-..-'",
        "",
    ])).split('\n'),
]
RAY_FRAMES_L = [_mirror('\n'.join(frame)).split('\n') for frame in RAY_FRAMES_R]

RAY_PREVIEW = [
    "      _.",
    "      \\ `--.._",
    "~--..__(    · _)",
    "      / _..-'",
    "      `'",
]
RAY_PREVIEW = _pad_art('\n'.join(RAY_PREVIEW)).split('\n')


# ── Denizanası (yön ayrımı yok) ──
JELLY_BELL = [
    "  _..._  ",
    " /· : ·\\ ",
    "(_.._.._)",
]
JELLY_FRAMES = [
    JELLY_BELL + [" )  │  ( ", "(   )   )", " ) (   ( "],
    JELLY_BELL + [" (  │  ) ", "  ) ( (  ", " (   ) ) "],
    JELLY_BELL + [" )  │  ) ", "(   ( (  ", " )   ) ) "],
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
