<div align="center">

# 🐠 Bentosim

**Terminal-tabanlı görsel simülasyon motoru.**
A terminal-based visual simulation engine.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE.md)
[![Status: alpha](https://img.shields.io/badge/status-alpha-yellow.svg)]()

</div>

---

## 🇹🇷 Türkçe

**Bentosim**, terminalde çalışan görsel/etkileşimli simülasyonların ortak bir motorda toplandığı bir projedir. İlk modülü **Aquarium** (Akvaryum) — `asciiquarium`'a benzeyen ama daha gelişmiş bir terminal akvaryumu.

### Özellikler

Aquarium modülü:

- **20 farklı balık** + 9 büyük canlı (köpekbalığı, balina, kaplumbağa, denizanası, yengeç, ahtapot, yılan balığı, manta ray, kabarcık)
- **AI davranışları** — balıklar köpekbalığından kaçar, sürü halinde yüzer, ekran kenarında 4 fazlı sinematik dönüş yapar
- **6 renk teması** — `ocean`, `deep`, `coral`, `abyss`, `bioluminescent`, `matrix`
- **256 renk paleti** ile akıcı RGB
- **Tam ekran TUI menü** — her ayar tek tuşla değiştirilebilir
- **Sıfır bağımlılık** — sadece Python standart kütüphanesi

### Kurulum

```bash
git clone https://github.com/kizilcahmet98/bentosim.git
cd bentosim
python -m bentosim aquarium
```

Windows kullanıcıları için:
```bash
pip install windows-curses
```

### Kullanım

```bash
python -m bentosim aquarium                    # varsayılan
python -m bentosim aquarium --menu             # menüyle başlat
python -m bentosim aquarium --theme abyss      # tema seç
python -m bentosim aquarium --fish 18 --fps 60 # balık ve FPS ayarı
```

### Klavye

| Tuş | İşlev |
|-----|-------|
| `q` / `ESC` | Çıkış |
| `space` | Duraklat |
| `m` | Ayar menüsü |
| `1`–`6` | Tema değiştir (anlık) |
| `+` / `-` | Balık sayısı |
| `f` | FPS döngüsü |

### Lisans

[GNU General Public License v3.0](LICENSE.md) — özgür yazılım. Türev çalışmalar da aynı lisans altında dağıtılmalıdır.

---

## 🇬🇧 English

**Bentosim** is a terminal-based visual simulation engine. Its first module is **Aquarium** — an `asciiquarium`-like but significantly more advanced terminal aquarium.

### Features

The Aquarium module:

- **20 distinct fish** + 9 large creatures (shark, whale, turtle, jellyfish, crab, octopus, eel, manta ray, bubbles)
- **AI behaviors** — fish flee from sharks, school together, perform a 4-phase cinematic turn at the screen edge
- **6 color themes** — `ocean`, `deep`, `coral`, `abyss`, `bioluminescent`, `matrix`
- **256-color palette** for smooth RGB
- **Full-screen TUI menu** — every setting is one keystroke away
- **Zero dependencies** — Python standard library only

### Installation

```bash
git clone https://github.com/kizilcahmet98/bentosim.git
cd bentosim
python -m bentosim aquarium
```

Windows users:
```bash
pip install windows-curses
```

### Usage

```bash
python -m bentosim aquarium                    # default
python -m bentosim aquarium --menu             # start with menu
python -m bentosim aquarium --theme abyss      # pick a theme
python -m bentosim aquarium --fish 18 --fps 60 # tune fish & FPS
```

### Keyboard

| Key | Action |
|-----|--------|
| `q` / `ESC` | Quit |
| `space` | Pause |
| `m` | Settings menu |
| `1`–`6` | Switch theme |
| `+` / `-` | Fish count |
| `f` | FPS cycle |

### License

[GNU General Public License v3.0](LICENSE.md) — free software. Derivative works must be distributed under the same license.

---

## 🗺️ Roadmap

Bentosim's vision goes beyond aquariums. Planned modules:

- **`aquarium`** ✅ — current
- **`space`** — space dogfights, asteroid fields, planet fly-bys
- **`ecosystem`** — predator/prey simulation
- **`physics`** — particle systems, gravity playgrounds
- **`weather`** — storms, auroras, atmosphere

Each module shares the same `bentosim.core` (color engine, terminal helpers).

## 📁 Repo Yapısı / Structure

```
bentosim/
├── bentosim/
│   ├── core/              # paylaşımlı altyapı (renk, terminal)
│   │   ├── colors.py
│   │   └── terminal.py
│   ├── aquarium/          # Akvaryum modülü
│   │   ├── art.py         # ASCII sanat veritabanı
│   │   ├── themes.py      # 6 renk teması
│   │   ├── entities.py    # Fish, Shark, Whale, ...
│   │   ├── environment.py # zemin, su, ışık huzmeleri
│   │   ├── menu.py        # TUI menü
│   │   ├── hud.py
│   │   ├── sim.py         # ana döngü
│   │   ├── config.py
│   │   └── cli.py         # argparse
│   ├── __init__.py
│   └── __main__.py        # 'python -m bentosim <modül>'
├── screenshots/
├── LICENSE.md
├── README.md
├── CLAUDE.md              # geliştirme bağlamı
└── pyproject.toml
```

## 🤝 Katkı / Contributing

Bug bildirimleri, tema önerileri ve yeni canlı PR'ları memnuniyetle karşılanır. Yeni modül (space, ecosystem, vb.) önermek isterseniz lütfen önce bir issue açın.

---

<div align="center">

🐠 ✨ 🦈

</div>
