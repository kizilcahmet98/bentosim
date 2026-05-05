# Screenshots

Bu klasör Bentosim modüllerinin ekran görüntüleri ve demo GIF'leri içindir.

## Önerilen format

- **Görüntüler:** PNG, ≤ 1MB
- **Demolar:** GIF (asciinema → svg-term-cli ile dönüştürülebilir)
- **Boyut:** 80×24 minimum, 120×40 ideal

## Adlandırma

```
aquarium-ocean.png
aquarium-abyss.png
aquarium-bioluminescent.gif
aquarium-menu.png
```

## Asciinema örneği

```bash
asciinema rec aquarium-demo.cast
svg-term --in aquarium-demo.cast --out aquarium-demo.svg --width 100 --height 30
```
