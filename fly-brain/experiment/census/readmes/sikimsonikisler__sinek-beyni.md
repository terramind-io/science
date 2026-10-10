# Sinek beyni

Meyve sineğinin gerçek beyin devresiyle çalışan bir tarayıcı oyunu. Sineği sen yürütüyorsun; yiyip yememesine FlyWire kablo şemasından çıkarılmış 1.538 nöronluk bir devre karar veriyor. Devre, sayfa açıkken tarayıcında canlı simüle ediliyor.

**Oyna:** https://sikimsonikisler.github.io/sinek-beyni/

## Nasıl oynanır

- Yön tuşları, WASD ya da dokunup sürükleyerek sineği agar kabında gezdir.
- Sinek bir yiyeceğe konunca tat nöronları ateşler. Hortumu uzatan MN9 nöronu 45 Hz'yi geçerse sinek yer.
- Şeker ve bal enerji verir. Acılı yiyecekler zehirlidir; sağlam beyin çoğunu kendiliğinden reddeder.
- Enerjin biterse ya da raket üç kez isabet ederse oyun biter.
- **Beyin cerrahı:** Roundup nöronlarını ya da acı frenini sustur, davranışın nasıl değiştiğini gör.
- **Laboratuvar:** Tatlı, acı ve su tat nöronlarını kaydırıcılarla doğrudan uyar, MN9'u izle.

## Ne gerçek, ne oyun kuralı

| Gerçek | Oyun kuralı |
|---|---|
| FlyWire v630'dan çıkarılmış 1.538 nöron ve 106.756 bağlantı | Sineği sen yürütüyorsun, yürüme devresi simüle edilmiyor |
| Shiu et al. (2024) LIF modelinin kuralları, 0,1 ms adımlarla | Yiyeceklerin tat nöronlarını uyarma hızları |
| Tatlı, acı ve su tat nöronları; MN9; Roundup; acı freni | 45 Hz yeme eşiği, enerji, zehir ve raket |
| Susturma düğmeleri nöron çıkışlarını gerçekten kapatıyor | |

**Acı freni** bu proje için bulundu. Acıyla ateşleyip tatlı → MN9 yoluna güçlü baskılayıcı sinaps yapan 11 nöron. Sustuğunda, tatlı 160 Hz + acı 100 Hz koşulunda MN9 yaklaşık 31 Hz'den 95 Hz'ye çıkıyor; sadece acıyla ise hâlâ beslenme başlamıyor.

## Doğrulama

- Çıkarılan alt devre, aynı rastgelelik tohumuyla tam beyinle (127.400 nöron) birebir aynı MN9 sonucunu veriyor. `game/export_brain.py` bunu her çalıştırmada kontrol ediyor.
- Tarayıcı motoru (`game/brain_core.js`), Python sürümüyle 9 koşulda en fazla ~5 Hz farkla uyuşuyor: `npm test`.
- Python simülatörü, Shiu et al.'ın orijinal Brian2 çıktılarıyla r = 0,9997 uyuşuyor. Ayrıntılar `kopru/README.md` dosyasında.

## GitHub Pages ile yayınla

Repo → **Settings** → **Pages** → Source: *Deploy from a branch*, Branch: `main`, klasör `/ (root)` → **Save**. Birkaç dakika sonra oyun `https://KULLANICI_ADIN.github.io/sinek-beyni/` adresinde açılır.

## Proje yapısı

| Yol | Görevi |
|---|---|
| `index.html` | Derlenmiş, tek dosyalık oyun (internetsiz de çalışır) |
| `game/template.html` | Oyun arayüzü ve mantığı; veri ve motor derlemede eklenir |
| `game/brain_core.js` | Tarayıcıdaki LIF motoru (Brian2 semantiğiyle) |
| `game/brain_data.json` | Dışa aktarılmış beyin devresi |
| `game/export_brain.py` | Devreyi FlyWire verisinden yeniden çıkarır |
| `game/build.py` | Şablon + motor + veri → `index.html` |
| `tests/` | Motor doğrulaması ve başsız tarayıcı testi |
| `kopru/` | Python simülatörü ve "Köprü" nöroprotez deneyi |

## Yeniden üretme

```bash
# Oyunu derle ve test et
python3 game/build.py
npm install && npm test

# Beyin devresini sıfırdan çıkar (FlyWire verisi ~370 MB)
python3 -m venv .venv && source .venv/bin/activate
pip install -r kopru/requirements.txt
(cd kopru && ./setup_data.sh)
python3 game/export_brain.py && python3 game/build.py
```

## Kaynaklar ve atıf

- Shiu, P. K. et al. (2024). *A Drosophila computational brain model reveals sensorimotor processing.* Nature. Kod ve veri: [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model) (MIT lisansı)
- Dorkenwald, S. et al. (2024). *Neuronal wiring diagram of an adult brain.* Nature (FlyWire)

Bağlantı verisi ve nöron kimlikleri Shiu et al. deposundan türetildi; lisans metni `THIRD_PARTY_NOTICES.md` dosyasında.
