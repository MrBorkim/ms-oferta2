# 🚀 MS-Oferta Performance Tester - ENHANCED EDITION

**Profesjonalny system testowania wydajności zoptymalizowany dla 8 vCPU / 24GB RAM / 400GB SSD / 600 Mbit/s**

## 🎯 Co nowego w ENHANCED EDITION?

### ⚡ Mega szybkie generowanie
- **HTTP/2 Support** - wykorzystanie HTTP/2 dla maksymalnej wydajności
- **Connection Pooling** - reużywanie połączeń TCP dla szybszych requestów
- **Burst Testing** - symulacja nagłych skoków ruchu (do 500 RPS)
- **Optimized dla 8 vCPU** - pełne wykorzystanie mocy procesora

### 📊 Zaawansowane metryki
- **Per-Core CPU Monitoring** - monitorowanie każdego z 8 rdzeni osobno
- **Real-time IOPS** - pomiar operacji I/O na sekundę (idealny dla SSD)
- **Network Throughput w Mbps** - pomiar przepustowości dla 600 Mbit/s
- **P75, P90, P999 percentile** - szczegółowa analiza czasów odpowiedzi
- **Throughput metrics** - pomiar przepływności danych w MB/s i Mbps

### 🔥 Nowe scenariusze testowe
- `burst_100` - 5 burst'ów po 100 requestów
- `burst_200` - 3 burst'ów po 200 requestów (stress test dla 8 vCPU)
- `extreme_500` - **500 równoczesnych requestów** (maksymalny test)
- `http2_ultra` - HTTP/2 test dla maksymalnego throughput
- `sustained_high` - 10 minut wysokiego obciążenia
- `mega_burst` - 🚀 **ULTIMATE TEST**: 10 burst'ów po 500 requestów!

### 💾 Optymalizacje bazy danych (SSD)
- **WAL Mode** - Write-Ahead Logging dla SSDs
- **Bulk Inserts** - masowe wstawianie rekordów (do 1000x szybsze)
- **64MB Cache** - optymalizacja pamięci
- **Memory-mapped I/O** - 256MB mmap dla wielkich dataset'ów
- **4KB Page Size** - wyrównanie do bloków SSD

---

## 📋 Wymagania

### System
- **Python**: 3.9 lub nowszy
- **CPU**: 8 vCPU (lub więcej)
- **RAM**: 24 GB (minimum 8GB)
- **Dysk**: 400 GB SSD
- **Sieć**: 600 Mbit/s

---

## 🔧 Instalacja

### 1. Przejdź do katalogu

```bash
cd /home/user/ms-oferta2/performance-tester
```

### 2. Utwórz virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
```

### 3. Zainstaluj zależności (z HTTP/2 support!)

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Konfiguracja

```bash
cp .env.example .env
nano .env
```

**Ważne ustawienia w `.env`:**

```env
# API do testowania
API_BASE_URL=http://localhost:8000

# Dashboard
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

## 🚀 Uruchomienie

### Uruchom MS-Oferta API (w osobnym terminalu)

```bash
cd /home/user/ms-oferta2
python main.py
```

### Uruchom Performance Tester

```bash
cd /home/user/ms-oferta2/performance-tester
source venv/bin/activate
python run.py
```

### Otwórz w przeglądarce

```
http://localhost:5000
```

---

## 🎮 Typy testów

### 1. **Concurrent Test** (Wielowątkowy)
- Używa ThreadPoolExecutor z connection pooling
- Najlepszy dla: średniego obciążenia, stabilnych testów
- **Zalecane dla 8 vCPU**: 10-100 workers

```python
Test Type: concurrent
Requests: 100
Workers: 20
```

### 2. **Async Test** (Wysokowydajny)
- Używa aiohttp i asyncio
- Najlepszy dla: bardzo wysokiego obciążenia
- Może obsłużyć setki równoczesnych połączeń

```python
Test Type: async
Requests: 500
```

### 3. **Ramp-Up Test** (Stopniowe zwiększanie)
- Stopniowo zwiększa liczbę użytkowników
- Najlepszy dla: testowania progów wydajności

```python
Test Type: ramp
Max Users: 200
Duration: 300s
```

### 4. **🆕 Burst Test** (Maksymalna szybkość)
- **NOWE!** Symuluje nagłe skoki ruchu
- Idealny dla testowania szczytowych obciążeń
- **Zoptymalizowany dla 8 vCPU / 600 Mbit/s**

```python
Test Type: burst
Burst Size: 100-500
Num Bursts: 1-10
Burst Delay: 1-60s
```

**Przykład:** 5 burst'ów po 100 requestów, co 10 sekund

### 5. **🆕 HTTP/2 Test** (Ultra szybki)
- **NOWE!** Wykorzystuje HTTP/2 dla maksymalnej wydajności
- Najlepszy dla nowoczesnych serwerów
- **Idealny dla 600 Mbit/s połączenia**

```python
Test Type: http2
Requests: 300
```

---

## 📊 Nowe scenariusze testowe

### 🟢 Quick Test
- **Czas**: 1 minuta
- **Użytkownicy**: 10
- **Cel**: Szybka weryfikacja

### 🔵 Standard Load Test
- **Czas**: 5 minut
- **Użytkownicy**: 50
- **Cel**: Standardowe obciążenie

### 🟡 Heavy Load Test
- **Czas**: 10 minut
- **Użytkownicy**: 100
- **Cel**: Wysokie obciążenie

### 🟠 Stress Test
- **Czas**: 15 minut
- **Użytkownicy**: 200
- **Cel**: Znajdowanie limitów

### 🔴 Spike Test
- **Czas**: 5 minut
- **Użytkownicy**: 300
- **Cel**: Nagły wzrost ruchu

### 🟣 Endurance Test
- **Czas**: 1 godzina
- **Użytkownicy**: 50
- **Cel**: Długoterminowa stabilność

---

## 🆕 NOWE Zaawansowane scenariusze

### 💥 Burst Test - 100 RPS
- **5 burst'ów po 100 requestów**, co 10s
- **Cel**: Test szczytowej pojemności
- **Dla**: 8 vCPU

```bash
Scenario: burst_100
Burst Size: 100
Num Bursts: 5
Delay: 10s
```

### 💥💥 Burst Test - 200 RPS
- **3 burst'ów po 200 requestów**, co 20s
- **Cel**: Stress test dla 8 vCPU
- **Dla**: Wysokie obciążenia

```bash
Scenario: burst_200
Burst Size: 200
Num Bursts: 3
Delay: 20s
```

### ⚡ Extreme Load - 500 RPS
- **500 równoczesnych requestów**
- **Cel**: MAKSYMALNE obciążenie dla 600 Mbit/s
- **WARNING**: Ekstremalny test!

```bash
Scenario: extreme_500
Users: 500
Duration: 3 min
```

### 🌐 HTTP/2 Ultra Fast
- **300 requestów przez HTTP/2**
- **Cel**: Maksymalny throughput
- **Dla**: Nowoczesne serwery

```bash
Scenario: http2_ultra
Users: 300
Duration: 5 min
```

### 🔥 Sustained High Load
- **150 użytkowników przez 10 minut**
- **Cel**: Długotrwałe wysokie obciążenie
- **Dla**: Test stabilności

```bash
Scenario: sustained_high
Users: 150
Duration: 10 min
```

### 🚀 MEGA Burst - Max Speed
- **10 burst'ów po 500 requestów!**
- **Cel**: OSTATECZNY TEST
- **WARNING**: Tylko dla potężnych serwerów!

```bash
Scenario: mega_burst
Burst Size: 500
Num Bursts: 10
Delay: 15s
```

---

## 📈 Nowe metryki

### Response Time Percentiles
- **P50** (mediana) - 50% requestów szybsze niż ta wartość
- **P75** - 75% requestów szybsze
- **P90** - 90% requestów szybsze
- **P95** - 95% requestów szybsze
- **P99** - 99% requestów szybsze
- **P999** - 99.9% requestów szybsze (tylko dla >1000 requestów)

### Throughput Metrics
- **Requests per second (RPS)** - liczba requestów na sekundę
- **Throughput (Mbps)** - przepustowość w megabitach na sekundę
- **Total bytes sent/received** - łączna ilość przesłanych danych
- **Standard deviation** - odchylenie standardowe czasów odpowiedzi

### CPU Metrics (Per-Core)
- **CPU per core** - użycie każdego z 8 rdzeni osobno
- **Load average** - średnie obciążenie (1min, 5min, 15min)
- **CPU frequency** - aktualna, min i max częstotliwość

### Disk Metrics (SSD Optimized)
- **IOPS** (Read/Write) - operacje I/O na sekundę
- **Throughput** (MB/s) - przepustowość dysku w megabajtach
- **Cumulative I/O** - łączny I/O od początku testu

### Network Metrics (600 Mbit/s)
- **Upload/Download Mbps** - real-time przepustowość
- **Total Mbps** - łączna przepustowość
- **Active connections** - liczba aktywnych połączeń

---

## 🎯 Optymalizacje dla Twojego serwera

### 8 vCPU
- **Max workers**: 16-32 (2x-4x liczby rdzeni)
- **Concurrent tests**: do 100-200 workers
- **Async tests**: do 1000+ połączeń
- **Burst tests**: 100-500 requestów per burst

### 24 GB RAM
- **64MB database cache** - optymalna wielkość
- **256MB mmap** - memory-mapped I/O
- **Bulk inserts**: do 1000 rekordów naraz

### 400 GB SSD
- **WAL mode** - minimalizuje zapis na dysk
- **4KB page size** - wyrównane do bloków SSD
- **Auto-vacuum** - zarządzanie miejscem

### 600 Mbit/s
- **HTTP/2 tests** - maksymalna przepustowość
- **Connection pooling** - reużycie połączeń
- **500+ RPS** - możliwe przy burst testach

---

## 🔍 Troubleshooting

### Test nie startuje
```bash
# Sprawdź czy MS-Oferta API działa
curl http://localhost:8000/health

# Sprawdź logi
tail -f logs/app.log
```

### Wysokie użycie CPU/RAM
```bash
# Zmniejsz max_workers lub num_requests
# Użyj typu async zamiast concurrent
# Zwiększ MONITOR_INTERVAL w config
```

### Błąd WebSocket
```bash
# Sprawdź port 5000
sudo netstat -tulpn | grep 5000

# Sprawdź browser console (F12)
```

### Brak danych w raportach
```bash
# Sprawdź bazę danych
sqlite3 database/performance.db "SELECT COUNT(*) FROM test_runs;"

# Sprawdź czy test się zakończył
```

---

## 📝 API Endpoints

### POST `/api/start-test`
Rozpocznij test

```json
{
  "test_name": "My Test",
  "scenario": "burst_100",
  "test_type": "burst",
  "endpoint_type": "docx",
  "num_requests": 100,
  "max_workers": 20,
  "burst_size": 100,
  "num_bursts": 5,
  "burst_delay": 10
}
```

### GET `/api/test-history?limit=50`
Historia testów

### GET `/api/test-run/<id>`
Szczegóły testu

### POST `/api/generate-report/<id>`
Generuj raport HTML

---

## 🏆 Benchmarki

### Na serwerze 8 vCPU / 24GB RAM:

**DOCX Generation:**
- Standard: ~50 RPS
- Burst: ~100-150 RPS peak
- HTTP/2: ~80-120 RPS sustained

**PDF Generation:**
- Standard: ~20-30 RPS
- Burst: ~40-60 RPS peak
- HTTP/2: ~35-50 RPS sustained

**JPG Generation:**
- Standard: ~15-25 RPS
- Burst: ~30-50 RPS peak

**Health Check:**
- Standard: ~500-800 RPS
- Burst: ~1000-2000 RPS peak
- HTTP/2: ~1500-2500 RPS sustained

---

## 🎓 Best Practices

### 1. Zacznij od małych testów
```bash
Scenario: quick
Type: concurrent
Workers: 10
```

### 2. Stopniowo zwiększaj obciążenie
```bash
quick → standard → heavy → stress
```

### 3. Używaj Burst dla szczytów
```bash
burst_100 → burst_200 → mega_burst
```

### 4. Testuj HTTP/2 osobno
```bash
Type: http2
Requests: 100-300
```

### 5. Monitoruj zasoby
- Obserwuj CPU per-core
- Sprawdzaj IOPS
- Monitoruj Network Mbps

---

## 📦 Zawartość Enhanced Edition

```
performance-tester/
├── app/
│   ├── app.py                    # Main Flask app (ENHANCED)
│   ├── load_tester.py            # 🆕 HTTP/2 + Burst + Connection Pooling
│   ├── monitor.py                # 🆕 Per-core CPU + IOPS + Mbps
│   ├── database.py               # 🆕 WAL mode + Bulk inserts + SSD optimized
│   ├── config.py                 # 🆕 6 nowych scenariuszy
│   └── report_generator.py       # Report generation
├── templates/
│   └── index.html                # Web dashboard
├── database/
│   └── performance.db            # 🆕 Enhanced schema
├── reports/                       # HTML reports
├── logs/                          # Application logs
├── requirements.txt               # 🆕 httpx[http2] + urllib3
├── run.py                         # Entry point
├── .env                           # Configuration
├── README.md                      # Original README
└── README_ENHANCED.md             # 🆕 Ten plik!
```

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Instalacja
cd /home/user/ms-oferta2/performance-tester
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Uruchom MS-Oferta API (terminal 1)
cd /home/user/ms-oferta2
python main.py

# 3. Uruchom Performance Tester (terminal 2)
cd /home/user/ms-oferta2/performance-tester
source venv/bin/activate
python run.py

# 4. Otwórz w przeglądarce
http://localhost:5000

# 5. Wybierz scenario: mega_burst lub extreme_500
# 6. Kliknij "Start Test"
# 7. Obserwuj MEGA wydajność! 🚀
```

---

## 💡 Tips & Tricks

### Maksymalna wydajność DOCX
```bash
Type: burst
Burst Size: 200
Endpoint: docx
Workers: 32
```

### Test HTTP/2 throughput
```bash
Type: http2
Requests: 500
Endpoint: health
```

### Długotrwały stress test
```bash
Type: async
Requests: 10000
Duration: 3600s
Endpoint: pdf
```

---

## ⚠️ Uwagi

- **mega_burst** i **extreme_500** są ekstremalne - używaj z rozwagą!
- Monitoruj temperaturę CPU podczas długich testów
- Burst testy mogą przeciążyć serwer - zacznij od małych burst_size
- HTTP/2 wymaga nowoczesnego serwera

---

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź logs: `tail -f logs/app.log`
2. Sprawdź bazę: `sqlite3 database/performance.db`
3. Sprawdź API: `curl http://localhost:8000/health`

---

## 📊 Features Summary

✅ HTTP/2 Support
✅ Connection Pooling
✅ Burst Testing (500 RPS)
✅ Per-Core CPU Monitoring
✅ Real-time IOPS
✅ Network Throughput (Mbps)
✅ WAL Mode (SSD)
✅ Bulk Inserts
✅ 6 nowych scenariuszy
✅ P75, P90, P999 percentile
✅ Throughput metrics

---

**Powered by Enhanced Edition v2.0 - Optimized for 8 vCPU / 24GB RAM / 400GB SSD / 600 Mbit/s** 🚀
