# İnceleme ve düzeltme takibi

Bu liste kod incelemesinde bulunan dört sorunu ve sırayla uygulanacak düzeltmelerin kabul ölçütlerini içerir. Her adım tamamlandığında durumu ve doğrulama sonucu burada güncellenir.

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

## İnceleme sırasında doğrulanan durum

- `python3 -m unittest discover -s tests -v`: 10 test geçti.
- Köpekbalığı ve kabarcığın güncelleme hız çarpanını uygulamadığı küçük davranış kontrolleriyle doğrulandı.
- Menüdeki 29 değerinin kayıt normalizasyonunda 28'e dönüştüğü doğrulandı.
- Gerçek terminalde görsel/etkileşimli kontrol yapılmadı.
- Bu takip dosyasının oluşturulduğu aşamada uygulama kodunda düzeltme yapılmadı.
