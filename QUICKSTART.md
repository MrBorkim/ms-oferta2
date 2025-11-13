# Quick Start Guide - 2 minuty do pierwszej oferty

## Lokalne testowanie (development)

### 1. Instalacja (30 sekund)

```bash
# Zainstaluj zależności
pip install -r requirements.txt

# Na Linuxie dodatkowo:
sudo apt-get install libreoffice poppler-utils
```

### 2. Uruchomienie (5 sekund)

```bash
python main.py
```

Serwer startuje na: http://localhost:8000

### 3. Test API (30 sekund)

**Otworz nowy terminal i wyślij zapytanie:**

```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "KLIENT(NIP)": "1234567890",
    "Oferta z dnia": "2024-11-10",
    "wazna_do": "2024-12-10",
    "firmaM": "Moja Firma Sp. z o.o.",
    "produkty": ["1.docx", "2.docx"],
    "output_format": "docx"
  }'
```

**Odpowiedź:**
```json
{
  "success": true,
  "message": "Oferta wygenerowana pomyślnie",
  "file_name": "oferta_abc123.docx",
  "file_size_bytes": 154234,
  "format": "docx",
  "processing_time_seconds": 0.45
}
```

### 4. Pobierz plik

```bash
# Pobierz wygenerowany plik
curl http://localhost:8000/api/download/oferta_abc123.docx --output oferta.docx
```

✅ **Gotowe!** Masz wygenerowaną ofertę w `oferta.docx`

---

## Testowanie z Pythonem

Stwórz plik `quick_test.py`:

```python
import requests

# Dane oferty
payload = {
    "KLIENT(NIP)": "1234567890",
    "Oferta z dnia": "2024-11-10",
    "wazna_do": "2024-12-10",
    "firmaM": "Moja Firma",
    "temat": "Wdrożenie CRM",
    "kategoria": "IT",
    "opis": "Kompleksowe wdrożenie systemu CRM",
    "produkty": ["1.docx", "2.docx"],
    "cena": 15000.00,
    "RBG": 120,
    "uzasadnienie": "Koszt obejmuje licencje i wdrożenie",
    "output_format": "pdf"  # DOCX, PDF lub JPG
}

# Wygeneruj ofertę
response = requests.post(
    "http://localhost:8000/api/generate-offer",
    json=payload
)

result = response.json()

if result["success"]:
    print(f"✅ Sukces! Plik: {result['file_name']}")
    print(f"⏱️  Czas: {result['processing_time_seconds']}s")

    # Pobierz plik
    file_url = f"http://localhost:8000/api/download/{result['file_name']}"
    file_data = requests.get(file_url)

    with open(f"downloaded_{result['file_name']}", "wb") as f:
        f.write(file_data.content)

    print(f"💾 Zapisano jako: downloaded_{result['file_name']}")
else:
    print(f"❌ Błąd: {result['message']}")
```

Uruchom:
```bash
python quick_test.py
```

---

## Wszystkie formaty w jednym teście

```python
import requests
import time

formats = ["docx", "pdf", "jpg"]
api_url = "http://localhost:8000/api/generate-offer"

for fmt in formats:
    print(f"\n🔄 Generowanie {fmt.upper()}...")

    payload = {
        "KLIENT(NIP)": "1234567890",
        "Oferta z dnia": "2024-11-10",
        "wazna_do": "2024-12-10",
        "firmaM": "Test Firma",
        "produkty": ["1.docx"],
        "output_format": fmt
    }

    start = time.time()
    response = requests.post(api_url, json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['file_name']} ({elapsed:.2f}s)")
    else:
        print(f"   ❌ Błąd: {response.status_code}")
```

---

## Testowanie kompletne

```bash
# Uruchom wszystkie testy
python test_api.py
```

---

## Swagger UI (interaktywna dokumentacja)

Otwórz w przeglądarce:
```
http://localhost:8000/docs
```

Możesz tam:
- ✅ Testować wszystkie endpointy
- ✅ Zobaczyć schematy JSON
- ✅ Wypróbować różne formaty
- ✅ Pobrać pliki

---

## Sprawdzanie dostępnych produktów

```bash
curl http://localhost:8000/api/list-produkty
```

Odpowiedź:
```json
{
  "success": true,
  "count": 8,
  "produkty": ["1.docx", "2.docx", "3.docx", "4.docx", "5.docx", "6.docx", "7.docx", "8.docx"]
}
```

---

## Tips & Tricks

### 1. Szybkie testowanie bez curl

Otwórz http://localhost:8000/docs i kliknij "Try it out"

### 2. Automatyczne pobieranie pliku w curl

```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{"KLIENT(NIP)":"123","Oferta z dnia":"2024-11-10","wazna_do":"2024-12-10","firmaM":"Test","produkty":["1.docx"],"output_format":"docx"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['file_name'])" \
  | xargs -I {} curl http://localhost:8000/api/download/{} --output oferta.docx
```

### 3. Generowanie wielu ofert naraz

```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/generate-offer \
    -H "Content-Type: application/json" \
    -d "{\"KLIENT(NIP)\":\"$i\",\"Oferta z dnia\":\"2024-11-10\",\"wazna_do\":\"2024-12-10\",\"firmaM\":\"Firma $i\",\"produkty\":[\"1.docx\"],\"output_format\":\"pdf\"}"
  echo ""
done
```

---

## Deployment na serwer

Szybki deployment (5 minut):

```bash
# 1. Skopiuj pliki na serwer
scp -r . user@server:/var/www/oferta-ts-ms

# 2. SSH do serwera
ssh user@server

# 3. Setup
cd /var/www/oferta-ts-ms
sudo apt-get install -y libreoffice poppler-utils
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Uruchom
python main.py
```

Pełna instrukcja: zobacz `INSTALL_SERVER.md`

---

## Częste problemy

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "LibreOffice not found" (przy konwersji PDF)
```bash
# Linux
sudo apt-get install libreoffice

# macOS
brew install libreoffice

# Windows - zainstaluj MS Word lub LibreOffice
```

### "Permission denied" na katalog output/
```bash
chmod 777 output/ temp/
```

### Port 8000 zajęty
```bash
# Zmień port
python main.py --port 8001

# Lub w config.py zmień PORT = 8001
```

---

## Next Steps

1. **Dostosuj szablon** - edytuj `templates/aidrops/oferta1.docx`
2. **Dodaj produkty** - wrzuć pliki `.docx` do `produkty/`
3. **Deployment** - zobacz `INSTALL_SERVER.md`
4. **Docker** - `docker-compose up -d`

---

## Support

📧 W razie problemów sprawdź:
- `README.md` - pełna dokumentacja
- `INSTALL_SERVER.md` - instalacja na serwerze
- http://localhost:8000/docs - dokumentacja API
