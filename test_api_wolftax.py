# -*- coding: utf-8 -*-
"""
Skrypt testowy do sprawdzenia działania WolfTax Oferta Generator API

Użycie:
    python test_api_wolftax.py
"""

import requests
import time
from pathlib import Path


# Konfiguracja
API_URL = "http://localhost:8001"


def test_health():
    """Test health check"""
    print("\n🔍 Test 1: Health Check")
    response = requests.get(f"{API_URL}/health")
    data = response.json()

    print(f"   Status: {data['status']}")
    print(f"   Szablony istnieją: {data['templates_exist']}")
    print(f"   Liczba szablonów: {data['templates_count']}")
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
    print("\n🔍 Test 3: Generowanie DOCX + JPG")

    payload = {
        "NazwaFirmyKlienta": "Test Firma Sp. z o.o.",
        "Sygnatura-sprawy": "WTX/2024/11/001",
        "Temat": "Kompleksowa obsługa podatkowa",
        "Termin": "31.12.2024",
        "waznosc-oferty": "10.12.2024",
        "produkty": ["1.docx"],
        "Wynagrodzenie": 5000.00,
        "Szacowanyczaspracy": 40,
        "output_format": "docx"
    }

    start = time.time()
    response = requests.post(f"{API_URL}/api/generate-offer", json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Folder: {data['output_folder']}")
        print(f"   Plik DOCX: {data['file_name']}")
        print(f"   Rozmiar: {data['file_size_bytes'] / 1024:.2f} KB")
        print(f"   Folder JPG: {data['jpg_folder']}")
        print(f"   Liczba JPG: {data['jpg_count']}")
        print(f"   Czas: {elapsed:.2f}s")
        return True, data['output_folder'], data['file_name']
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        print(f"   {response.text}")
        return False, None, None


def test_generate_pdf():
    """Test generowania PDF"""
    print("\n🔍 Test 4: Generowanie PDF + JPG")

    payload = {
        "NazwaFirmyKlienta": "PDF Test Firma Sp. z o.o.",
        "Temat": "Doradztwo podatkowe",
        "waznosc-oferty": "15.12.2024",
        "produkty": ["1.docx", "2.docx"],
        "Wynagrodzenie": 10000.00,
        "output_format": "pdf"
    }

    start = time.time()
    response = requests.post(f"{API_URL}/api/generate-offer", json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Folder: {data['output_folder']}")
        print(f"   Plik PDF: {data['file_name']}")
        print(f"   Rozmiar: {data['file_size_bytes'] / 1024:.2f} KB")
        print(f"   Liczba JPG: {data['jpg_count']}")
        print(f"   Czas: {elapsed:.2f}s")
        return True, data['output_folder'], data['file_name']
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        print(f"   {response.text}")
        return False, None, None


def test_generate_jpg():
    """Test generowania JPG"""
    print("\n🔍 Test 5: Generowanie tylko JPG (100 DPI)")

    payload = {
        "NazwaFirmyKlienta": "JPG Test Firma",
        "Temat": "Konsultacje podatkowe",
        "waznosc-oferty": "20.12.2024",
        "produkty": ["1.docx"],
        "Szacowanyczaspracy": 20,
        "output_format": "jpg"
    }

    start = time.time()
    response = requests.post(f"{API_URL}/api/generate-offer", json=payload)
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Folder: {data['output_folder']}")
        print(f"   Główny plik: {data['file_name']}")
        print(f"   Liczba JPG: {data['jpg_count']}")
        print(f"   Czas: {elapsed:.2f}s")
        return True, data['output_folder']
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        print(f"   {response.text}")
        return False, None


def test_list_offers():
    """Test listowania wygenerowanych ofert"""
    print("\n🔍 Test 6: Lista wygenerowanych ofert")
    response = requests.get(f"{API_URL}/api/list-offers")

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sukces!")
        print(f"   Liczba ofert: {data['count']}")

        for offer in data['offers'][:3]:  # Pokaż 3 najnowsze
            print(f"      - {offer['name']}")
            print(f"        Pliki: {', '.join(offer['files'][:3])}")

        return True
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        return False


def test_download(folder_name, file_name):
    """Test pobierania pliku"""
    print(f"\n🔍 Test 7: Pobieranie pliku {file_name}")

    response = requests.get(f"{API_URL}/api/download/{folder_name}/{file_name}")

    if response.status_code == 200:
        # Zapisz plik
        output_path = Path("test_download_wolftax") / folder_name
        output_path.mkdir(exist_ok=True, parents=True)
        file_path = output_path / file_name
        file_path.write_bytes(response.content)

        print(f"   ✅ Pobrano: {file_path}")
        print(f"   Rozmiar: {len(response.content) / 1024:.2f} KB")
        return True
    else:
        print(f"   ❌ Błąd: {response.status_code}")
        return False


def main():
    """Uruchom wszystkie testy"""
    print("=" * 60)
    print("🐺 WolfTax Oferta Generator API - Testy")
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
    folder_name = None
    file_name = None
    try:
        success, folder, filename = test_generate_docx()
        results.append(("Generowanie DOCX", success))
        if success:
            folder_name = Path(folder).name
            file_name = filename
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Generowanie DOCX", False))

    # Test 4: PDF
    try:
        success, folder, filename = test_generate_pdf()
        results.append(("Generowanie PDF", success))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Generowanie PDF", False))

    # Test 5: JPG
    try:
        success, folder = test_generate_jpg()
        results.append(("Generowanie JPG", success))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Generowanie JPG", False))

    # Test 6: Lista ofert
    try:
        results.append(("Lista ofert", test_list_offers()))
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        results.append(("Lista ofert", False))

    # Test 7: Pobieranie
    if folder_name and file_name:
        try:
            results.append(("Pobieranie pliku", test_download(folder_name, file_name)))
        except Exception as e:
            print(f"   ❌ Błąd: {e}")
            results.append(("Pobieranie pliku", False))

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
