from pypdf import PdfReader
from scraper.file_scraper import main
from pdf2image import convert_from_path
import pytesseract
import scraper.tools.tablelist_utils as tbl


def test_search_text_pdf(pdf_with_text, tmp_path):
    """Integration test: file_scraper returns pages 2 and 3
    of pdf_with_text based on the search."""
    output_pdf = tmp_path / "output.pdf"
    writer = main(pdf_with_text, "Hello")
    with open(output_pdf, "wb") as f:
        writer.write(f)
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 3
    content = "".join(
        page.extract_text() or ""
        for page in reader.pages
    )
    assert "Hello" in content


def test_text_search_returns_empty_for_missing_query(
    pdf_with_text, tmp_path
):
    """Integration test: file_scraper returns empty PDF for
    missing query."""
    output_pdf = tmp_path / "output_empty.pdf"
    writer = main(pdf_with_text, "test-string")
    assert writer is None


def test_search_scanned_pdf(scanned_pdf, tmp_path, monkeypatch):
    """Integration test: file_scraper returns correct pages
    from a scanned (OCR) PDF based on the search, simulating a table list hit."""
    # Simulate finding a relevant page number in the table list (e.g., page 0)
    monkeypatch.setattr(tbl, "search_table_list", lambda *a, **kw: 0)
    output_pdf = tmp_path / "output_scanned.pdf"
    writer = main(scanned_pdf, "types")
    with open(output_pdf, "wb") as f:
        writer.write(f)
    images = convert_from_path(output_pdf)
    # Confirm that "this" is present in at least one page (OCR)
    found = any(
        "types" in pytesseract.image_to_string(image).lower()
        for image in images
    )
    assert found