# Ekran görüntüleri

Bu klasör README ve GitHub sayfasında kullanılacak seçilmiş akvaryum ekran
görüntüleri ve demo GIF'leri içindir. Git takibine açıktır; uygulama bu
dosyalara ihtiyaç duymaz.

Debug ekran görüntülerini, önce/sonra karşılaştırmalarını ve geçici çizim
araçlarını repo kökündeki `tmp/` klasöründe tutun. `tmp/` Git dışında kalır.
Tanıtım için seçilen bir görseli `screenshots/` altına alın.

## Önerilen format

- Görüntüler: PNG, tercihen 1 MB altında.
- Demolar: kısa GIF veya terminal kaydı.
- Boyut: en az 80×24; tanıtım için 120×40 veya daha büyük terminal.
- Debug incelemesi yerine normal akvaryum görünümünü gösteren kareleri seçin.

## Adlandırma

```text
aquarium-realistic.png
aquarium-premium.png
aquarium-tokyo.gif
aquarium-menu.png
```

## Terminal kaydı

Yerel ortamınızda `asciinema` kuruluysa:

```sh
asciinema rec screenshots/aquarium-demo.cast
```

Kaydı izleyip paylaşılacak çıktıyı bu klasöre ekleyin.
