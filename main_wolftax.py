# -*- coding: utf-8 -*-
import asyncio
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import config_wolftax as config
from models_wolftax import WolftaxOfertaRequest, WolftaxOfertaResponse
from document_service_wolftax import WolftaxDocumentService
from conversion_service_wolftax import WolftaxConversionService


# Inicjalizacja serwisów przy starcie aplikacji
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.document_service = WolftaxDocumentService()
    app.state.conversion_service = WolftaxConversionService()
    print("✅ Serwisy WolfTax zainicjalizowane")
    print(f"📁 Katalog szablonów: {config.TEMPLATES_DIR}")
    print(f"📦 Katalog produktów: {config.PRODUKTY_DIR}")
    print(f"📤 Katalog wyjściowy: {config.OUTPUT_DIR}")

    yield

    # Shutdown
    print("🔴 Zamykanie aplikacji WolfTax...")


# Inicjalizacja FastAPI
app = FastAPI(
    title="WolfTax Oferta Generator API",
    description="API do generowania ofert WolfTax w formatach DOCX, PDF i JPG z multi-file szablonów",
    version="1.0.0",
    lifespan=lifespan
)

# Dodaj CORS middleware - permissive dla development i external IP
# Akceptuj localhost + external IP (184.174.33.251)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|184\.174\.33\.251)(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "WolfTax Oferta Generator API",
        "version": "1.0.0",
        "template": "multi-file (wolftax-oferta)",
        "endpoints": {
            "generate": "/api/generate-offer",
            "health": "/health",
            "list_produkty": "/api/list-produkty"
        }
    }


@app.get("/health")
async def health_check():
    """Szczegółowy health check"""
    templates_exist = all(
        (config.TEMPLATES_DIR / f["file"]).exists()
        for f in config.WOLFTAX_FILES
    )

    return {
        "status": "healthy",
        "templates_dir": str(config.TEMPLATES_DIR),
        "templates_exist": templates_exist,
        "templates_count": len(config.WOLFTAX_FILES),
        "produkty_dir": str(config.PRODUKTY_DIR),
        "produkty_count": len(list(config.PRODUKTY_DIR.glob("*.docx"))) if config.PRODUKTY_DIR.exists() else 0
    }


@app.options("/api/generate-offer")
async def options_generate_offer():
    """Handle CORS preflight request"""
    # CORS middleware już obsługuje preflight, ale dodajemy handler dla pewności
    return JSONResponse(
        content={"status": "ok"}
    )


@app.post("/api/generate-offer", response_model=WolftaxOfertaResponse)
async def generate_offer(request: WolftaxOfertaRequest):
    """
    Generuje ofertę WolfTax w wybranym formacie (DOCX/PDF/JPG)

    Struktura wyjściowa:
    output/
      oferta_XXXXX/
        oferta_XXXXX.docx (lub .pdf)
        jpg/
          page_1.jpg
          page_2.jpg
          ...

    Args:
        request: Dane oferty w formacie JSON

    Returns:
        WolftaxOfertaResponse z informacjami o wygenerowanych plikach
    """
    start_time = time.time()

    try:
        # Generuj unikalną nazwę
        file_id = str(uuid.uuid4())[:8]
        base_name = f"oferta_{file_id}"

        # Pobierz serwisy z state
        doc_service: WolftaxDocumentService = app.state.document_service
        conv_service: WolftaxConversionService = app.state.conversion_service

        print(f"\n{'='*60}")
        print(f"🚀 Rozpoczynam generowanie oferty WolfTax: {base_name}")
        print(f"{'='*60}")

        # 1. Generuj tymczasowy DOCX (łączenie wszystkich plików)
        temp_docx_path = config.TEMP_DIR / f"{base_name}.docx"
        print(f"\n📝 Krok 1: Generowanie DOCX...")
        await doc_service.generate_offer(request, temp_docx_path)
        print(f"✅ DOCX wygenerowany: {temp_docx_path}")

        # 2. Przetwórz do zorganizowanej struktury folderów
        print(f"\n📁 Krok 2: Organizowanie plików...")
        main_folder, main_file, jpg_paths = await conv_service.process_offer_to_organized_folder(
            temp_docx_path,
            base_name,
            request.output_format
        )

        print(f"✅ Pliki zorganizowane w: {main_folder}")
        print(f"   📄 Plik główny: {main_file.name}")
        print(f"   🖼️  Obrazy JPG: {len(jpg_paths)} plików")

        # Oblicz czas przetwarzania
        processing_time = time.time() - start_time

        # Przygotuj odpowiedź
        jpg_folder = main_folder / "jpg" if jpg_paths else None

        print(f"\n{'='*60}")
        print(f"✅ SUKCES! Oferta wygenerowana w {processing_time:.2f}s")
        print(f"{'='*60}\n")

        return WolftaxOfertaResponse(
            success=True,
            message="Oferta WolfTax wygenerowana pomyślnie",
            output_folder=str(main_folder),
            docx_path=str(main_file) if main_file else None,
            jpg_folder=str(jpg_folder) if jpg_folder else None,
            file_name=main_file.name if main_file else None,
            file_size_bytes=main_file.stat().st_size if main_file and main_file.exists() else None,
            format=request.output_format,
            processing_time_seconds=round(processing_time, 2),
            jpg_count=len(jpg_paths)
        )

    except Exception as e:
        # Obsługa błędów
        processing_time = time.time() - start_time
        error_msg = f"Błąd podczas generowania oferty: {str(e)}"
        print(f"\n❌ {error_msg}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": error_msg,
                "processing_time_seconds": round(processing_time, 2)
            }
        )


@app.get("/api/download/{folder_name}/{file_name}")
async def download_file(folder_name: str, file_name: str):
    """
    Pobiera wygenerowany plik z folderu oferty

    Args:
        folder_name: Nazwa folderu oferty (np. "oferta_abc123")
        file_name: Nazwa pliku do pobrania

    Returns:
        FileResponse z plikiem
    """
    file_path = config.OUTPUT_DIR / folder_name / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Plik nie został znaleziony")

    # Określ MIME type na podstawie rozszerzenia
    mime_types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"
    }

    mime_type = mime_types.get(file_path.suffix, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        filename=file_name
    )


@app.get("/api/download-jpg/{folder_name}/{jpg_name}")
async def download_jpg(folder_name: str, jpg_name: str):
    """
    Pobiera plik JPG z folderu jpg/

    Args:
        folder_name: Nazwa folderu oferty (np. "oferta_abc123")
        jpg_name: Nazwa pliku JPG (np. "page_1.jpg")

    Returns:
        FileResponse z plikiem JPG
    """
    file_path = config.OUTPUT_DIR / folder_name / "jpg" / jpg_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Plik JPG nie został znaleziony")

    return FileResponse(
        path=str(file_path),
        media_type="image/jpeg",
        filename=jpg_name
    )


@app.get("/api/list-jpgs/{folder_name}")
async def list_jpgs(folder_name: str):
    """
    Zwraca listę plików JPG z folderu oferty

    Args:
        folder_name: Nazwa folderu oferty (np. "oferta_abc123")

    Returns:
        Lista nazw plików JPG
    """
    jpg_folder = config.OUTPUT_DIR / folder_name / "jpg"

    if not jpg_folder.exists():
        return {"success": False, "jpgs": [], "message": "Folder JPG nie istnieje"}

    jpg_files = sorted([f.name for f in jpg_folder.glob("*.jpg")])

    return {
        "success": True,
        "folder_name": folder_name,
        "jpgs": jpg_files,
        "count": len(jpg_files)
    }


@app.get("/api/list-produkty")
async def list_produkty():
    """
    Zwraca listę dostępnych produktów z folderu produkty/

    Returns:
        Lista nazw plików produktów
    """
    try:
        produkty_files = sorted([f.name for f in config.PRODUKTY_DIR.glob("*.docx")])
        return {
            "success": True,
            "count": len(produkty_files),
            "produkty": produkty_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd odczytu katalogu produktów: {str(e)}")


@app.get("/api/list-offers")
async def list_offers():
    """
    Zwraca listę wygenerowanych ofert w katalogu output/

    Returns:
        Lista folderów ofert
    """
    try:
        offer_folders = [
            {
                "name": f.name,
                "created": f.stat().st_mtime,
                "files": [file.name for file in f.iterdir() if file.is_file()]
            }
            for f in config.OUTPUT_DIR.iterdir()
            if f.is_dir() and f.name.startswith("oferta_")
        ]

        # Sortuj po dacie utworzenia (najnowsze pierwsze)
        offer_folders.sort(key=lambda x: x["created"], reverse=True)

        return {
            "success": True,
            "count": len(offer_folders),
            "offers": offer_folders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd odczytu katalogu output: {str(e)}")


# Uruchomienie serwera
if __name__ == "__main__":
    import uvicorn

    print("🐺 Uruchamianie WolfTax Oferta Generator API...")
    print(f"🌐 Adres: http://{config.HOST}:{config.PORT}")
    print(f"📚 Dokumentacja: http://{config.HOST}:{config.PORT}/docs")

    uvicorn.run(
        "main_wolftax:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
