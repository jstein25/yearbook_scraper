from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
import tempfile
from pathlib import Path
import pytest

from scraper.directory_scraper import main as directory_main

def dummy_scrape(pdf_path, query, verbose):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    return writer

def test_directory_scraper_creates_merged_pdf(monkeypatch):
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        for i in range(2):
            pdf_path = Path(input_dir) / f"{2000+i}_test.pdf"
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Times", size=12)
            pdf.cell(40, 10, f"Dummy PDF {i}")
            pdf.output(str(pdf_path))

        monkeypatch.setenv("INPUT_DIR", input_dir)
        monkeypatch.setenv("OUTPUT_DIR", output_dir)

        import scraper.directory_scraper
        monkeypatch.setattr(scraper.directory_scraper, "scrape", dummy_scrape)

        directory_main("TestQuery", verbose=False)

        output_pdf = Path(output_dir) / f"TestQuery-scraped-{Path(input_dir).name}.pdf"
        assert output_pdf.exists()
        reader = PdfReader(str(output_pdf))
        assert len(reader.pages) == 4