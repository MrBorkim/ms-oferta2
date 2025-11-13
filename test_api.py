"""
Skrypt testowy do sprawdzenia działania Oferta Generator API

Użycie:
    python test_api.py
"""

import requests
import time
from pathlib import Path


# Konfiguracja
API_URL = "http://localhost:8000"


def test_health():
    """Test health check"""
    print("\n🔍 Test 1: Health Check")
    response = requests.get(f"{API_URL}/health")
    data = response.json()

    print(f"   Status: {data['status']}")
    print(f"   Szablon istnieje: {data['template_exists']}")
    print(f"   Liczba produktów: {data['produkty_count']}")

    return data['status'] == 'healthy'


def test_list_produkty():
    """Test listowania produktów"""
    print("\n🔍 Test 2: Lista produktów")
    response = requests.get(f"{API_URL}/api/list-produkty")
    data = response.json()

    print(f"   Sukces: {data['success']}")
    print(f"   Liczba produktów: {data['count']}")
    print(f"   Produkty: {', '.join(data['produkty'][:5])}")

    return data['success'] and data['count'] > 0


def test_generate_docx():
    """Test generowania DOCX"""
    print("\n🔍 Test 3: Generowanie DOCX")

    payload = {
        "KLIENT(NIP)": "1234567890",
        "Oferta z dnia": "2024-11-10",
        "wazna_do": "2024-12-10",
        "firmaM": "Test Firma Sp. z o.o.",
        "temat": "Testowe zlecenie",
        "kategoria": "IT",
        "opis": "Test generowania oferty przez API",
        "produkty": ["1.docx"],
        "cena": 5000.00,
        "RBG": 40,
        "uzasadnienie": "Test",
        "output_format": "docx"
    }

    start = time.time()
    response = requests.post(f"{API_URL}/api/generate-offer", json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Plik: {data['file_name']}")
        print(f"   Rozmiar: {data['file_size_bytes'] / 1024:.2f} KB")
        print(f"   Czas: {elapsed:.2f}s")
        return True, data['file_name']
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        print(f"   {response.text}")
        return False, None


def test_generate_pdf():
    """Test generowania PDF"""
    print("\n🔍 Test 4: Generowanie PDF")

    payload = {
        "KLIENT(NIP)": "9876543210",
        "Oferta z dnia": "2024-11-10",
        "wazna_do": "2024-12-10",
        "firmaM": "PDF Test Firma",
        "produkty": ["1.docx", "2.docx"],
        "output_format": "pdf"
    }

    start = time.time()
    response = requests.post(f"{API_URL}/api/generate-offer", json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Plik: {data['file_name']}")
        print(f"   Rozmiar: {data['file_size_bytes'] / 1024:.2f} KB")
        print(f"   Czas: {elapsed:.2f}s")
        return True, data['file_name']
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        print(f"   {response.text}")
        return False, None


def test_generate_jpg():
    """Test generowania JPG"""
    print("\n🔍 Test 5: Generowanie JPG (100 DPI)")

    payload = {
        "KLIENT(NIP)": "5555555555",
        "Oferta z dnia": "2024-11-10",
        "wazna_do": "2024-12-10",
        "firmaM": "JPG Test Firma",
        "produkty": ["1.docx"],
        "output_format": "jpg"
    }

    start = time.time()
    response = requests.post(f"{API_URL}/api/generate-offer", json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Plik: {data['file_name']}")
        print(f"   Rozmiar: {data['file_size_bytes'] / 1024:.2f} KB")
        print(f"   Czas: {elapsed:.2f}s")
        return True, data['file_name']
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        print(f"   {response.text}")
        return False, None


def test_download(file_name):
    """Test pobierania pliku"""
    print(f"\n🔍 Test 6: Pobieranie pliku {file_name}")

    response = requests.get(f"{API_URL}/api/download/{file_name}")

    if response.status_code == 200:
        # Zapisz plik
        output_path = Path("test_download") / file_name
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_bytes(response.content)

        print(f"   ✅ Pobrano: {output_path}")
        print(f"   Rozmiar: {len(response.content) / 1024:.2f} KB")
        return True
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        return False


def main():
    """Uruchom wszystkie testy"""
    print("=" * 60)
    print("🚀 Oferta Generator API - Testy")
    print("=" * 60)

    results = []

    # Test 1: Health check
    try:
        results.append(("Health Check", test_health()))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Health Check", False))

    # Test 2: Lista produktów
    try:
        results.append(("Lista produktów", test_list_produkty()))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Lista produktów", False))

    # Test 3: DOCX
    try:
        success, file_name = test_generate_docx()
        results.append(("Generowanie DOCX", success))
        if success and file_name:
            test_download(file_name)
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Generowanie DOCX", False))

    # Test 4: PDF
    try:
        success, file_name = test_generate_pdf()
        results.append(("Generowanie PDF", success))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Generowanie PDF", False))

    # Test 5: JPG
    try:
        success, file_name = test_generate_jpg()
        results.append(("Generowanie JPG", success))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Generowanie JPG", False))

    # Podsumowanie
    print("\n" + "=" * 60)
    print("📊 Podsumowanie testów")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")

    print("\n" + "=" * 60)
    print(f"Wynik: {passed}/{total} testów przeszło")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Błąd krytyczny: {e}")
        exit(1)
