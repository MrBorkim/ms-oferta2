# 🐺 WolfTax Oferta Generator

Generator ofert wykorzystujący **multi-file template** WolfTax. System łączy wiele plików DOCX w jedną ofertę i automatycznie organizuje output w strukturę folderów.

---

## 📁 Struktura Output

Generator tworzy zorganizowaną strukturę dla każdej oferty:

```
output/
  oferta_abc12345/
    oferta_abc12345.docx (lub .pdf)
    jpg/
      page_1.jpg
      page_2.jpg
      page_3.jpg
      ...
```

**Zalety:**
- 📄 Plik główny (DOCX/PDF) w folderze głównym
- 🖼️ Wszystkie JPG w osobnym folderze `jpg/`
- 🚀 Szybki podgląd przez przeglądarkę plików
- 📦 Łatwe archiwizowanie całej oferty

---

## 🏗️ Szablon WolfTax

Szablon składa się z **6 plików DOCX** w folderze `templates/wolftax-oferta/`:

| Plik | Rola | Kolejność |
|------|------|-----------|
| `Dok1.docx` | Strona tytułowa | 1 |
| `Doc2.docx` | Wprowadzenie | 2 |
| `doc3.docx` | Spis treści | 3 |
| **PRODUKTY** | **Wstrzykiwane tutaj** | **3.5** |
| `doc4.docx` | Podsumowanie | 4 |
| `Dok5.docx` | Warunki | 5 |
| `Dok6.docx` | Strona końcowa | 6 |

Produkty są **automatycznie wstrzykiwane** między plik `doc3.docx` (spis treści) a `doc4.docx` (podsumowanie).

---

## 🚀 Uruchomienie

### 1. Uruchom serwer WolfTax

```bash
python main_wolftax.py
```

Serwer uruchomi się na **porcie 8001** (różny od aidrops):
- 🌐 API: `http://localhost:8001`
- 📚 Dokumentacja: `http://localhost:8001/docs`

### 2. Uruchom testy

```bash
python test_api_wolftax.py
```

Testy sprawdzą:
- ✅ Health check
- ✅ Listowanie produktów
- ✅ Generowanie DOCX + JPG
- ✅ Generowanie PDF + JPG
- ✅ Generowanie samych JPG
- ✅ Listowanie wygenerowanych ofert
- ✅ Pobieranie plików

---

## 📡 Endpointy API

### `POST /api/generate-offer`

Generuje ofertę WolfTax.

**Przykład request:**

```json
{
  "NazwaFirmyKlienta": "ABC Company Sp. z o.o.",
  "Sygnatura-sprawy": "WTX/2024/11/001",
  "Temat": "Kompleksowa obsługa podatkowa",
  "Termin": "31.12.2024",
  "waznosc-oferty": "10.12.2024",
  "produkty": ["1.docx", "2.docx"],
  "Wynagrodzenie": 10000.00,
  "Szacowanyczaspracy": 80,
  "output_format": "docx"
}
```

**Pola:**
- `NazwaFirmyKlienta` (wymagane) - Nazwa firmy klienta
- `Sygnatura-sprawy` (opcjonalne) - Sygnatura sprawy
- `Temat` (wymagane) - Temat oferty
- `Termin` (opcjonalne) - Termin realizacji
- `waznosc-oferty` (wymagane) - Data ważności oferty
- `produkty` (wymagane) - Lista plików DOCX z produktami
- `Wynagrodzenie` (opcjonalne) - Wynagrodzenie w PLN
- `Szacowanyczaspracy` (opcjonalne) - Szacowany czas pracy w rbh
- `output_format` (wymagane) - Format: "docx", "pdf" lub "jpg"

**Przykład response:**

```json
{
  "success": true,
  "message": "Oferta WolfTax wygenerowana pomyślnie",
  "output_folder": "/root/MS-oferta/output/oferta_abc12345",
  "docx_path": "/root/MS-oferta/output/oferta_abc12345/oferta_abc12345.docx",
  "jpg_folder": "/root/MS-oferta/output/oferta_abc12345/jpg",
  "file_name": "oferta_abc12345.docx",
  "file_size_bytes": 245678,
  "format": "docx",
  "processing_time_seconds": 8.45,
  "jpg_count": 12
}
```

### `GET /api/list-offers`

Lista wszystkich wygenerowanych ofert.

### `GET /api/download/{folder_name}/{file_name}`

Pobiera plik główny z oferty.

### `GET /api/download-jpg/{folder_name}/{jpg_name}`

Pobiera konkretny plik JPG z folderu `jpg/`.

---

## 🔧 Konfiguracja

Ustawienia w pliku `config_wolftax.py`:

```python
# Porty (8001 dla wolftax, 8000 dla aidrops)
PORT = 8001

# Struktura plików WolfTax
WOLFTAX_FILES = [
    {"file": "Dok1.docx", "order": 1, "name": "Strona tytułowa"},
    {"file": "Doc2.docx", "order": 2, "name": "Wprowadzenie"},
    {"file": "doc3.docx", "order": 3, "name": "Spis treści"},
    {"file": "doc4.docx", "order": 4, "name": "Podsumowanie"},
    {"file": "Dok5.docx", "order": 5, "name": "Warunki"},
    {"file": "Dok6.docx", "order": 6, "name": "Strona końcowa"}
]

# Punkt wstrzyknięcia produktów
INJECTION_AFTER_FILE = "doc3.docx"

# Jakość JPG
JPG_DPI = 100
```

---

## 🆚 Różnice: WolfTax vs Aidrops

| Funkcja | Aidrops | WolfTax |
|---------|---------|---------|
| **Szablon** | Single-file (`oferta1.docx`) | Multi-file (6 plików) |
| **Port** | 8000 | 8001 |
| **Struktura output** | Płaska (`output/oferta.docx`) | Zorganizowana (`output/oferta_xxx/`) |
| **JPG folder** | Bezpośrednio w output | W podfolderze `jpg/` |
| **Injection** | Po paragrafie z opisem | Między doc3.docx a doc4.docx |

---

## 📦 Przykładowe użycie

### Przykład 1: DOCX + JPG

```python
import requests

payload = {
    "NazwaFirmyKlienta": "Test Firma Sp. z o.o.",
    "Temat": "Obsługa podatkowa",
    "waznosc-oferty": "15.12.2024",
    "produkty": ["1.docx", "2.docx"],
    "Wynagrodzenie": 8000.00,
    "output_format": "docx"
}

response = requests.post(
    "http://localhost:8001/api/generate-offer",
    json=payload
)

data = response.json()
print(f"Folder: {data['output_folder']}")
print(f"DOCX: {data['docx_path']}")
print(f"JPG count: {data['jpg_count']}")
```

### Przykład 2: Tylko JPG

```python
payload = {
    "NazwaFirmyKlienta": "Test Firma",
    "Temat": "Konsultacje",
    "waznosc-oferty": "20.12.2024",
    "produkty": ["1.docx"],
    "Szacowanyczaspracy": 20,
    "output_format": "jpg"
}

response = requests.post(
    "http://localhost:8001/api/generate-offer",
    json=payload
)
```

---

## 🛠️ Pliki systemu WolfTax

```
MS-oferta/
├── config_wolftax.py              # Konfiguracja WolfTax
├── models_wolftax.py              # Modele Pydantic
├── document_service_wolftax.py   # Łączenie multi-file templates
├── conversion_service_wolftax.py # Konwersja + organizacja folderów
├── main_wolftax.py               # FastAPI serwer
├── test_api_wolftax.py           # Testy automatyczne
└── templates/
    └── wolftax-oferta/
        ├── Dok1.docx
        ├── Doc2.docx
        ├── doc3.docx
        ├── doc4.docx
        ├── Dok5.docx
        └── Dok6.docx
```

---

## ✅ Podsumowanie

**WolfTax Generator** to:
- 🏗️ **Multi-file system** - łączy 6 plików w jedną ofertę
- 📁 **Zorganizowana struktura** - każda oferta w osobnym folderze
- 🖼️ **Automatyczne JPG** - zawsze generowane dla szybkiego podglądu
- 🚀 **Niezależny** - działa równolegle z systemem Aidrops
- 🔧 **Konfigurowalny** - łatwa modyfikacja struktury plików

**Gotowe do użycia!** 🎉
