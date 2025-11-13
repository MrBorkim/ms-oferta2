# Oferta Generator API - FastAPI

Szybkie i wydajne API do generowania ofert w formatach DOCX, PDF i JPG z szablonów.

## Funkcje

- ✅ Generowanie ofert z szablonów DOCX
- ✅ Automatyczne wstawianie produktów z folderu `produkty/`
- ✅ Zamiana placeholderów ({{KLIENT(NIP)}}, {{temat}}, itp.)
- ✅ Konwersja DOCX → PDF
- ✅ Konwersja DOCX → JPG (100 DPI)
- ✅ Asynchroniczne przetwarzanie (szybkie!)
- ✅ REST API z automatyczną dokumentacją

## Instalacja

### 1. Wymagania systemowe

**Na serwerze Linux (Ubuntu/Debian):**
```bash
# Zainstaluj LibreOffice (do konwersji PDF)
sudo apt-get update
sudo apt-get install -y libreoffice poppler-utils

# Zainstaluj Python 3.11+
sudo apt-get install -y python3.11 python3.11-venv python3-pip
```

**Na macOS:**
```bash
brew install libreoffice poppler
```

**Na Windows:**
- Zainstaluj Microsoft Word (docx2pdf używa COM API)
- Lub zainstaluj LibreOffice

### 2. Instalacja zależności Python

```bash
# Stwórz virtual environment
python3 -m venv .venv

# Aktywuj (Linux/macOS)
source .venv/bin/activate

# Aktywuj (Windows)
.venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt
```

## Struktura katalogów

```
oferta-ts-ms/
├── main.py                 # Główny plik FastAPI
├── models.py               # Modele Pydantic
├── document_service.py     # Serwis generowania DOCX
├── conversion_service.py   # Serwis konwersji PDF/JPG
├── config.py               # Konfiguracja
├── requirements.txt        # Zależności
├── templates/
│   └── aidrops/
│       ├── oferta1.docx    # Szablon główny
│       └── oferta1.json    # Konfiguracja szablonu
├── produkty/               # Produkty do wstawiania
│   ├── 1.docx
│   ├── 2.docx
│   └── ...
├── output/                 # Wygenerowane pliki (auto)
└── temp/                   # Pliki tymczasowe (auto)
```

## Uruchomienie

### Rozwojowe (localhost)
```bash
python main.py
```

### Produkcyjne (serwer)
```bash
# Z auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Bez auto-reload (produkcja)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Jako usługa systemd (Linux)

Stwórz plik `/etc/systemd/system/oferta-api.service`:

```ini
[Unit]
Description=Oferta Generator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/oferta-ts-ms
Environment="PATH=/path/to/oferta-ts-ms/.venv/bin"
ExecStart=/path/to/oferta-ts-ms/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Uruchom:
```bash
sudo systemctl daemon-reload
sudo systemctl enable oferta-api
sudo systemctl start oferta-api
sudo systemctl status oferta-api
```

## Użycie API

### Endpoint: POST /api/generate-offer

**Request Body (JSON):**

```json
{
  "KLIENT(NIP)": "1234567890",
  "Oferta z dnia": "2024-11-10",
  "wazna_do": "2024-12-10",
  "firmaM": "Moja Firma Sp. z o.o.",
  "temat": "Wdrożenie systemu CRM",
  "kategoria": "IT",
  "opis": "Kompleksowe wdrożenie systemu CRM dla firmy",
  "produkty": ["1.docx", "2.docx", "3.docx"],
  "cena": 15000.00,
  "RBG": 120,
  "uzasadnienie": "Koszt obejmuje licencje, wdrożenie i szkolenia",
  "output_format": "pdf"
}
```

**Parametry:**

| Parametr | Typ | Wymagany | Opis |
|----------|-----|----------|------|
| `KLIENT(NIP)` | string | ✅ | NIP klienta |
| `Oferta z dnia` | string | ✅ | Data oferty |
| `wazna_do` | string | ✅ | Data ważności |
| `firmaM` | string | ✅ | Nazwa Twojej firmy |
| `temat` | string | ❌ | Temat zlecenia |
| `kategoria` | string | ❌ | Kategoria |
| `opis` | string | ❌ | Opis zlecenia |
| `produkty` | array | ✅ | Lista plików z `produkty/` |
| `cena` | float | ❌ | Cena usługi (PLN) |
| `RBG` | integer | ❌ | Limit roboczogodzin |
| `uzasadnienie` | string | ❌ | Uzasadnienie kosztu |
| `output_format` | string | ✅ | Format: `docx`, `pdf`, `jpg` |

**Response:**

```json
{
  "success": true,
  "message": "Oferta wygenerowana pomyślnie",
  "file_path": "/path/to/output/oferta_a1b2c3d4.pdf",
  "file_name": "oferta_a1b2c3d4.pdf",
  "file_size_bytes": 245678,
  "format": "pdf",
  "processing_time_seconds": 1.23
}
```

### Przykład użycia (curl)

**Generuj DOCX:**
```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "KLIENT(NIP)": "1234567890",
    "Oferta z dnia": "2024-11-10",
    "wazna_do": "2024-12-10",
    "firmaM": "Moja Firma",
    "produkty": ["1.docx", "2.docx"],
    "output_format": "docx"
  }'
```

**Generuj PDF:**
```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "KLIENT(NIP)": "1234567890",
    "Oferta z dnia": "2024-11-10",
    "wazna_do": "2024-12-10",
    "firmaM": "Moja Firma",
    "produkty": ["1.docx"],
    "output_format": "pdf"
  }'
```

**Generuj JPG (100 DPI):**
```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "KLIENT(NIP)": "1234567890",
    "Oferta z dnia": "2024-11-10",
    "wazna_do": "2024-12-10",
    "firmaM": "Moja Firma",
    "produkty": ["1.docx"],
    "output_format": "jpg"
  }'
```

### Przykład użycia (Python)

```python
import requests

url = "http://localhost:8000/api/generate-offer"

data = {
    "KLIENT(NIP)": "1234567890",
    "Oferta z dnia": "2024-11-10",
    "wazna_do": "2024-12-10",
    "firmaM": "Moja Firma Sp. z o.o.",
    "temat": "Wdrożenie CRM",
    "produkty": ["1.docx", "2.docx"],
    "cena": 15000.00,
    "output_format": "pdf"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Sukces: {result['success']}")
print(f"Plik: {result['file_name']}")
print(f"Czas: {result['processing_time_seconds']}s")

# Pobierz plik
download_url = f"http://localhost:8000/api/download/{result['file_name']}"
file_response = requests.get(download_url)

with open(f"downloaded_{result['file_name']}", "wb") as f:
    f.write(file_response.content)
```

### Inne endpointy

**Lista dostępnych produktów:**
```bash
curl http://localhost:8000/api/list-produkty
```

**Health check:**
```bash
curl http://localhost:8000/health
```

**Pobieranie pliku:**
```bash
curl http://localhost:8000/api/download/oferta_a1b2c3d4.pdf --output oferta.pdf
```

## Dokumentacja API

Automatyczna dokumentacja Swagger dostępna pod:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Optymalizacja wydajności

### 1. Użyj więcej workerów (produkcja)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8
```

### 2. Nginx jako reverse proxy
```nginx
upstream oferta_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://oferta_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Docker (opcjonalnie)
Stwórz `Dockerfile`:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build i uruchom:
```bash
docker build -t oferta-api .
docker run -p 8000:8000 -v $(pwd)/produkty:/app/produkty oferta-api
```

## Troubleshooting

### LibreOffice nie znaleziony
```bash
# Sprawdź czy zainstalowany
which libreoffice

# Jeśli nie, zainstaluj
sudo apt-get install libreoffice
```

### Błąd konwersji PDF
```bash
# Sprawdź poppler-utils
which pdftoppm

# Jeśli nie, zainstaluj
sudo apt-get install poppler-utils
```

### Permisje do zapisu
```bash
# Ustaw właściciela katalogów
sudo chown -R $USER:$USER output/ temp/
chmod -R 755 output/ temp/
```

## Wydajność

Na serwerze z 4 CPU i 8GB RAM:
- **DOCX:** ~0.3-0.5s
- **PDF:** ~1.0-1.5s
- **JPG:** ~1.5-2.5s

Z 4 workerami można obsłużyć ~100-200 requestów/minutę.

## Licencja

Projekt prywatny - Wszystkie prawa zastrzeżone.
