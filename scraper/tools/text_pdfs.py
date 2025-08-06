"""Functions for text pdf handling.

Allows for checking whether a pdf contains text to decide whether
to search via this text handler (get_page_nums_from_query_text) or via ocr.
"""
from pypdf import PdfReader


def pdf_has_text(pdf_path):
    """Check if pdf has extractable text.

    Returns true if pdf contains text.
    Signals use for ocr to search document.

    Args:
        pdf_path: path to pdf.

    Returns:
        Boolean whether pdf has text.

    Example usage:
        if not is_text_file(pdf_path):
            do_some_ocr_functions()
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return bool(text)


def get_page_nums_from_query_text(pdf_path, query):
    """Search for a string in pdf.

    Args:
        str: string to search for
        pdf_path: pdf to search

    Returns:
        page_nums: a list of page numbers on which the string occurs.
    """
    reader = PdfReader(pdf_path)
    page_nums = []
    for page in reader.pages:
        if query.lower() in page.extract_text().lower():
            page_nums.append(page.page_number)
    return page_nums