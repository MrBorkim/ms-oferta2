# 🎬 Demo - MS-Oferta Performance Tester

Ten dokument pokazuje przykłady użycia narzędzia do testowania wydajności.

## 📺 Scenariusz Demo

### Przygotowanie środowiska

```bash
# Terminal 1: Uruchom MS-Oferta API
cd /home/user/ms-oferta2
source venv/bin/activate
python main.py
# API będzie dostępne na http://localhost:8000

# Terminal 2: Uruchom Performance Tester
cd /home/user/ms-oferta2/performance-tester
./install.sh
./start.sh
# Dashboard będzie dostępny na http://localhost:5000
```

---

## 🎯 Demo 1: Quick Test (Szybki test funkcjonalności)

### Cel
Sprawdzenie czy aplikacja MS-Oferta odpowiada poprawnie i szybko.

### Konfiguracja w UI
1. **Test Name**: "Demo 1 - Quick Health Check"
2. **Scenario**: Quick Test
3. **Test Type**: Concurrent
4. **Endpoint**: Health Check
5. **Requests**: 50
6. **Workers**: 10

### Oczekiwane wyniki
- ✅ Wszystkie requesty zakończone sukcesem (100%)
- ✅ Średni czas odpowiedzi < 0.1s
- ✅ 0 błędów
- ✅ ~500-1000 requests/second

### CLI Alternative
```bash
python cli.py test -e health -r 50 -w 10
```

---

## 🎯 Demo 2: Document Generation Test (Test generowania dokumentów)

### Cel
Testowanie wydajności generowania dokumentów DOCX.

### Konfiguracja w UI
1. **Test Name**: "Demo 2 - DOCX Generation"
2. **Scenario**: Standard Load
3. **Test Type**: Concurrent
4. **Endpoint**: Generate DOCX
5. **Requests**: 100
6. **Workers**: 20

### Oczekiwane wyniki
- ✅ Success rate > 95%
- ✅ Średni czas odpowiedzi: 0.3-0.5s
- ✅ P95 < 1.0s
- ✅ CPU usage: 50-80%
- ✅ ~20-50 requests/second

### CLI Alternative
```bash
python cli.py test -e docx -r 100 -w 20
```

### Co obserwować
1. **Response Time Chart**: Powinien być stabilny
2. **CPU Usage**: Wzrost do 50-80%
3. **Memory Usage**: Stabilny wzrost, potem płaszczyzna
4. **Activity Log**: Brak błędów

---

## 🎯 Demo 3: PDF Conversion Test (Test konwersji PDF)

### Cel
Testowanie najbardziej zasobożernego endpointu (PDF generation).

### Konfiguracja w UI
1. **Test Name**: "Demo 3 - PDF Stress Test"
2. **Scenario**: Heavy Load
3. **Test Type**: Concurrent
4. **Endpoint**: Generate PDF
5. **Requests**: 200
6. **Workers**: 40

### Oczekiwane wyniki
- ✅ Success rate > 90%
- ✅ Średni czas odpowiedzi: 1.0-1.5s
- ✅ P95 < 3.0s
- ✅ CPU usage: 80-95%
- ✅ ~10-20 requests/second

### CLI Alternative
```bash
python cli.py test -e pdf -r 200 -w 40
```

### Ostrzeżenia
- 🟡 CPU może osiągnąć wysokie wartości (to normalne)
- 🟡 Conversion do PDF jest CPU-intensive
- 🟡 Jeśli błędy > 10%, zmniejsz workers

---

## 🎯 Demo 4: Async High-Load Test (Test wysokiego obciążenia)

### Cel
Sprawdzenie maksymalnej przepustowości z wykorzystaniem async mode.

### Konfiguracja w UI
1. **Test Name**: "Demo 4 - Async Stress Test"
2. **Scenario**: Stress Test
3. **Test Type**: Async
4. **Endpoint**: Generate DOCX
5. **Requests**: 500
6. **Workers**: (nie używane w async)

### Oczekiwane wyniki
- ✅ Success rate > 85%
- ✅ Bardzo wysokie requests/second (~100+)
- ✅ CPU usage: 90-100%
- ✅ Możliwe timeouty przy bardzo wysokim load

### CLI Alternative
```bash
python cli.py test -t async -e docx -r 500
```

### Analiza
Ten test pokaże:
- Maksymalną przepustowość systemu
- Punkt w którym serwer zaczyna throttle
- Limity connection pool

---

## 🎯 Demo 5: Ramp-Up Test (Test stopniowego wzrostu)

### Cel
Symulacja realistycznego wzrostu ruchu (np. promocja, launch).

### Konfiguracja w UI
1. **Test Name**: "Demo 5 - Gradual Load Increase"
2. **Scenario**: Custom
3. **Test Type**: Ramp-Up
4. **Endpoint**: Generate PDF
5. **Requests**: 300 (max users)
6. **Duration**: 300s (5 minut)

### Oczekiwane wyniki
- 📈 Stopniowy wzrost użytkowników 0 → 300
- 📈 Response time początkowo niski, potem wzrasta
- 📈 CPU usage stopniowo rośnie
- 📈 System znajduje "sweet spot" lub limit

### Obserwacje
1. **Minute 1**: Niskie obciążenie, wszystko OK
2. **Minute 2-3**: Wzrost obciążenia, stabilne performance
3. **Minute 4-5**: Wysokie obciążenie, możliwe spowolnienia

---

## 🎯 Demo 6: Endurance Test (Test wytrzymałościowy)

### Cel
Sprawdzenie stabilności przez długi okres (memory leaks, degradacja).

### Konfiguracja w UI
1. **Test Name**: "Demo 6 - Long Running Stability"
2. **Scenario**: Endurance Test
3. **Test Type**: Concurrent
4. **Endpoint**: Generate DOCX
5. **Requests**: Custom (ciągłe przez 1h)
6. **Workers**: 30

### Oczekiwane wyniki
- ✅ Stabilne performance przez cały czas
- ✅ Brak memory leaks
- ✅ Brak degradacji response time
- ✅ CPU/RAM stabilne

### Czerwone flagi 🚩
- ❌ Response time rośnie w czasie
- ❌ Memory usage ciągle rośnie
- ❌ Wzrost liczby błędów w czasie

---

## 📊 Interpretacja wyników

### Dobre znaki ✅
- Success rate > 95%
- Response time stabilny
- P95 < 2x średniej
- CPU < 90% sustained
- Memory stabilna
- 0 timeouts

### Ostrzeżenia 🟡
- Success rate 90-95%
- Response time rośnie pod obciążeniem
- P95 2-3x średniej
- CPU 90-100% sustained
- Memory slowly growing
- Pojedyncze timeouts

### Problemy ❌
- Success rate < 90%
- Response time bardzo wysoki
- P95 > 5x średniej
- CPU 100% cały czas
- Memory leak
- Częste timeouts/errors

---

## 🎨 Przykładowe metryki sukcesu

### Dla 8 vCPU / 24GB RAM / 400GB SSD

#### Health Check Endpoint
```
Requests/second: 500-1000
Avg response: < 0.1s
P95: < 0.2s
Success rate: 100%
```

#### DOCX Generation
```
Requests/second: 30-50
Avg response: 0.3-0.5s
P95: < 1.0s
Success rate: > 95%
CPU: 50-70%
```

#### PDF Generation
```
Requests/second: 10-20
Avg response: 1.0-1.5s
P95: < 3.0s
Success rate: > 90%
CPU: 80-90%
```

#### JPG Generation
```
Requests/second: 5-10
Avg response: 1.5-2.5s
P95: < 5.0s
Success rate: > 85%
CPU: 80-95%
Memory: High
```

---

## 🛠️ Troubleshooting podczas demo

### Problem: Dużo błędów 500
**Rozwiązanie:**
- Zmniejsz liczba workerów
- Sprawdź logi MS-Oferta API
- Sprawdź czy produkty (1.docx, 2.docx) istnieją

### Problem: Timeouts
**Rozwiązanie:**
- Zwiększ timeout w config
- Zmniejsz liczbę równoczesnych requestów
- Sprawdź czy serwer nie jest przeciążony

### Problem: Wysokie użycie CPU/RAM
**To normalne!**
- PDF/JPG conversion jest resource-intensive
- Monitoruj czy stabilne czy rośnie
- Jeśli problem, zmniejsz obciążenie

---

## 📈 Po demo - Analiza raportów

1. **Kliknij na test w historii**
2. **Wybierz "Generate Report"**
3. **Otwórz wygenerowany HTML**
4. **Analizuj wykresy:**
   - Response Time Distribution
   - Throughput Over Time
   - Percentiles
   - System Resources
   - I/O Metrics

---

## 🎓 Best Practices z demo

1. **Zawsze zacznij od Quick Test** - weryfikacja podstawowa
2. **Stopniuj obciążenie** - nie zaczynaj od max load
3. **Monitoruj system** - CPU/RAM są ważne jak response time
4. **Zapisuj wyniki** - porównuj różne konfiguracje
5. **Testuj różne endpointy** - mają różne charakterystyki
6. **Używaj realistic data** - prawdziwe produkty i szablony
7. **Daj systemowi odpocząć** - między testami chwila przerwy

---

## 🚀 Następne kroki po demo

1. **Optymalizuj** - na podstawie wyników
2. **Skaluj** - dodaj więcej workerów w main.py
3. **Cache** - rozważ caching często używanych ofert
4. **Database** - jeśli będziesz przechowywać oferty
5. **CDN** - dla statycznych assetów
6. **Load Balancer** - dla multiple instances

---

**Miłego testowania! 🎯📊🚀**
