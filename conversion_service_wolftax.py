# -*- coding: utf-8 -*-
import asyncio
import os
import platform
from pathlib import Path
from typing import List, Tuple
from pdf2image import convert_from_path
import config_wolftax as config


class WolftaxConversionService:
    """Serwis do konwersji dokumentów DOCX -> PDF -> JPG z organizacją folderów"""

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

        for i, image in enumerate(images, start=1):
            jpg_path = output_dir / f"page_{i}.jpg"

            # Zapisz asynchronicznie
            await loop.run_in_executor(
                None,
                image.save,
                str(jpg_path),
                "JPEG"
            )

            jpg_paths.append(jpg_path)

        return jpg_paths

    async def process_offer_to_organized_folder(
        self,
        docx_path: Path,
        base_folder_name: str,
        output_format: str
    ) -> Tuple[Path, Path, List[Path]]:
        """
        Przetwarza ofertę i organizuje pliki w strukturze:
        output/
          base_folder_name/
            base_folder_name.docx (lub .pdf)
            jpg/
              page_1.jpg
              page_2.jpg
              ...

        Args:
            docx_path: Ścieżka do wygenerowanego DOCX
            base_folder_name: Nazwa folderu (np. "oferta_abc123")
            output_format: Format wyjściowy ("docx", "pdf", "jpg")

        Returns:
            Tuple[Path, Path, List[Path]]: (folder główny, plik główny, lista JPG)
        """
        # Utwórz folder główny
        main_folder = config.OUTPUT_DIR / base_folder_name
        main_folder.mkdir(exist_ok=True, parents=True)

        # Folder na JPG
        jpg_folder = main_folder / "jpg"
        jpg_folder.mkdir(exist_ok=True, parents=True)

        # Plik główny w zależności od formatu
        if output_format == "docx":
            # Przenieś DOCX do folderu głównego
            final_docx = main_folder / f"{base_folder_name}.docx"
            if docx_path != final_docx:
                docx_path.rename(final_docx)

            # Generuj JPG z DOCX
            temp_pdf = config.TEMP_DIR / f"{base_folder_name}.pdf"
            try:
                await self.convert_to_pdf(final_docx, temp_pdf)
                jpg_paths = await self.convert_to_jpg(temp_pdf, jpg_folder)
            finally:
                if temp_pdf.exists():
                    temp_pdf.unlink()

            return main_folder, final_docx, jpg_paths

        elif output_format == "pdf":
            # Konwertuj DOCX -> PDF
            final_pdf = main_folder / f"{base_folder_name}.pdf"
            await self.convert_to_pdf(docx_path, final_pdf)

            # Usuń tymczasowy DOCX
            if docx_path.exists():
                docx_path.unlink()

            # Generuj JPG z PDF
            jpg_paths = await self.convert_to_jpg(final_pdf, jpg_folder)

            return main_folder, final_pdf, jpg_paths

        elif output_format == "jpg":
            # Konwertuj DOCX -> PDF -> JPG
            temp_pdf = config.TEMP_DIR / f"{base_folder_name}.pdf"
            try:
                await self.convert_to_pdf(docx_path, temp_pdf)
                jpg_paths = await self.convert_to_jpg(temp_pdf, jpg_folder)
            finally:
                if temp_pdf.exists():
                    temp_pdf.unlink()

            # Usuń tymczasowy DOCX
            if docx_path.exists():
                docx_path.unlink()

            # Główny plik to pierwszy JPG
            main_file = jpg_paths[0] if jpg_paths else None

            return main_folder, main_file, jpg_paths

        else:
            raise ValueError(f"Nieobsługiwany format: {output_format}")
