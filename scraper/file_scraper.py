"""Scan yearbook pdfs.

Run this program using if __name__ == '__main__' to 
scan individual files. Otherwise, this is the helper function for
directory_scraper, as each file in the directory goes through this program.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

from scraper.tools import text_pdfs as text
from scraper.tools import pdf_page_utils as p
from scraper.tools import ocr_pdfs as ocr


def main(pdf_path, query):
    """Main method for file_scraper returning pages from search.

    Search pages by either running this program as a module
    and inputing parameters in if __name__ statement, or through loop
    in directory_scraper.py.
    NOTE: ASSUMES THAT FIRST MATCH IS A PART OF TABLE OF CONTENTS

    Args:
        pdf_path: path to pdf for scraping.
        query: search term to look for.
    
    Returns:
        Pages from search as PdfWriter instance.
        If # of matches > 2, return only after the 2nd match.
    """
    # search and upload
    print(f"Processing: {pdf_path.name}")
    print("Attempting to extract text...")
    page_nums = []
    if text.pdf_has_text(pdf_path):
        print("Text pdf registered.")
        print("Searching pdf for query...")
        page_nums = text.get_page_nums_from_query_text(pdf_path, query)
    else:
        print("Scanned pdf registered.")
        print("Searching pdf for query...")
        page_nums = ocr.get_page_nums_from_query_ocr(pdf_path, query)

    match len(page_nums):
        case 0:
            print("No matches found.")
            return p.get_pages_from_nums(pdf_path, [])
        case 1:
            print("Only 1 match found. Returning match.")
            return p.get_pages_from_nums(pdf_path, page_nums)
        case _:
            print(f"{len(page_nums)} matches found, returning matches after ToC.")
            page_nums = page_nums[1:]
            return p.get_pages_from_nums(pdf_path, page_nums)


if __name__ == "__main__":
    load_dotenv()
    FILE_PATH = Path(os.getenv('FILE_PATH'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR'))
    print("Enter your query: ", end="")
    QUERY = input()

    output_pdf = main(FILE_PATH, QUERY)
    output_path = OUTPUT_DIR / f"scraped-{FILE_PATH.stem}.pdf"

    with open(output_path, "wb") as f:
        output_pdf.write(f)