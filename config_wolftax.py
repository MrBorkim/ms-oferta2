# -*- coding: utf-8 -*-
import os
from pathlib import Path

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates" / "wolftax-oferta"
PRODUKTY_DIR = BASE_DIR / "produkty"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# Tworzenie katalogów jeśli nie istnieją
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Pliki szablonu WolfTax (w odpowiedniej kolejności)
WOLFTAX_FILES = [
    {"file": "Dok1.docx", "order": 1, "name": "Strona tytułowa"},
    {"file": "Doc2.docx", "order": 2, "name": "Wprowadzenie"},
    {"file": "doc3.docx", "order": 3, "name": "Spis treści", "is_toc": True},
    # Tutaj wstrzykiwane są produkty
    {"file": "doc4.docx", "order": 4, "name": "Podsumowanie"},
    {"file": "Dok5.docx", "order": 5, "name": "Warunki"},
    {"file": "Dok6.docx", "order": 6, "name": "Strona końcowa"}
]

# Punkt wstrzyknięcia produktów (po którym pliku)
INJECTION_AFTER_FILE = "doc3.docx"

# Ustawienia konwersji
JPG_DPI = 100

# Ustawienia serwera
HOST = "0.0.0.0"
PORT = 8001  # Inny port niż aidrops (8000)

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
