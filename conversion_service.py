import asyncio
import os
import platform
from pathlib import Path
from typing import List
from pdf2image import convert_from_path
import config


class ConversionService:
    """Serwis do konwersji dokumentów DOCX -> PDF -> JPG"""

    def __init__(self):
        self.dpi = config.JPG_DPI

    async def convert_to_pdf(self, docx_path: Path, pdf_path: Path) -> Path:
        """
        Konwertuje DOCX do PDF używając LibreOffice (szybka metoda)

        Args:
            docx_path: Ścieżka do pliku DOCX
            pdf_path: Ścieżka do zapisu PDF

        Returns:
            Path: Ścieżka do wygenerowanego PDF
        """
        # Sprawdź system operacyjny i wybierz odpowiednią metodę
        system = platform.system()

        if system == "Linux":
            # Na Linuxie użyj LibreOffice (najszybsza opcja)
            await self._convert_with_libreoffice(docx_path, pdf_path)
        elif system == "Darwin":  # macOS
            # Na macOS użyj LibreOffice jeśli dostępny
            try:
                await self._convert_with_libreoffice(docx_path, pdf_path)
            except Exception:
                # Fallback do docx2pdf
                await self._convert_with_docx2pdf(docx_path, pdf_path)
        elif system == "Windows":
            # Na Windows użyj docx2pdf (używa MS Word COM API)
            await self._convert_with_docx2pdf(docx_path, pdf_path)
        else:
            raise RuntimeError(f"Nieobsługiwany system operacyjny: {system}")

        return pdf_path

    async def _convert_with_libreoffice(self, docx_path: Path, pdf_path: Path):
        """Konwersja używając LibreOffice (najszybsza dla Linuxa)"""
        output_dir = pdf_path.parent

        # Komenda LibreOffice
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(docx_path)
        ]

        # Uruchom asynchronicznie
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {stderr.decode()}")

        # LibreOffice tworzy plik z nazwą bazową docx + .pdf
        generated_pdf = output_dir / f"{docx_path.stem}.pdf"

        # Jeśli nazwa docelowa jest inna, przenieś plik
        if generated_pdf != pdf_path:
            generated_pdf.rename(pdf_path)

    async def _convert_with_docx2pdf(self, docx_path: Path, pdf_path: Path):
        """Konwersja używając docx2pdf (dla Windows/macOS fallback)"""
        from docx2pdf import convert

        # docx2pdf działa synchronicznie, więc użyj executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            convert,
            str(docx_path),
            str(pdf_path)
        )

    async def convert_to_jpg(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        Konwertuje PDF do JPG (100 DPI) - każda strona jako osobny plik

        Args:
            pdf_path: Ścieżka do pliku PDF
            output_dir: Katalog do zapisu plików JPG

        Returns:
            List[Path]: Lista ścieżek do wygenerowanych plików JPG
        """
        output_dir.mkdir(exist_ok=True, parents=True)

        # Konwertuj PDF do obrazów
        loop = asyncio.get_event_loop()
        images = await loop.run_in_executor(
            None,
            convert_from_path,
            str(pdf_path),
            self.dpi
        )

        # Zapisz obrazy jako JPG
        jpg_paths = []
        base_name = pdf_path.stem

        for i, image in enumerate(images, start=1):
            jpg_path = output_dir / f"{base_name}_page_{i}.jpg"

            # Zapisz asynchronicznie
            await loop.run_in_executor(
                None,
                image.save,
                str(jpg_path),
                "JPEG"
            )

            jpg_paths.append(jpg_path)

        return jpg_paths

    async def convert_docx_to_jpg(self, docx_path: Path, output_dir: Path) -> List[Path]:
        """
        Konwertuje DOCX -> PDF -> JPG w jednym kroku

        Args:
            docx_path: Ścieżka do pliku DOCX
            output_dir: Katalog do zapisu plików JPG

        Returns:
            List[Path]: Lista ścieżek do wygenerowanych plików JPG
        """
        # Stwórz tymczasowy plik PDF
        temp_pdf = config.TEMP_DIR / f"{docx_path.stem}.pdf"

        try:
            # Konwertuj DOCX -> PDF
            await self.convert_to_pdf(docx_path, temp_pdf)

            # Konwertuj PDF -> JPG
            jpg_paths = await self.convert_to_jpg(temp_pdf, output_dir)

            return jpg_paths

        finally:
            # Usuń tymczasowy PDF
            if temp_pdf.exists():
                temp_pdf.unlink()
