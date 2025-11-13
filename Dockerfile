# Dockerfile dla Oferta Generator API
# Build: docker build -t oferta-api .
# Run: docker run -p 8000:8000 -v $(pwd)/produkty:/app/produkty -v $(pwd)/templates:/app/templates oferta-api

FROM python:3.11-slim

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    poppler-utils \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie requirements
COPY requirements.txt .

# Instalacja zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu aplikacji
COPY main.py .
COPY models.py .
COPY document_service.py .
COPY conversion_service.py .
COPY config.py .

# Kopiowanie szablonów i produktów
COPY templates/ templates/
COPY produkty/ produkty/

# Tworzenie katalogów
RUN mkdir -p output temp && \
    chmod 777 output temp

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Uruchomienie aplikacji
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
