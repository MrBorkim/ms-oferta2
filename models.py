from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date


class OfertaRequest(BaseModel):
    """Model dla zapytania do API generowania oferty"""

    # Podstawowe dane
    nip: str = Field(..., description="NIP klienta", alias="KLIENT(NIP)")
    data_oferty: str = Field(..., description="Data oferty", alias="Oferta z dnia")
    wazna_do: str = Field(..., description="Oferta ważna do")
    firma: str = Field(..., description="Nazwa Twojej firmy", alias="firmaM")

    # Szczegóły zlecenia
    temat: Optional[str] = Field(None, description="Temat zlecenia")
    kategoria: Optional[str] = Field(None, description="Kategoria")
    opis: Optional[str] = Field(None, description="Opis zlecenia")

    # Produkty - lista nazw plików z folderu produkty (np. ["1.docx", "2.docx"])
    produkty: List[str] = Field(..., description="Lista nazw plików produktów (z folderu produkty/)")

    # Finansowe
    cena: Optional[float] = Field(None, description="Cena usługi w PLN")
    rbg: Optional[int] = Field(None, description="Limit roboczogodzin", alias="RBG")
    uzasadnienie: Optional[str] = Field(None, description="Uzasadnienie kosztu")

    # Format wyjściowy
    output_format: Literal["docx", "pdf", "jpg"] = Field(
        "docx",
        description="Format wyjściowy: docx, pdf lub jpg (100 DPI)"
    )

    class Config:
        populate_by_name = True


class OfertaResponse(BaseModel):
    """Model odpowiedzi API"""
    success: bool
    message: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    format: str
    processing_time_seconds: Optional[float] = None
