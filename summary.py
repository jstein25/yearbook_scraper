"""
This program scrapes scanned yearbook pdfs and provides output
based on matches from a given search.

This submission is a one-page summary of individual files which
can be found at https://github.com/jstein25/yearbook_scraper. Tests for
the program are also provided in the Github repo for this project.
"""

# directory_scraper.py ------------------------------
"""Scan directories containing yearbook pdfs.

Note: assumes pdfs begin with their year for sorting.
"""
import os
from pathlib import Path
import tempfile

from dotenv import load_dotenv
from pypdf import PdfReader, PdfWriter

from scraper.file_scraper import main as scrape
from scraper.tools import pdf_page_utils as p

def main(query, verbose):
    load_dotenv()
    INPUT_DIR = Path(os.getenv('INPUT_DIR'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR'))
    merged_writer = PdfWriter()

    files_not_written = []

    for pdf in sorted(os.listdir(INPUT_DIR)):
        # guard against non-pdf files
        if not pdf.lower().endswith(".pdf"):
            continue
        pdf_path = INPUT_DIR / pdf

        if verbose:
            # increase legibility
            print()
            print()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            temp_info_path = tmp.name
        p.create_pdf_with_text(temp_info_path, f"File: {pdf_path.stem}\nQuery: {query}")
        
        info_reader = PdfReader(temp_info_path)
        merged_writer.add_page(info_reader.pages[0])
        
        os.remove(temp_info_path)

        # then scrape
        output_writer = scrape(pdf_path, query, verbose)
        if output_writer is not None:
            for page in output_writer.pages:
                merged_writer.add_page(page)
            if verbose:
                print("Scraped pages added.")
        else:
            if verbose:
                files_not_written.append(pdf_path.stem)
                print("Moving to next file.")
        
        new_file_name = f"{query}-scraped-{INPUT_DIR.name}.pdf"
        output_path = OUTPUT_DIR / new_file_name
    with open(output_path, "wb") as f:
        merged_writer.write(f)
    if verbose:
        print(f"{new_file_name} written to output directory.")
        print("Files not written: " + str(files_not_written))

if __name__ == "__main__":
    print("Enter your query: ", end="")
    query = input()
    main(query, verbose=True)


# file_scraper.py ------------------------------
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


# tools.ocr.py ------------------------------
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


# tools.pdf_page_utils.py ------------------------------
"""File for getting page objects.
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


# tools.tablelist_utils.py ------------------------------
"""Use ocr to get relevant page for extraction from a
list of tables appearing at the beginning of the pdf.
"""
import pytesseract
from pdf2image import convert_from_path
import re


class TableListNotFoundError(Exception):
    """Raised when a table list is not found in the PDF"""
    pass


def search_table_list(pdf_path, query):
    """Searches table list for query and returns relevant page number.

    Locates the table list, searches for the query, and returns the page number corresponding to
    where that table most likely appears in the actual pdf. Should be used with a range of +/- 5
    when doing actual ocr on the output page to account for possible errors in the table-list location
    process.

    Args:
        pdf_path: path to the pdf to search.
        query: search term

    Returns:
        logical page: where the table appears.

    Raises:
        TableListNotFoundError: The text "table list" or "list of tables" could not
        be found within the first 25 pages.

    Example usage:
        try:
            relevant_page_num = search_table_list(pdf_path, query)
        Except TableListNotFoundError:
            # do logic
        if relevant_page_num is None:
            print("relevant page not found")
        else:
            final_table = do_ocr_around_relevant_page_num(relevant_page_num)
    """
    # first, extract images.
    images = extract_first_n_images(pdf_path, 25)
    # print("[DEBUG] image extraction done")
    start_page = get_table_list_start_page(images)
    # print(f"[DEBUG] start page: {start_page}")
    table_list = get_english_table_list(images, start_page)
    for text in table_list:
        if query.lower() in text.lower():
            # print(f"[DEBUG] query found in text: {text}")
            written_page = get_page_nums_near_query(text, query)
            print(f"[DEBUG] Written page: {written_page}")
            if written_page is not None:
                start_page_of_body = start_page + len(table_list)
                actual_pdf_page = start_page_of_body + (written_page - 1)
                return actual_pdf_page
            return None
    return None


def extract_first_n_images(pdf_path, n):
    return convert_from_path(pdf_path, first_page=1, last_page=n)


def get_table_list_start_page(images):
    """Find table list start page and raise TableListNotFoundError if not found.
    """
    for idx, image in enumerate(images):
        text = pytesseract.image_to_string(image).lower()
        if "table list" in text or "list of tables" in text:
            return idx
        if idx > 10:
            raise TableListNotFoundError


# ocr logic
def get_english_table_list(images, start_page):
    """Returns a list of extracted text from the table list.

    NOTE: This method is used specifically for the two-column
    format of Korean Statistical Yearbooks where the right side is English.
    For other uses of this program, the exact method for detecting tables from the
    list of tables should be altered according to the use.

    Looks at pages starting from the table list start page (determined beforehand),
    using ocr to extract text from the right half of the page. When Korean is detected,
    it assumes that the first page of the body of the document has been reached (since tables
    are in both Korean and English on a given page) and ends the list there. This is taken
    to be the entirety of the table list.

    Args:
        images: a list of images converted from the first 25 pages of the pdf
        to be used for ocr extraction.
        start_page: the starting page for the table list determined previously
        by get_table_list_start_page().

    Returns:
        text_list: a list of extracted text from the english column of the table list.

    Example Usage:
        text_list = get_english_text_list(images, start_page)
    """
    text_list = []
    near_end = False
    for idx, image in enumerate(images):
        if idx < start_page:
            continue
        text = ocr_right_column(image)
        if near_end and "XX" not in text:
            # print(f"[DEBUG] TableList ends at idx={idx}, text={text[:60]!r}")
            # append one more page for safety
            text_list.append(text)
            break
        text_list.append(text)
        if "XX" in text:
            near_end = True
    return text_list


def ocr_right_column(image):
    """uses ocr to extract text from the right half of the given image.
    """
    width, height = image.size
    right_col = image.crop((width // 2, 0, width, height))
    text = pytesseract.image_to_string(right_col, lang='kor+eng')
    return text


def get_page_nums_near_query(text, query):
    """
    
    matches the first number after query that occurs
    at the END OF A LINE. it may not be the exact page number of the query table,
    but this is why we search a range around the written number.

    If fails, get previous one before query.
    """
    # prefer finding a number after the query (may grab same line)
    idx = text.lower().find(query.lower())
    after_query = text[idx + len(query):]
    num = re.search(r'(\d+)\s*$', after_query, re.MULTILINE)
    if num:
        return int(num.group(0))
    # 
    before_query = text[:idx]
    matches = re.findall(r'(\d+)\s*$', before_query, re.MULTILINE)
    if matches:
        return int(matches[-1])
    return None


# tools.text_pdfs.py ------------------------------
"""Functions for text pdf handling.

Allows for checking whether a pdf contains text to decide whether
to search via this text handler (get_page_nums_from_query_text) or via ocr.
"""
from pypdf import PdfReader


def pdf_has_text(pdf_path, max_pages=30):
    """Check if pdf has extractable text.

    Returns true if pdf contains text.
    Signals use for ocr to search document.

    Args:
        pdf_path: path to pdf.
        max_pages: max num of pages to scan to improve efficiency.

    Returns:
        Boolean whether pdf has text.

    Example usage:
        if not is_text_file(pdf_path):
            do_some_ocr_functions()
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages[:max_pages]:
        page_text = page.extract_text()
        if page_text:
            text += page_text
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