# 🎓 Digital SAT Prep AI — Kurulum Rehberi

## Gereksinimler
- Python 3.8+
- Anthropic API anahtarı (https://console.anthropic.com)

## Kurulum (3 adım)

### 1. Kütüphaneleri kur
```bash
pip install flask anthropic flask-cors
```

### 2. API anahtarını ayarla
`app.py` dosyasını aç, şu satırı bul:
```python
api_key=os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
```
`YOUR_API_KEY_HERE` yerine kendi anahtarını yaz.

**Ya da** terminal'de ortam değişkeni olarak ver:
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

### 3. Çalıştır
```bash
python app.py
```
Tarayıcıda aç: **http://localhost:5000**

---

## Özellikler

| Buton | Ne Yapar |
|-------|----------|
| ✍️ Grammar Fix | Cümledeki tüm grammatik hataları bulur, düzeltir, açıklar |
| 📖 Vocabulary | Kelime anlamı, IPA, eş/zıt anlamlılar, SAT notu |
| 🔊 Pronounce | Fonetik transkripsiyon + tarayıcı sesli okuma |
| 📰 Article Quiz | SAT-seviyesi metin → ana fikir + özet yaz → skor al |
| 🧮 SAT Questions | Her basışta yeni Math veya W&R sorusu + şıklar + açıklama |
| 📝 Grammar Exercises | Her basışta yeni konu, bitmez soru bankası |

## Dosya Yapısı
```
proje/
├── app.py       ← Python Flask backend
├── index.html   ← Frontend (app.py ile aynı klasörde olmalı)
└── README.md
```

## Notlar
- İnternet bağlantısı gerekir (Claude API çağrısı için)
- Her soru butona her basışta FARKLI konu/soru gelir
- Sorular bitmez — Claude her seferinde üretir
