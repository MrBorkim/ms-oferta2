# 🚀 Quick Start Guide

Szybki przewodnik uruchomienia MS-Oferta Performance Tester w 5 minut!

## Wymagania wstępne

- ✅ Python 3.9 lub nowszy
- ✅ 4GB RAM minimum
- ✅ Aplikacja MS-Oferta uruchomiona na porcie 8000

## Krok 1: Instalacja (2 minuty)

```bash
cd /home/user/ms-oferta2/performance-tester

# Automatyczna instalacja
chmod +x install.sh
./install.sh
```

**Co się stanie:**
- Utworzenie środowiska wirtualnego Python
- Instalacja wszystkich zależności
- Utworzenie plików konfiguracyjnych
- Przygotowanie katalogów

## Krok 2: Konfiguracja (1 minuta)

```bash
# Edytuj konfigurację (opcjonalne)
nano .env
```

**Najważniejsze ustawienia:**
```env
API_BASE_URL=http://localhost:8000  # Adres API MS-Oferta
FLASK_PORT=5000                      # Port web dashboardu
```

## Krok 3: Uruchomienie (30 sekund)

```bash
# Uruchom aplikację
./start.sh
```

**Albo manualnie:**
```bash
source venv/bin/activate
python run.py
```

## Krok 4: Dostęp do dashboardu (10 sekund)

Otwórz przeglądarkę i wejdź na:

```
http://localhost:5000
```

Lub z zewnątrz:
```
http://YOUR_SERVER_IP:5000
```

## Krok 5: Pierwszy test (1 minuta)

### W przeglądarce:

1. **Wybierz scenariusz:** Quick Test (1 min, 10 users)
2. **Wybierz endpoint:** Generate DOCX
3. **Kliknij:** "Start Test"
4. **Obserwuj:** Real-time metryki i wykresy

### Wyniki:
- ✅ Total requests
- ✅ Success rate
- ✅ Average response time
- ✅ System metrics (CPU, RAM)

---

## 📊 Przykładowe testy

### Test 1: Quick Health Check
```
Scenario: Quick Test
Endpoint: Health Check
Requests: 50
Workers: 10
Expected time: ~5 seconds
```

### Test 2: Document Generation
```
Scenario: Standard Load
Endpoint: Generate DOCX
Requests: 100
Workers: 20
Expected time: ~30-60 seconds
```

### Test 3: Stress Test
```
Scenario: Stress Test
Endpoint: Generate PDF
Requests: 200
Workers: 50
Expected time: ~5-10 minutes
```

---

## 🐛 Szybkie rozwiązywanie problemów

### Problem: "Connection refused"
**Rozwiązanie:** Sprawdź czy MS-Oferta API działa
```bash
curl http://localhost:8000/health
```

### Problem: "Module not found"
**Rozwiązanie:** Zainstaluj dependencies ponownie
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Port already in use"
**Rozwiązanie:** Zmień port w .env
```bash
export FLASK_PORT=5500
python run.py
```

---

## 📱 Dostęp z zewnątrz

Jeśli chcesz dostać się do dashboardu z innego komputera:

### 1. Sprawdź IP serwera
```bash
hostname -I
# Output: 192.168.1.100
```

### 2. Otwórz port w firewall (jeśli potrzeba)
```bash
sudo ufw allow 5000/tcp
```

### 3. Dostęp z przeglądarki
```
http://192.168.1.100:5000
```

---

## 🎯 Następne kroki

Po uruchomieniu pierwszego testu:

1. **Eksploruj różne scenariusze** - Quick, Standard, Heavy, Stress
2. **Testuj różne endpointy** - DOCX, PDF, JPG
3. **Analizuj raporty** - Generuj HTML reports z wykresami
4. **Monitoruj zasoby** - Sprawdź jak aplikacja wykorzystuje serwer
5. **Optymalizuj** - Dostosuj parametry dla najlepszej wydajności

---

## 📚 Więcej informacji

- **Pełna dokumentacja:** [README.md](README.md)
- **API Documentation:** Zobacz sekcję API w README
- **Troubleshooting:** Zobacz sekcję Troubleshooting w README

---

**Gotowe! Masz działający system testowania wydajności! 🎉**
