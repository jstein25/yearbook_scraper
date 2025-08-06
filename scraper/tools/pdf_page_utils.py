"""File for getting page objects.

Connects page numbers to the actual page objects
they're connected to for writing new, shortened pdfs.
"""
from pypdf import PdfReader, PdfWriter


def get_pages_from_nums(pdf_path, page_nums: list):
    """
    Extracts specified pages from a PDF and returns a PdfWriter instance containing those pages.

    Args:
        pdf_path: Path to the PDF file to extract pages from.
        page_nums: List of page numbers (0-based indices) to extract.

    Returns:
        PdfWriter: An instance containing only the specified pages.
    
    Example:
        writer = get_pages_from_nums("input.pdf", [0, 2, 4])
        with open("output.pdf", "wb") as f:
            writer.write(f)
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page_num in page_nums:
        writer.add_page(reader.pages[page_num])
    return writer