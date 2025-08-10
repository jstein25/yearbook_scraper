"""File for getting page objects.

Connects page numbers to the actual page objects
they're connected to for writing new, shortened pdfs.
"""
from typing import List
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF

def get_pages_from_nums(pdf_path, page_nums: List[int]) -> PdfWriter:
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


def get_page_nums_near(pdf_path, page_num, window) -> List[int]:
    """Uses an interval of +/- window to return list of page_nums around page_num.
    """
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    start_page = max(page_num - window, 0)
    end_page = min(page_num + window + 1, num_pages)
    return start_page, end_page


def create_pdf_with_text(output_path, text):
    """
    Creates a single-page PDF with the given text using fpdf.

    Args:
        output_path: Path to save the generated PDF.
        text: The text to write on the PDF page.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)