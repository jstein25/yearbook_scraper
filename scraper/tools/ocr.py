"""Tools for handling scanned pdfs using ocr.

Searches document for query by first converting pdf to images
and then using ocr.
"""
from pdf2image import convert_from_path
import pytesseract


def get_page_nums_from_query_ocr(pdf_path, query, start, end):
    """Get pages on which query appears.

    Searches a portion of a scanned pdf based on start and ending
    args to find where a query appears. Outputs the page numbers from
    the broader pdf. This is to optimize OCR.

    Args:
        pdf_path: Path to pdf.
        query: search term to look for.
        start: page to begin search
        end: page to end search

    Returns:
        page_nums: page numbers on which the term appears.
    
    Example usage:
        page_nums = get_page_nums_from_query_ocr(input_pdf, "translations")
        pages = pdf_page_utils.get_pages_from_nums(input_pdf, page_nums)
    """
    images = convert_from_path(pdf_path, first_page=start+1, last_page=end)
    page_nums = []
    for idx, image in enumerate(images):
        text = pytesseract.image_to_string(image).lower()
        if query.lower() in text:
            page_nums.append(start + idx)
    return page_nums