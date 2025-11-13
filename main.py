# -*- coding: utf-8 -*-
import asyncio
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import config
from models import OfertaRequest, OfertaResponse
from document_service import DocumentService
from conversion_service import ConversionService
import traceback


# Inicjalizacja serwis�w przy starcie aplikacji
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.document_service = DocumentService()
    app.state.conversion_service = ConversionService()
    print(" Serwisy zainicjalizowane")
    print(f"=� Katalog szablon�w: {config.TEMPLATES_DIR}")
    print(f"=� Katalog produkt�w: {config.PRODUKTY_DIR}")
    print(f"=� Katalog wyj[ciowy: {config.OUTPUT_DIR}")

    yield

    # Shutdown
    print("=� Zamykanie aplikacji...")


# Inicjalizacja FastAPI
app = FastAPI(
    title="Oferta Generator API",
    description="API do generowania ofert w formatach DOCX, PDF i JPG z szablon�w",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Oferta Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/api/generate-offer",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Szczeg�Bowy health check"""
    return {
        "status": "healthy",
        "templates_dir": str(config.TEMPLATES_DIR),
        "template_exists": config.TEMPLATE_FILE.exists(),
        "produkty_dir": str(config.PRODUKTY_DIR),
        "produkty_count": len(list(config.PRODUKTY_DIR.glob("*.docx"))) if config.PRODUKTY_DIR.exists() else 0
    }


@app.post("/api/generate-offer", response_model=OfertaResponse)
async def generate_offer(request: OfertaRequest):
    """
    Generuje ofert w wybranym formacie (DOCX/PDF/JPG)

    Args:
        request: Dane oferty w formacie JSON

    Returns:
        OfertaResponse z linkiem do pobrania pliku
    """
    start_time = time.time()

    try:
        # Generuj unikaln nazw pliku
        file_id = str(uuid.uuid4())[:8]
        base_filename = f"oferta_{file_id}"

        # Pobierz serwisy z state
        doc_service: DocumentService = app.state.document_service
        conv_service: ConversionService = app.state.conversion_service

        # 1. Generuj DOCX
        docx_path = config.OUTPUT_DIR / f"{base_filename}.docx"
        await doc_service.generate_offer(request, docx_path)

        # 2. Konwersja do |danego formatu
        final_path = docx_path
        final_format = "docx"

        if request.output_format == "pdf":
            # Konwertuj do PDF
            pdf_path = config.OUTPUT_DIR / f"{base_filename}.pdf"
            await conv_service.convert_to_pdf(docx_path, pdf_path)
            final_path = pdf_path
            final_format = "pdf"

            # UsuD tymczasowy DOCX
            docx_path.unlink()

        elif request.output_format == "jpg":
            # Konwertuj do JPG
            jpg_dir = config.OUTPUT_DIR / base_filename
            jpg_paths = await conv_service.convert_docx_to_jpg(docx_path, jpg_dir)

            # Zwr� pierwsz stron (mo|na rozszerzy o archiwum ZIP)
            final_path = jpg_paths[0] if jpg_paths else None
            final_format = "jpg"

            # UsuD tymczasowy DOCX
            docx_path.unlink()

            if not final_path:
                raise HTTPException(status_code=500, detail="Nie udaBo si wygenerowa JPG")

        # Oblicz czas przetwarzania
        processing_time = time.time() - start_time

        # Zwr� odpowiedz
        return OfertaResponse(
            success=True,
            message="Oferta wygenerowana pomy[lnie",
            file_path=str(final_path),
            file_name=final_path.name,
            file_size_bytes=final_path.stat().st_size if final_path.exists() else None,
            format=final_format,
            processing_time_seconds=round(processing_time, 2)
        )

    except Exception as e:
        # Detailed logging
        print(f"ERROR in generate_offer: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        # ObsBuga bBd�w
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"BBd podczas generowania oferty: {str(e)}",
                "processing_time_seconds": round(processing_time, 2)
            }
        )


@app.get("/api/download/{file_name}")
async def download_file(file_name: str):
    """
    Pobiera wygenerowany plik

    Args:
        file_name: Nazwa pliku do pobrania

    Returns:
        FileResponse z plikiem
    """
    file_path = config.OUTPUT_DIR / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Plik nie zostaB znaleziony")

    # Okre[l MIME type na podstawie rozszerzenia
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


@app.get("/api/list-produkty")
async def list_produkty():
    """
    Zwraca list dostpnych produkt�w z folderu produkty/

    Returns:
        Lista nazw plik�w produkt�w
    """
    try:
        produkty_files = sorted([f.name for f in config.PRODUKTY_DIR.glob("*.docx")])
        return {
            "success": True,
            "count": len(produkty_files),
            "produkty": produkty_files
        }
    except Exception as e:
        # Detailed logging
        print(f"ERROR in generate_offer: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"BBd odczytu katalogu produkt�w: {str(e)}")


# Uruchomienie serwera
if __name__ == "__main__":
    import uvicorn

    print("=� Uruchamianie Oferta Generator API...")
    print(f"=� Adres: http://{config.HOST}:{config.PORT}")
    print(f"=� Dokumentacja: http://{config.HOST}:{config.PORT}/docs")

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
