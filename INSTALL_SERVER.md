# Instalacja na serwerze Linux (Ubuntu/Debian)

## Szybki start (5 minut)

### 1. Przygotowanie serwera

```bash
# Aktualizacja systemu
sudo apt-get update
sudo apt-get upgrade -y

# Instalacja zależności systemowych
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libreoffice \
    libreoffice-writer \
    poppler-utils \
    git

# Weryfikacja
python3.11 --version
libreoffice --version
```

### 2. Pobranie kodu

```bash
# Skopiuj pliki na serwer (np. przez SCP, rsync, git)
# Przykład z git:
cd /var/www/
sudo git clone <repo-url> oferta-ts-ms
cd oferta-ts-ms

# Lub przez SCP z lokalnego komputera:
# scp -r /path/to/oferta-ts-ms user@server:/var/www/
```

### 3. Konfiguracja virtual environment

```bash
# Stwórz venv
python3.11 -m venv .venv

# Aktywuj
source .venv/bin/activate

# Zainstaluj zależności
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Testowe uruchomienie

```bash
# Test lokalnie
python main.py

# W innym terminalu:
curl http://localhost:8000/health
```

Jeśli działa, przerwij (Ctrl+C) i przejdź do instalacji jako serwis systemd.

### 5. Instalacja jako serwis systemd

```bash
# Stwórz katalog na logi
sudo mkdir -p /var/log/oferta-api
sudo chown www-data:www-data /var/log/oferta-api

# Edytuj plik serwisu (zmień ścieżki!)
sudo nano oferta-api.service

# Skopiuj do systemd
sudo cp oferta-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Włącz autostart
sudo systemctl enable oferta-api

# Uruchom
sudo systemctl start oferta-api

# Sprawdź status
sudo systemctl status oferta-api
```

### 6. Weryfikacja

```bash
# Sprawdź czy działa
curl http://localhost:8000/health

# Logi
sudo journalctl -u oferta-api -f

# Lub z pliku
sudo tail -f /var/log/oferta-api/access.log
sudo tail -f /var/log/oferta-api/error.log
```

### 7. Konfiguracja firewall (opcjonalnie)

```bash
# Jeśli używasz UFW
sudo ufw allow 8000/tcp
sudo ufw reload

# Sprawdź
sudo ufw status
```

---

## Instalacja z Nginx (zalecane dla produkcji)

### 1. Instalacja Nginx

```bash
sudo apt-get install -y nginx
```

### 2. Konfiguracja Nginx

Stwórz plik `/etc/nginx/sites-available/oferta-api`:

```nginx
upstream oferta_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.twojadomena.pl;  # Zmień na swoją domenę

    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://oferta_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://oferta_api;
    }

    location /docs {
        proxy_pass http://oferta_api;
    }

    location / {
        proxy_pass http://oferta_api;
        proxy_set_header Host $host;
    }
}
```

### 3. Włączenie konfiguracji

```bash
# Symlink
sudo ln -s /etc/nginx/sites-available/oferta-api /etc/nginx/sites-enabled/

# Test konfiguracji
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 4. Test

```bash
curl http://twojadomena.pl/health
```

### 5. SSL z Certbot (opcjonalnie)

```bash
# Instalacja Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Uzyskaj certyfikat
sudo certbot --nginx -d api.twojadomena.pl

# Auto-renewal jest już skonfigurowany
sudo certbot renew --dry-run
```

---

## Instalacja z Docker

### 1. Instalacja Docker

```bash
# Instalacja Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose
sudo apt-get install -y docker-compose

# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER
```

### 2. Build i uruchomienie

```bash
# Build obrazu
docker build -t oferta-api .

# Uruchom
docker run -d \
    --name oferta-api \
    -p 8000:8000 \
    -v $(pwd)/produkty:/app/produkty:ro \
    -v $(pwd)/templates:/app/templates:ro \
    -v $(pwd)/output:/app/output \
    oferta-api

# Sprawdź logi
docker logs -f oferta-api

# Sprawdź status
docker ps
```

### 3. Lub z Docker Compose

```bash
# Uruchom
docker-compose up -d

# Logi
docker-compose logs -f

# Stop
docker-compose down
```

---

## Monitorowanie i maintenance

### Sprawdzanie logów

```bash
# Logi systemd
sudo journalctl -u oferta-api -n 100 -f

# Logi plików
sudo tail -f /var/log/oferta-api/error.log

# Logi Docker
docker logs -f oferta-api
```

### Restart serwisu

```bash
# Systemd
sudo systemctl restart oferta-api

# Docker
docker restart oferta-api

# Docker Compose
docker-compose restart
```

### Update kodu

```bash
# Systemd
cd /var/www/oferta-ts-ms
git pull  # lub scp nowe pliki
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart oferta-api

# Docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Czyszczenie starych plików

```bash
# Usuń pliki starsze niż 7 dni
find /var/www/oferta-ts-ms/output -type f -mtime +7 -delete
find /var/www/oferta-ts-ms/temp -type f -mtime +1 -delete

# Lub dodaj do crontab
crontab -e

# Dodaj linię:
0 2 * * * find /var/www/oferta-ts-ms/output -type f -mtime +7 -delete
```

---

## Troubleshooting

### Problem: LibreOffice nie działa

```bash
# Sprawdź czy jest zainstalowany
which libreoffice

# Reinstalacja
sudo apt-get remove libreoffice
sudo apt-get install -y libreoffice libreoffice-writer
```

### Problem: Permission denied na output/

```bash
sudo chown -R www-data:www-data /var/www/oferta-ts-ms/output
sudo chmod -R 755 /var/www/oferta-ts-ms/output
```

### Problem: Port 8000 już zajęty

```bash
# Sprawdź co używa portu
sudo lsof -i :8000

# Zmień port w config.py lub użyj innego portu
uvicorn main:app --port 8001
```

### Problem: Nie można połączyć się z API

```bash
# Sprawdź czy serwis działa
sudo systemctl status oferta-api

# Sprawdź firewall
sudo ufw status

# Sprawdź czy port jest otwarty
sudo netstat -tulpn | grep 8000
```

---

## Bezpieczeństwo

### 1. Firewall

```bash
# Otwórz tylko potrzebne porty
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Rate limiting (w Nginx)

Już skonfigurowane w `nginx.conf` - 10 requestów/sekundę.

### 3. API Key (opcjonalnie)

Dodaj do `main.py`:

```python
from fastapi import Header, HTTPException

API_KEY = "twoj-tajny-klucz"

@app.post("/api/generate-offer")
async def generate_offer(
    request: OfertaRequest,
    x_api_key: str = Header(...)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... reszta kodu
```

---

## Performance tuning

### Zwiększ liczbę workerów

```bash
# W oferta-api.service
ExecStart=/var/www/oferta-ts-ms/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8
```

### Dodaj Redis cache (zaawansowane)

```bash
sudo apt-get install -y redis-server
pip install redis aioredis
```

---

## Support

W razie problemów:
1. Sprawdź logi: `sudo journalctl -u oferta-api -n 100`
2. Sprawdź health: `curl http://localhost:8000/health`
3. Sprawdź czy LibreOffice działa: `libreoffice --version`
