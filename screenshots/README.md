# Screenshots

Bu klasör Bentosim modüllerinin ekran görüntüleri ve demo GIF'leri içindir.

## Çizim önizlemesi

[Balina önizlemesi](whale-preview.svg), mevcut 104×12 ASCII çizimini `realistic`
temasının renkleriyle gösterir. Sabit hücre yerleşimi çizimin satır sonlarında
kaymasını önler; SVG yakınlaştırılabilir. Beş baloncuğun konumu balinanın
`emit_spout()` hesabından alınmıştır. Bu dosya koddan üretilmiş statik bir
önizlemedir; terminal ekran görüntüsü değildir ve çizim değişirse güncellenmelidir.

## Önerilen format

- **Görüntüler:** PNG, ≤ 1MB
- **Demolar:** GIF (asciinema → svg-term-cli ile dönüştürülebilir)
- **Boyut:** 80×24 minimum, 120×40 ideal

## Adlandırma

```
aquarium-realistic.png
aquarium-premium.png
aquarium-tokyo.gif
aquarium-menu.png
```

## Asciinema örneği

```bash
asciinema rec aquarium-demo.cast
svg-term --in aquarium-demo.cast --out aquarium-demo.svg --width 100 --height 30
```
