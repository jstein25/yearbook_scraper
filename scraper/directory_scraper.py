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