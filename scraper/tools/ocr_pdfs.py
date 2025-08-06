"""Tools for handling scanned pdfs using ocr.

Searches document for query by first converting pdf to images
and then using ocr.
"""
from pdf2image import convert_from_path
import pytesseract


def get_page_nums_from_query_ocr(pdf_path, query):
    """Get pages on which query appears.

    Searches a scanned pdf. Use in conjunction with
    uploads.get_pages_from_nums() to create a new pdf
    with these pages.

    Args:
        pdf_path: Path to pdf.
        query: search term to look for.

    Returns:
        page_nums: page numbers on which the term appears.
    
    Example usage:
        page_nums = get_page_nums_from_query_ocr(input_pdf, "translations")
        pages = pdf_page_utils.get_pages_from_nums(input_pdf, page_nums)
    """
    images = convert_from_path(pdf_path)
    page_nums = []
    current_page = 0
    for image in images:
        text = pytesseract.image_to_string(image).lower()
        if query.lower() in text:
            page_nums.append(current_page)
            current_page += 1
    return page_nums