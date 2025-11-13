# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date


class WolftaxOfertaRequest(BaseModel):
    """Model dla zapytania do API generowania oferty WolfTax"""

    # Podstawowe dane (dopasowane do placeholderów w szablonie)
    nazwa_firmy_klienta: str = Field(..., description="Nazwa firmy klienta", alias="NazwaFirmyKlienta")
    sygnatura_sprawy: Optional[str] = Field(None, description="Sygnatura sprawy", alias="Sygnatura-sprawy")
    temat: str = Field(..., description="Temat oferty", alias="Temat")
    termin: Optional[str] = Field(None, description="Termin realizacji", alias="Termin")
    waznosc_oferty: str = Field(..., description="Ważność oferty do", alias="waznosc-oferty")

    # Produkty - lista nazw plików z folderu produkty (np. ["1.docx", "2.docx"])
    # Może być pusta [] - wtedy generuje się tylko podstawowy szablon bez produktów
    produkty: List[str] = Field(default_factory=list, description="Lista nazw plików produktów (z folderu produkty/)")

    # Finansowe
    wynagrodzenie: Optional[float] = Field(None, description="Wynagrodzenie w PLN", alias="Wynagrodzenie")
    szacowany_czas_pracy: Optional[int] = Field(None, description="Szacowany czas pracy (rbh)", alias="Szacowanyczaspracy")

    # Format wyjściowy
    output_format: Literal["docx", "pdf", "jpg"] = Field(
        "docx",
        description="Format wyjściowy: docx, pdf lub jpg (100 DPI)"
    )

    class Config:
        populate_by_name = True


class WolftaxOfertaResponse(BaseModel):
    """Model odpowiedzi API"""
    success: bool
    message: str
    output_folder: Optional[str] = None  # Folder z całą ofertą
    docx_path: Optional[str] = None      # Ścieżka do pliku DOCX
    jpg_folder: Optional[str] = None     # Folder z plikami JPG
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    format: str
    processing_time_seconds: Optional[float] = None
    jpg_count: Optional[int] = None      # Liczba wygenerowanych JPG
