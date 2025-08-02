"""
Read pdf and find tables with
given title in Yearbooks and export to pdf.
"""
import pdfplumber

def get_tables_from_file(file):
    """Get tables from file.

    If file has text, will use pdfplumber to
    extract tables. Else, may require ocr.
    Args:
        file: File to read.
    """
    tables = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            if page_tables:
                tables.extend(page_tables)
    if not tables:
        raise ValueError("Table processing error. PDF is likely scanned.")
    
    return tables