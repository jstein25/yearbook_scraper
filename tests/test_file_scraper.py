from pypdf import PdfReader
from scraper.file_scraper import main
from pdf2image import convert_from_path
import pytesseract


def test_search_text_pdf(pdf_with_text, tmp_path):
    """Integration test: file_scraper returns pages 2 and 3
    of pdf_with_text based on the search."""
    output_pdf = tmp_path / "output.pdf"
    writer = main(pdf_with_text, "Hello")
    with open(output_pdf, "wb") as f:
        writer.write(f)
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 2
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
    with open(output_pdf, "wb") as f:
        writer.write(f)
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 0


def test_search_scanned_pdf(scanned_pdf, tmp_path):
    """Integration test: file_scraper returns correct pages
    from a scanned (OCR) PDF based on the search."""
    output_pdf = tmp_path / "output_scanned.pdf"
    writer = main(scanned_pdf, "this")
    with open(output_pdf, "wb") as f:
        writer.write(f)
    images = convert_from_path(output_pdf)
    # Confirm that "this" is present in at least one page (OCR)
    found = any(
        "this" in pytesseract.image_to_string(image).lower()
        for image in images
    )
    assert found, '"this" not found in any scanned page'