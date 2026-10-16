# İnceleme ve düzeltme takibi

Bu liste davranış ve görsel incelemelerde bulunan sorunları ve düzeltmelerin kabul ölçütlerini içerir. Her adım tamamlandığında durumu ve doğrulama sonucu burada güncellenir.

## 1. Menüde gereksiz CPU tüketimi

- [x] Düzeltildi; otomatik testler ve kullanıcının gerçek terminal kontrolü tamamlandı.
- Konum: `bentosim/aquarium/menu.py`, `sim.py`.
- Sorun: Simülasyonun açtığı `nodelay(True)` menüye taşınıyor. `m` ile açılan menü tuş beklemek yerine sürekli yeniden çiziliyor.
- Hedef: Menü tuş girişini beklemeli; simülasyona dönüşte gerekli giriş modu yeniden kurulmalı.
- Doğrulama: Açılış menüsü ve simülasyondan menüye geçiş için giriş modu kontrolü; gerçek terminalde menüye girme, ayar değiştirme ve simülasyona dönme.
- Uygulama: `run_menu()` girişinde `nodelay(False)` ile tuş bekleme etkinleştirildi. `run_sim()` mevcut `nodelay(True)` çağrısıyla simülasyon modunu yeniden kuruyor.
- Sonuç: Açılış menüsü açık/kapalı ve 12×40 / 24×80 ekran senaryolarında gerçek menü/simülasyon giriş fonksiyonları sahte curses penceresiyle çalıştırıldı. Tema değiştirme, menüden dönüş ve giriş modları doğrulandı. `python3 -m unittest discover -s tests -v`: 11 test geçti. Gerçek terminalde görsel kontrol yapılmadı.

## 2. Kapalı kabarcık ayarının balinaya uygulanması

- [x] Düzeltildi; otomatik testler ve kullanıcının gerçek terminal kontrolü tamamlandı.
- Konum: `bentosim/aquarium/sim.py`.
- Sorun: Balina fıskiyesi `bubbles` kontrolünün dışında kabarcık üretiyor.
- Hedef: Kabarcık ayarı kapalıyken balina dahil hiçbir kaynak yeni kabarcık eklememeli; açıkken mevcut davranış korunmalı.
- Doğrulama: Balinanın fıskiye zamanı geldiğinde açık/kapalı ayarla kabarcık üretimini karşılaştıran regresyon testi.
- Uygulama: Balina fıskiyesi de diğer kabarcık kaynaklarıyla aynı `bubbles` koşuluna alındı.
- Sonuç: Gerçek simülasyon döngüsü sahte terminalle çalıştırılarak balinanın doğması ve fıskiye zamanının gelmesi test edildi. Yeni test düzeltmeden önce kapalı ayarda 5 kabarcık üreterek başarısız oldu; düzeltmeden sonra kapalıyken 0, açıkken 5 kabarcık üretildiği doğrulandı. 12 test ve değişen Python dosyalarının sözdizimi kontrolü geçti. Gerçek terminalde görsel kontrol yapılmadı.

## 3. Balık sayısı sınırlarının tutarlılığı

- [x] Düzeltildi; otomatik testler ve kullanıcının gerçek terminal kontrolü tamamlandı.
- Konum: `bentosim/aquarium/menu.py`, `config.py`, `sim.py`.
- Sorun: Menü 3–29, yapılandırma 1–28 aralığını kullanıyor; simülasyondaki eksi tuşu da 2'de duruyor. Menüde 29 seçildiğinde oturum değeri ile kaydedilen değer farklılaşıyor.
- Hedef: Menü, CLI, klavye kontrolü ve kayıt işlemi `config.BOUNDS` içindeki 1–28 sınırlarına uymalı.
- Doğrulama: Alt/üst sınırlar, menü seçimi ve kayıt için normalizasyonun aynı değeri üretmesi.
- Uygulama: Menü seçenekleri ve simülasyondaki `+`/`-` kontrolleri artık `config.BOUNDS["fish_count"]` sınırlarını kullanıyor. CLI ve kayıt işlemi mevcut normalizasyonu kullanmaya devam ediyor.
- Sonuç: Yeni regresyon testleri düzeltmeden önce menüde 29 seçilebildiğini ve klavyeyle 2'den 1'e inilemediğini gösterdi. Düzeltmeden sonra menüde 1–28 seçenekleri, sınırda döngü, tüm seçeneklerin kayıt/yükleme sırasında korunması, CLI sınırları ve `+`/`-` alt/üst sınırları doğrulandı. Dosya işlemleri taklit edildi; kullanıcı ayarlarına erişilmedi. 15 test ve değişen Python dosyalarının sözdizimi kontrolü geçti. Gerçek terminal kontrolü yapılmadı.

## 4. FPS değişiminde simülasyon zamanının tutarlılığı

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `bentosim/aquarium/sim.py`, `entities.py`, gerektiğinde `environment.py`.
- Sorun: `frame_speed()` tüm canlılara uygulanmıyor. Bazı canlıların hızı oluşturulurken sabitleniyor; animasyon, davranış, ömür ve doğma sayaçları kare bazlı ilerliyor. `t` her karede sabit artıyor.
- Hedef: FPS değişimi eşit gerçek süredeki hareketi ve olay sürelerini değiştirmemeli. Mevcut ve yeni doğan canlılar aynı zaman ölçeğini kullanmalı; duraklatma simülasyon zamanını ilerletmemeli.
- Doğrulama: Sabit rastgelelik ve kontrollü zamanla farklı FPS değerlerinde eşit süreli hareket, animasyon/olay süreleri ve çalışma sırasında FPS değişimi. Yalnızca `frame_speed()` sonucunu kontrol etmek yeterli değil.
- Uygulama: `SimulationClock` monotonic zamandan saniyede 30 sabit güncelleme adımı üretiyor. Hareket, AI, animasyon sayaçları, ömürler, doğma ve kabarcık üretimi bu adımlar içinde ilerliyor; çizim FPS'e göre ayrı çalışıyor. FPS'e bağlı hız çarpanı kaldırıldı. HUD zamanı gerçek simülasyon saniyesi olarak ilerliyor; duraklatma süresi devam ederken telafi edilmiyor. Işık huzmeleri simülasyonun rastgele sayı akışını tüketmiyor ve aynı simülasyon anında aynı görünümü üretiyor.
- Sonuç: Kontrollü saatle 5, 15, 20, 30, 45 ve 60 FPS koşularında tüm 10 canlı türünün konumları, yönleri, davranış/animasyon sayaçları ve rastgele sayı durumu eşit bulundu. Koşu sırasında FPS değişimi, 100 ms çizim gecikmesi, uzun duraklatma ve devam etme doğrulandı. 60 saniyelik koşularda canlıların ömürlerinin dolması ve yerlerine yenilerinin doğması 5/60 FPS arasında aynı sonucu verdi. 21 test, 18 Python dosyasının sözdizimi kontrolü ve `git diff --check` geçti. Bu adım için gerçek terminalde görsel kontrol yapılmadı.
- Sınır: Simülasyon güncellemeleri 30 Hz'dir; 45/60 FPS çizimlerinde ara konum interpolasyonu yapılmıyor.

## İlk davranış incelemesi sırasında doğrulanan durum

- `python3 -m unittest discover -s tests -v`: 10 test geçti.
- Köpekbalığı ve kabarcığın güncelleme hız çarpanını uygulamadığı küçük davranış kontrolleriyle doğrulandı.
- Menüdeki 29 değerinin kayıt normalizasyonunda 28'e dönüştüğü doğrulandı.
- Gerçek terminalde görsel/etkileşimli kontrol yapılmadı.
- Bu takip dosyasının oluşturulduğu aşamada uygulama kodunda düzeltme yapılmadı.

## Görsel inceleme — düzeltme takibi

Bu bulgular kaynak kod ve sahte terminal çizim kontrollerine dayanır. G1–G10 kod düzeltmeleri ve otomatik kontroller tamamlandı; gerçek terminalde görsel/font değerlendirmesi henüz yapılmadı. Her düzeltmenin uygulaması ve doğrulaması ilgili maddede kayıtlıdır. Kontroller obje yönlerini, üst üste bindirmeyi, küçük/normal terminal boyutlarını ve temaları kapsar.

### G1. Yılan balığında tekrarlanan kafalar

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `entities.py::Eel.__init__`, `art.py::EEL_R` / `EEL_L`.
- Sorun: Kafa içeren çizimin tamamı 2–5 kez tekrarlanıyor; tek uzun canlı yerine `…º>…º>…º>` şeklinde bir dizi oluşuyor.
- Hedef: Tek kafa ve uzatılabilir bir gövde; sol yön tüm şeklin doğru aynası olmalı.
- Doğrulama: 2–5 segmentin her birinde iki yön için kafa sayısı, toplam genişlik ve aynalama.
- Uygulama: Gövde ve kafa `art.py` içinde ayrıldı. `build_eel_art()` yalnızca gövdeyi tekrar ediyor, tek kafa ekliyor ve sol yön için tamamını aynalıyor. Simülasyon çizimi bu oluşturucuyu kullanıyor; menünün tek segmentli `EEL_R` / `EEL_L` çizimleri korunuyor.
- Sonuç: Regresyon testi düzeltmeden önce her uzunlukta birden fazla kafa bulunduğunu gösterdi. Düzeltmeden sonra 2–5 segment, iki yön, kafa sayısı, gövde uzunluğu ve aynalama doğrulandı. 24×8 sahte terminalde iki kenardan kırpma ve iki tema test edildi. 23 test ve 19 Python dosyasının sözdizimi kontrolü geçti. Gerçek terminalde görsel kontrol yapılmadı.

### G2. Balina fıskiyesinin konumu

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `entities.py::Whale.emit_spout`, `art.py::WHALE_R` / `WHALE_L`.
- Sorun: Fıskiye `W // 2` konumundan çıkıyor. Sağ çizimde merkez 30, hava deliğindeki `^` ise 47. sütunda; yaklaşık 17 sütun kayma var.
- Hedef: Fıskiye her iki yönde de çizimdeki hava deliğinden çıkmalı.
- Doğrulama: Sağ/sol çizimde kaynak koordinatı, dikey konum ve kabarcık ayarının korunması. Kabarcıkların mevcut küçük rastgele saçılması hesaba katılmalı.
- Uygulama: Fıskiyenin yatay merkezi, kullanılan sağ/sol çizimin üst satırındaki `^` hava deliğinden hesaplanıyor. Beş kabarcık, küçük rastgele saçılma ve bekleme süresi korunuyor.
- Sonuç: Yeni test düzeltmeden önce iki yönde de kaymayı gösterdi. İki yön, üç yatay konum (ekran kenarları dahil), saçılmanın alt/orta/üst değerleri, çıkış yüksekliği ve bekleme süresi doğrulandı. Kabarcık ayarı açık/kapalı simülasyon regresyon testi de geçti. Toplam 25 test ve değişen Python dosyalarının sözdizimi kontrolü geçti. Gerçek terminalde görsel kontrol yapılmadı.

### G3. Yüzen canlıların kuma girmesi

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `entities.py::Shark.update`, `Whale.update`, `Turtle.update`; `environment.py::draw_sand`.
- Sorun: Alt sınırlar kum başlangıcına göre belirlenmiyor. 24 satırlık sahnede kum 21'de başlarken köpekbalığı 22'ye, balina 23'e, kaplumbağa 21'e kadar çizilebiliyor. Canlılar kumdan sonra çizildiği için kumu örtüyor.
- Hedef: Bu yüzen canlıların alt kenarı su bölgesinde kalmalı. Kumda yaşayan yengecin davranışı korunmalı.
- Doğrulama: Obje yüksekliği, en alt konum, küçük terminal ve yeniden boyutlandırma; sığmayan büyük çizimler için tutarlı davranış belirlenmeli.
- Uygulama: Köpekbalığı, balina ve kaplumbağanın doğma/güncelleme konumları üstte iki, dipte üç satır ayıran ortak `clamp_swim_y()` sınırını kullanıyor. Balina ve kaplumbağada gerçek çizim yüksekliği kaydediliyor. `draw_swimming_art()` çizim sırasında da konumu sınırlar; çok kısa terminalde alt kısmı su alanına kırpar. Böylece duraklatmada veya iki simülasyon adımı arasındaki resize da kumu bozamıyor. Pencere yeniden büyüyünce tam şekil çizilebiliyor; yengeç kumda kalıyor.
- Sonuç: Regresyon testleri düzeltmeden önce taşmayı gösterdi. Üç canlı, iki yön, en derin doğma konumu, uç hedef derinlikleri ve farklı animasyon zamanları test edildi. İki temada 24×100 → 12×40 → 8×30 → 4×10 → 32×100 yeniden boyutlandırma dizisi güncelleme olmadan çizildi; üç kum satırının korunması ve tekrar büyüyünce görünürlük doğrulandı. Yengecin dipteki iki satırlık yerleşimi korundu. 28 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminal kontrolü yapılmadı.

### G4. Kaplumbağanın kabarcık çıkış noktası

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `entities.py::Turtle.emit_bubble`, `art.py::TURTLE_R` / `TURTLE_L`.
- Sorun: Kaynak daima `x + 2`; yön ve başın konumu dikkate alınmıyor. Sağa giderken kabarcık gövdenin arkasından çıkıyor.
- Hedef: Kabarcık iki yönde de baş/ağız çevresinden çıkmalı.
- Doğrulama: Yöne bağlı yatay ve dikey kaynak koordinatları; rastgele saçılma dikkate alınmalı.
- Uygulama: Kaynak sütunu sağ/sol çizimdeki ağız işaretinden (`>` / `<`) alınıyor. Kabarcık, ağız çizimini örtmeden yükselmesi için başın bir satır üstünde doğuyor. Mevcut küçük rastgele saçılma ve üretim bekleme süresi korunuyor.
- Sonuç: Yeni test düzeltmeden önce iki yöndeki kaynak hatasını gösterdi. İki yön, üç yatay konum (kenarlar dahil), saçılmanın alt/orta/üst değerleri, başa göre çıkış yüksekliği ve bekleme süresi doğrulandı. Toplam 30 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminalde görsel kontrol yapılmadı.

### G5. Denizanasının uygulanmayan parlaklık animasyonu

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `entities.py::Jellyfish.draw`.
- Sorun: `bright` hesaplanıyor fakat çizim renklerine uygulanmıyor. `pulse_t = 0` ve `pi/2` için aynı renkler çiziliyor.
- Hedef: Tema renklerini koruyan görünür bir parlaklık döngüsü; gövde/dokunaç renk ilişkisi korunmalı.
- Doğrulama: Farklı pulse evrelerindeki RGB ve terminal paleti sonuçları, renk sınırları ve tema değişimi. RGB farkının 256 renk dönüşümünde görünür kaldığı kontrol edilmeli.
- Uygulama: Sinüs döngüsü temanın denizanası rengine %55–100 parlaklık olarak uygulanıyor. Beş seviye kullanılarak tema başına en fazla 10 gövde/dokunaç renk-öznitelik birleşimi üretiliyor. Dokunaçlar gövdeden koyu tutuluyor; katsayı, mono temada da soluk/parlak uçların ayrı terminal renklerine dönüşeceği şekilde ayarlandı. Çizim simülasyon durumunu ilerletmiyor.
- Sonuç: Yeni testler önce sabit kalan renkleri gösterdi; ilk düzeltmede mono dokunaçlarının aynı palet rengine düştüğünü de yakaladı. Son durumda altı temanın üç animasyon karesinde gövde/dokunaçların soluk → parlak → soluk RGB ve 256 renk dönüşümü doğrulandı. Şekiller, bold/dim ilişkisi, kanal sınırları, 300 faz örneğinde sınırlı renk sayısı ve çizimin durumu değiştirmemesi kontrol edildi. Toplam 32 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminalde görsel kontrol yapılmadı.

### G6. Manta ve büyük balıklarda aynalama hizası

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `art.py::_mirror`, `RAY_R` / `RAY_L`, `_FISH_RAW` içindeki `büyük` ve `dev`.
- Sorun: Bu şekillerde üst satır 9, gövde 10 karakter. Satırları kendi genişlikleriyle aynalamak sol yönde üst bölümü gövdeye göre bir sütun kaydırıyor.
- Hedef: Çok satırlı şekiller ortak genişlik etrafında aynalanmalı. Tek satırlı çizimler ve mevcut veri yapıları korunmalı.
- Doğrulama: Ortak tuval üzerinde sağ/sol hücre koordinatları. Yalnızca çift aynalama testi yeterli değil; mevcut 20 balığın çift aynalama kontrolü bu hataya rağmen geçiyor.
- Uygulama: `_pad_art()` satırları ortak genişliğe tamamlıyor; `_mirror()` tüm şekli aynı eksende aynalıyor. `FISH_DB` sağ/sol metinleri eşit genişlikte üretiliyor ve dört alanlı veri yapısı korunuyor. Manta satırları da ortak tuval üzerinden aynalanıyor. Tek satırlı şekillerin görünümü değişmiyor.
- Sonuç: Yeni testler önce büyük/dev balıkların ve mantanın eşit olmayan satır genişliklerini, kayan üst parçaları ve boş satır aynalama hatasını yakaladı. Düzeltmeden sonra mantanın üst satırı ve büyük balıkların süs konumları beklenen sabit metinlerle kontrol edildi. Balığın gerçek yön çevirme işleminde hiza ve boyutlar doğrulandı; tüm 20 balık, beş yönlü büyük canlı çizimi ve iki yengeç karesinde ortak genişlik ve çift aynalama kontrolleri geçti. Toplam 35 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminalde görsel kontrol yapılmadı.

### G7. Obje boşluklarının arka planı silmesi

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `entities.py::Turtle.draw`, `Crab.draw`, `Octopus.draw`, `Jellyfish.draw`, `MantaRay.draw`.
- Sorun: Satırlar kenar ve boş alanlarıyla birlikte yazılıyor; arka plandaki dekor, kum ve diğer canlılar dikdörtgen alanlar halinde silinebiliyor. Kontrolde kaplumbağa 31, yengeç 4, ahtapot 10, denizanası 14, manta 21 boş hücre yazdı.
- Hedef: Çizim dışındaki boşluklar şeffaf kalmalı. Gövde içlerinin opak mı şeffaf mı olacağı şekle göre belirlenmeli; bütün boşlukları körlemesine kaldırmak gövdede arka plan sızıntısı yaratabilir.
- Doğrulama: Desenli arka plan ve başka bir obje üzerinde her animasyon karesi ve iki yön; çevre boşlukları ile gövde içleri ayrı kontrol edilmeli.
- Uygulama: `draw_art_shape()` dış boşlukları şeffaf bırakıyor; seçili gövde satırlarında sadece ilk/son dolu karakter arasını opak çiziyor. Kaplumbağanın gövdesi, ahtapotun başı ve mantanın gövde içleri korunuyor. Ahtapot kolları, denizanası dokunaçları ve manta kanatları arasındaki dış boşluklar arkadaki sahneyi gösteriyor. Yengecin çevre boşlukları kumu silmiyor. Kaplumbağanın su bölgesine kırpılması ve denizanasının farklı gövde/dokunaç renkleri korunuyor.
- Sonuç: Desenli arka planda iki tema, iki ekran boyutu, sol/sağ kenar kırpması, tüm animasyon kareleri ve yönlü canlılarda iki yön için hücre bazlı kontroller yapıldı. Yeni test düzeltmeden önce 156 senaryoda arka plan silinmesini gösterdi; son durumda dış alanlar ve kol aralıkları korunurken tanımlı gövde içleri opak kaldı. Toplam 36 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminalde görsel kontrol yapılmadı.

### G8. Başlık ile klavye açıklamalarının çakışması

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `hud.py::draw_hud`.
- Sorun: Başlık ve sağdaki tuş açıklamaları aynı satırda birbirinin alanına giriyor. Kontrolde 80 sütunda 22 karakterlik çakışma bulundu; 120 sütunda bile 2 karakter çakışıyor.
- Hedef: Ekran genişliğine göre başlık ve durum/kısayol alanları çakışmadan yerleşmeli; dar ekranda öncelikler açık olmalı.
- Doğrulama: 40, 60, 80 ve 120 sütunda normal/duraklatılmış durum; yazılan alanların kesişmemesi.
- Uygulama: Önce temel başlık ve durum/kısayol alanları sığdırılıyor, kalan alana göre uzun/orta/kısa başlık seçiliyor. Kontroller sağda ayrı bir alanda çiziliyor; dar ekranda açıklamalar kısalıyor. İki alan arasında en az bir sütun bırakılıyor. Duraklatma durumu ve devam tuşu normal boyutlarda korunuyor.
- Sonuç: Yeni test düzeltmeden önce normal/duraklatılmış durumlarda çakışmayı gösterdi. İki temada 40, 60, 80 ve 120 sütunda alanların ayrıklığı, sınırlar, başlık ve temel kontroller doğrulandı. 1–19 sütunlarda sınır dışı yazma olmaması ve HUD kapalıyken hiç çizim yapılmaması kontrol edildi. Toplam 39 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminal kontrolü yapılmadı. G9'daki istatistik/yüzey çakışması ve G10'daki geniş glifler ayrı açık işler olarak duruyor.

### G9. İstatistik satırının su yüzeyini örtmesi

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal kontrolü bekliyor.
- Konum: `hud.py::draw_hud`, `environment.py::draw_surface`, `sim.py` çizim sırası.
- Sorun: Normal boyutta istatistikler ve su yüzeyinin ilk katmanı aynı 1. satıra çiziliyor. HUD sonradan yazıldığı için dalgaları siliyor.
- Hedef: HUD için ayrılan satırlar ile su yüzeyi ayrılmalı; küçük ekranda yeni çakışmalar oluşmamalı.
- Doğrulama: HUD açık/kapalı, duraklatma, küçük/normal ekran ve yüzeyin iki katmanının görünürlüğü.
- Uygulama: `hud_height()` HUD için ayrılan satır sayısını belirliyor; simülasyon su yüzeyini bu alanın altına yerleştiriyor. Normal boyutta başlık 0, istatistikler 1, su yüzeyi 2–3. HUD kapalıyken yüzey önceki 1–2 konumunu kullanıyor. 4–6 satırlık pencerelerde istatistik gizleniyor, daha kısada HUD çizilmiyor. Yüzey katmanları kumun başladığı satıra gelirse çizilmiyor.
- Sonuç: Yeni entegrasyon testi eski durumda HUD/yüzey ve çok kısa pencerelerde yüzey/kum çakışmalarını yakaladı. Gerçek simülasyon çizim akışında iki tema, 4/5/6/7/8/12/24 satır, HUD açık/kapalı ve normal/duraklatılmış kareler için HUD, yüzey ve kum satırlarının ayrılığı doğrulandı. Toplam 40 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti. Gerçek terminalde görsel kontrol yapılmadı. G10 geniş glif/hücre hesabı açık kalıyor.

### G10. Unicode karakterlerin hücre genişliği

- [x] Düzeltildi ve otomatik testle doğrulandı; gerçek terminal/font kontrolü bekliyor.
- Konum: `core/terminal.py::safeadd`, `hud.py::draw_hud`, `art.py::ANCHOR_ART`.
- Sorun: Hizalama ve kırpma Python karakter sayısına dayanıyor. HUD emojileri ve çapadaki `⚓` pek çok terminalde iki hücre kaplıyor; hesaplanan genişlik ile ekrandaki genişlik farklılaşıyor. Gerçek görünüm terminal/fonta bağlı.
- Hedef: Terminal hücresi genişliğine göre hizalama/kırpma veya uygun dar karakter alternatifleri; stdlib-only tasarım korunmalı.
- Doğrulama: Çapa ve emojili HUD için dar/geniş glifler, sağ/sol kenar kırpması ve gerçek terminal/font kontrolü.
- Uygulama: Stdlib `unicodedata` ile `cell_width()` ve `clip_cells()` eklendi. `safeadd()` sol/sağ kırpmayı hücre üzerinden yapıyor; yarım geniş glif çizilmiyor, sol kenardaki kesik glifin kalan hücresi boş bırakılarak sonraki metin hizası korunuyor. Birleşen aksanlar görünür taban karakterle tutuluyor. ASCII hızlı yolu ve karakter genişliği önbelleği var. HUD başlık/kontrol hesabı ve dekor genişlikleri hücre üzerinden hesaplanıyor; istatistikler karakter sayısıyla önceden kesilmiyor. Çapadaki çift genişlikli `⚓`, tek hücreli `O` halkasıyla değiştirildi.
- Sonuç: Yeni testler önce emojili HUD taşmasını, iki kenardaki yanlış kırpmayı, kopan aksanları ve çapanın geniş glifini gösterdi. ASCII/Türkçe, birleşen işaretler, CJK/tam genişlikli karakterler, emoji, negatif konumlar ve çok dar pencere testleri geçti. On canlı ikonunun bulunduğu istatistik satırı 10/20/40/80/120 sütunda normal/duraklatılmış durumlarda hücre sınırları içinde kaldı. Toplam 48 test, 22 Python dosyasının sözdizimi kontrolü ve `git diff --check` geçti.
- Sınır: Belirsiz (East Asian Ambiguous) karakterler bir hücre sayılıyor. Yardımcılar projedeki tek karakterli ikonlar ve birleşen aksanları destekliyor; fonta özgü emoji/ZWJ dizileri için tam grapheme çözümleyici değil. Gerçek terminal/font kontrolü yapılmadı.

### G11. Son curses kontrolünde bulunan dar menü başlığı taşması

- [x] Düzeltildi; otomatik test ve gerçek curses PTY kontrolü geçti.
- Konum: `menu.py::draw_menu_frame`.
- Sorun: 40 sütunluk gerçek curses oturumunda uzun menü başlığı satır sonundan alt satıra sarılıyor ve alt başlık alanını bozuyordu. İlk incelemedeki G1–G10 listesine son kontrolde eklendi.
- Uygulama: Menünün iç genişliğine sığan uzun/orta/kısa başlık seçiliyor. Alt başlık hücre bazında kırpılıyor; başlıklar ve ayırıcı kenarlığın içine `safeadd()` ile çiziliyor.
- Sonuç: Regresyon testi eski durumda 20/40 sütunda taşmayı gösterdi; 8×20, 12×40 ve 24×80 boyutlarında üç başlık alanının kenarlık içinde kaldığı doğrulandı. Toplam 49 test, değişen Python dosyalarının sözdizimi kontrolü ve `git diff --check` geçti.

### Son curses kontrolü

- `TERM=xterm-256color` ile gerçek curses PTY oturumunda 12×40 ve 24×80 boyutlarında menü açılışı, başlık, premium temasına geçiş, duraklatma ve devam etme hatasız tamamlandı.
- Gerçek curses imleç konumuyla `🐠12` genişliği, solda yarım kalan emoji, sağ kenarda kırpma ve birleşen aksanın bir hücrede kalması doğrulandı.
- Kullanıcı ayarları okunmadı/yazılmadı; test doğrudan varsayılan yapılandırmayla menü ve simülasyon fonksiyonlarını çalıştırdı.
- PTY kontrolü kullanıcı terminalindeki fontun görünümünü değerlendirmez; gerçek fontla gözle kontrol hâlâ yapılmadı.

### Görsel incelemede belirgin yapısal hata bulunmayanlar

- Kalan 18 balık çeşidinde G6'daki genişlik kaynaklı aynalama sorunu görülmedi.
- Kabarcıkların tek karakterlik şekillerinde belirgin hata bulunmadı; kaynak konumları G2 ve G4 kapsamında.
- Mercan çeşitleri, anemonlar, denizyıldızı, sandık, kaya ve kafatasında doğrudan doğrulanan yapısal hata bulunmadı. Çapa G10 kapsamında.
- Köpekbalığı ve balinanın çizim maskeleri mevcut sağ/sol şekillerin dolu karakterlerini kaybetmiyor.
- İnceleme sonunda mevcut 21 otomatik test geçti. Bu sonuç, yukarıdaki açık görsel sorunların doğrulandığı veya çözüldüğü anlamına gelmiyor; düzeltmelere özel regresyon kontrolleri eklenecek.
