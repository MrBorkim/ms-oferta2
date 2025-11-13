import os
from pathlib import Path

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates" / "aidrops"
PRODUKTY_DIR = BASE_DIR / "produkty"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# Tworzenie katalogów jeśli nie istnieją
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Szablony
TEMPLATE_FILE = TEMPLATES_DIR / "oferta1.docx"

# Ustawienia konwersji
JPG_DPI = 100

# Ustawienia serwera
HOST = "0.0.0.0"
PORT = 8000

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
