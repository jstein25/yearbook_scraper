"""Scan yearbook pdfs.

Run this program using if __name__ == '__main__' to 
scan individual files. Otherwise, this is the helper function for
directory_scraper, as each file in the directory goes through this program.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

from scraper.tools import text_pdfs as text
from scraper.tools import pdf_page_utils as p
from scraper.tools import ocr
from scraper.tools import tablelist_utils as tbl
from scraper.tools.tablelist_utils import TableListNotFoundError


def main(pdf_path, query, verbose=True):
    """Main method for file_scraper returning pages from search.

    Search pages by either running this program as a module
    and inputing parameters in if __name__ statement, or through loop
    in directory_scraper.py.

    Args:
        pdf_path: path to pdf for scraping.
        query: search term to look for.
    
    Returns:
        Pages from search as PdfWriter instance.
        If # of matches > 2, return only after the 2nd match.
    """
    if verbose:
        print(f"PROCESSING: {pdf_path.name}")
        print("Attempting to extract text...")
    page_nums = []
    # branch logic according to text vs scanned pdf
    if text.pdf_has_text(pdf_path):
        if verbose:
            print("Text pdf registered.")
            print("Searching pdf for query...")
        page_nums = text.get_page_nums_from_query_text(pdf_path, query)

    else:
        # is ocr
        if verbose:
            print("Scanned pdf registered.")
            print("Checking for list of tables.")
        try:
            relevant_page_num = tbl.search_table_list(pdf_path, query)
        except TableListNotFoundError:
            print("Pdf does not contain visible list of tables.")
            print("Scan pdf using ocr anyways? (this may take a while for large files)")
            print("Y/n: ", end="")
            user_input = input()
            if user_input != "Y":
                return
            # do ocr on whole document
            reader = PdfReader(pdf_path)
            start = 0
            end = len(reader.pages)
            page_nums = ocr.get_page_nums_from_query_ocr(pdf_path, query, start, end)
        
        if verbose:
            print("Table list found.")

        if relevant_page_num is None and verbose:
            print("No page number found in table list")
            return
        elif relevant_page_num is not None and verbose:
            print(f"Page number found from table list: {relevant_page_num}")
            print(f"Searching pages near {relevant_page_num}...")
            start, end = p.get_page_nums_near(pdf_path, relevant_page_num, 5)
            page_nums = ocr.get_page_nums_from_query_ocr(pdf_path, query, start, end)
        else:
            return
    
                
    match len(page_nums):
        case 0:
            if verbose:
                print("No matches found.")
            return

        case 1:
            if verbose:
                print("1 match found. Returning match.")
            return p.get_pages_from_nums(pdf_path, page_nums)

        case _:
            if verbose:
                print(f"{len(page_nums)} matches found. Returning all pages.")
            return p.get_pages_from_nums(pdf_path, page_nums)


if __name__ == "__main__":
    load_dotenv()
    FILE_PATH = Path(os.getenv('FILE_PATH'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR'))

    print("Enter your query: ", end="")
    QUERY = input()

    output_pdf = main(FILE_PATH, QUERY, verbose=True)
    if output_pdf is not None:
        output_path = OUTPUT_DIR / f"scraped-{FILE_PATH.stem}.pdf"

        with open(output_path, "wb") as f:
            output_pdf.write(f)

        print(f"output file written to {output_path}.")