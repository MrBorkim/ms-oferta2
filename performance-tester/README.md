# 🚀 MS-Oferta Performance Tester

Profesjonalny program do testowania wydajności aplikacji MS-Oferta z nowoczesnym webowym interfejsem użytkownika.

## 📋 Spis treści

- [Funkcje](#funkcje)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Użycie](#użycie)
- [Typy testów](#typy-testów)
- [Scenariusze testowe](#scenariusze-testowe)
- [Architektura](#architektura)
- [API](#api)

---

## ✨ Funkcje

### 🎯 Testowanie wydajności
- **3 typy testów**: Concurrent (wielowątkowy), Async (wysokowydajny), Ramp-Up (stopniowe zwiększanie obciążenia)
- **6 predefiniowanych scenariuszy**: Quick, Standard, Heavy, Stress, Spike, Endurance
- **Testowanie różnych endpointów**: Health check, generowanie DOCX/PDF/JPG
- **Konfigurowalna liczba requestów i workerów**

### 📊 Monitoring w czasie rzeczywistym
- **Monitorowanie zasobów systemowych**: CPU, RAM, Disk I/O, Network I/O
- **WebSocket live updates**: Real-time wykresy i metryki
- **Historia metryk**: Zapisywanie i analiza danych z testów

### 📈 Raporty i wizualizacje
- **Interaktywne wykresy**: Plotly.js charts z możliwością zoom i pan
- **HTML raporty**: Profesjonalne raporty z wszystkimi metrykami
- **Export do JSON**: Pełny eksport danych do dalszej analizy
- **Statystyki**: Avg, Min, Max, P50, P95, P99 response times

### 💾 Baza danych
- **SQLite database**: Przechowywanie wszystkich testów i wyników
- **Historia testów**: Dostęp do wszystkich poprzednich testów
- **Szczegółowe metryki**: Request-level i system-level data

### 🌐 Webowy interfejs
- **Nowoczesny Bootstrap UI**: Responsywny, przyjazny interfejs
- **Real-time updates**: Live monitoring podczas testów
- **Activity log**: Szczegółowy log wszystkich operacji
- **Test history**: Przeglądanie i porównywanie testów

---

## 📦 Wymagania

### System
- **Python**: 3.9 lub nowszy
- **RAM**: Minimum 4GB (zalecane 8GB+)
- **CPU**: Wielordzeniowy procesor (zalecane 4+ cores)
- **Dysk**: 1GB wolnego miejsca

### Specyfikacja testowa serwera
Program został zoptymalizowany dla serwera:
- **CPU**: 8 vCPU Cores
- **RAM**: 24 GB
- **Dysk**: 400 GB SSD
- **Sieć**: 600 Mbit/s

---

## 🔧 Instalacja

### 1. Klonowanie lub pobranie projektu

```bash
cd /home/user/ms-oferta2/performance-tester
```

### 2. Utworzenie wirtualnego środowiska

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
```

### 3. Instalacja zależności

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Konfiguracja

```bash
# Skopiuj przykładowy plik konfiguracji
cp .env.example .env

# Edytuj .env i dostosuj do swoich potrzeb
nano .env
```

**Ważne ustawienia w `.env`:**

```env
# Adres API aplikacji MS-Oferta do testowania
API_BASE_URL=http://localhost:8000

# Adres i port web dashboardu
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

## 🚀 Uruchomienie

### Standardowe uruchomienie

```bash
python run.py
```

### Z custom portem

```bash
export FLASK_PORT=5500
python run.py
```

### Dostęp do dashboardu

Otwórz przeglądarkę i wejdź na:

```
http://localhost:5000
```

Lub z zewnątrz (jeśli serwer jest dostępny):

```
http://YOUR_SERVER_IP:5000
```

---

## 📖 Użycie

### 1. Uruchomienie aplikacji MS-Oferta

Przed testowaniem upewnij się, że aplikacja MS-Oferta działa:

```bash
cd /home/user/ms-oferta2
python main.py
```

Aplikacja powinna być dostępna na `http://localhost:8000`

### 2. Uruchomienie Performance Testera

```bash
cd /home/user/ms-oferta2/performance-tester
source venv/bin/activate
python run.py
```

### 3. Konfiguracja testu w UI

1. **Nazwa testu**: Wprowadź nazwę dla identyfikacji
2. **Scenariusz**: Wybierz predefiniowany scenariusz lub custom
3. **Typ testu**: Concurrent, Async lub Ramp-Up
4. **Endpoint**: Wybierz co testować (DOCX, PDF, JPG, Health)
5. **Parametry**: Liczba requestów i max workers

### 4. Start testu

Kliknij **"Start Test"** i obserwuj:
- Real-time progress bar
- Live system metrics (CPU, Memory)
- Activity log z szczegółami
- Live charts z wykresami zasobów

### 5. Analiza wyników

Po zakończeniu testu:
- Sprawdź **Summary Metrics** (total requests, success rate, avg time)
- Zobacz **Test History** z poprzednimi testami
- **Wygeneruj raport HTML** z pełną analizą i wykresami

---

## 🔬 Typy testów

### 1. Concurrent Test (Wielowątkowy)
- Używa `ThreadPoolExecutor` do symulacji wielu użytkowników
- Najlepszy dla: średniego obciążenia, stabilnych testów
- Zalecane workers: 10-50 dla 8 vCPU

```python
# Przykład: 100 requestów, 20 workerów
Test Type: Concurrent
Requests: 100
Workers: 20
```

### 2. Async Test (Wysokowydajny)
- Używa `aiohttp` i `asyncio` dla maksymalnej wydajności
- Najlepszy dla: bardzo wysokiego obciążenia, stress testing
- Może symulować setki równoczesnych połączeń

```python
# Przykład: 500 requestów asynchronicznie
Test Type: Async
Requests: 500
```

### 3. Ramp-Up Test (Stopniowe zwiększanie)
- Stopniowo zwiększa liczbę użytkowników w czasie
- Najlepszy dla: testowania progów wydajności, znajdowania limitów
- Symuluje realistyczne wzrosty ruchu

```python
# Przykład: od 0 do 200 użytkowników w 5 minut
Test Type: Ramp-Up
Max Users: 200
Duration: 300s
```

---

## 📊 Scenariusze testowe

### 🟢 Quick Test
- **Czas trwania**: 1 minuta
- **Użytkownicy**: 10
- **Cel**: Szybka weryfikacja działania

### 🔵 Standard Load Test
- **Czas trwania**: 5 minut
- **Użytkownicy**: 50
- **Cel**: Standardowe obciążenie produkcyjne

### 🟡 Heavy Load Test
- **Czas trwania**: 10 minut
- **Użytkownicy**: 100
- **Cel**: Wysokie obciążenie

### 🟠 Stress Test
- **Czas trwania**: 15 minut
- **Użytkownicy**: 200
- **Cel**: Znajdowanie limitów systemu

### 🔴 Spike Test
- **Czas trwania**: 5 minut
- **Użytkownicy**: 300
- **Cel**: Nagły wzrost ruchu

### 🟣 Endurance Test
- **Czas trwania**: 1 godzina
- **Użytkownicy**: 50
- **Cel**: Stabilność długoterminowa

---

## 🏗️ Architektura

```
performance-tester/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main Flask application
│   ├── config.py            # Configuration settings
│   ├── database.py          # SQLite database manager
│   ├── monitor.py           # System monitoring
│   ├── load_tester.py       # Load testing engine
│   └── report_generator.py  # Report generation
├── templates/
│   └── index.html           # Web dashboard UI
├── static/
│   ├── css/                 # Custom styles
│   └── js/
│       └── dashboard.js     # Frontend JavaScript
├── database/                # SQLite database
│   └── performance.db
├── reports/                 # Generated HTML reports
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── run.py                   # Main entry point
├── .env                     # Configuration file
└── README.md               # This file
```

---

## 🔌 API

### REST Endpoints

#### GET `/api/health`
Sprawdzenie stanu aplikacji

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-13T10:30:00",
  "database": "connected",
  "monitor": "active"
}
```

#### GET `/api/system-info`
Informacje o systemie

**Response:**
```json
{
  "hostname": "server-name",
  "cpu_cores": 8,
  "cpu_threads": 8,
  "total_memory_gb": 24.0,
  "total_disk_gb": 400.0
}
```

#### POST `/api/start-test`
Rozpoczęcie testu

**Request:**
```json
{
  "test_name": "My Test",
  "scenario": "standard",
  "test_type": "concurrent",
  "endpoint_type": "docx",
  "num_requests": 100,
  "max_workers": 20
}
```

**Response:**
```json
{
  "success": true,
  "test_run_id": 123,
  "message": "Test started successfully"
}
```

#### POST `/api/stop-test`
Zatrzymanie testu

#### GET `/api/test-history`
Historia testów

**Query params:**
- `limit` (default: 50) - liczba testów do zwrócenia

#### GET `/api/test-run/<id>`
Szczegóły testu

#### POST `/api/generate-report/<id>`
Generowanie raportu HTML

### WebSocket Events

#### Client → Server
- `connect` - Połączenie
- `disconnect` - Rozłączenie
- `request_system_metrics` - Żądanie metryk

#### Server → Client
- `connected` - Potwierdzenie połączenia
- `test_started` - Test rozpoczęty
- `test_progress` - Postęp testu
- `test_completed` - Test zakończony
- `test_error` - Błąd testu
- `system_metrics` - Metryki systemowe

---

## 📈 Metryki i statystyki

Program zbiera następujące metryki:

### Request Metrics
- **Total Requests**: Łączna liczba requestów
- **Successful**: Liczba udanych requestów (status 2xx)
- **Failed**: Liczba nieudanych requestów
- **Response Times**: Avg, Min, Max, P50, P95, P99
- **Throughput**: Requests per second
- **Error Rate**: Errors per second
- **Status Code Distribution**: Rozkład kodów HTTP

### System Metrics
- **CPU Usage**: Percentage, per core
- **Memory Usage**: Percentage, MB used
- **Disk I/O**: Read/Write MB
- **Network I/O**: Sent/Received MB
- **Active Connections**: Liczba aktywnych połączeń

---

## 🎨 Przykładowe wykresy

Raporty HTML zawierają:

1. **Response Time Over Time** - Czasy odpowiedzi w czasie
2. **Response Time Distribution** - Histogram czasów
3. **Throughput Chart** - Requests per second
4. **Percentile Chart** - P50, P75, P90, P95, P99
5. **Status Code Pie Chart** - Rozkład kodów odpowiedzi
6. **CPU Usage Chart** - Użycie CPU w czasie
7. **Memory Usage Chart** - Użycie RAM w czasie
8. **Disk I/O Chart** - Operacje dyskowe
9. **Network I/O Chart** - Transfer sieciowy

---

## 🔧 Optymalizacja dla 8 vCPU / 24GB RAM

### Zalecane ustawienia

#### Dla testów Concurrent:
```python
max_workers = cpu_count * 2  # ~16 dla 8 vCPU
num_requests = 100-500
```

#### Dla testów Async:
```python
num_requests = 500-2000  # Async może więcej
```

#### Dla testów Ramp-Up:
```python
max_users = 200-500
ramp_duration = 60-300s
```

### Limity systemu

Na serwerze 8 vCPU / 24GB RAM bezpiecznie można:
- **Concurrent**: do 100-200 równoczesnych workerów
- **Async**: do 1000+ równoczesnych połączeń
- **Sustained load**: ~50-100 requests/second

---

## 🐛 Troubleshooting

### Problem: Test się nie uruchamia

**Rozwiązanie:**
1. Sprawdź czy MS-Oferta API działa: `curl http://localhost:8000/health`
2. Sprawdź logi: `tail -f logs/app.log`
3. Zweryfikuj konfigurację w `.env`

### Problem: Wysokie użycie CPU/RAM

**Rozwiązanie:**
1. Zmniejsz `max_workers` lub `num_requests`
2. Użyj typu `Async` zamiast `Concurrent`
3. Zwiększ `MONITOR_INTERVAL` w config

### Problem: WebSocket nie działa

**Rozwiązanie:**
1. Sprawdź czy port 5000 nie jest blokowany
2. Zweryfikuj firewall settings
3. Sprawdź browser console (F12) dla błędów

### Problem: Brak danych w raportach

**Rozwiązanie:**
1. Upewnij się że test się zakończył
2. Sprawdź bazę danych: `sqlite3 database/performance.db`
3. Sprawdź czy są dane w tabeli `test_runs`

---

## 📝 Licencja

Copyright © 2024 MS-Oferta Performance Testing Team

---

## 👥 Wsparcie

W przypadku problemów:
1. Sprawdź dokumentację powyżej
2. Zobacz sekcję Troubleshooting
3. Sprawdź logi aplikacji
4. Skontaktuj się z zespołem developerskim

---

## 🚀 Szybki start

```bash
# 1. Instalacja
cd performance-tester
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Konfiguracja
cp .env.example .env
# Edytuj .env jeśli potrzeba

# 3. Uruchomienie
python run.py

# 4. Dostęp
# Otwórz: http://localhost:5000
```

---

**Powodzenia w testowaniu! 🎯📊🚀**
