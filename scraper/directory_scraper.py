"""Scan directories containing yearbook pdfs.

Note: assumes pdfs begin with their year for sorting.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfWriter

from scraper.file_scraper import main as scrape


def main(query):
    load_dotenv()
    INPUT_DIR = Path(os.getenv('INPUT_DIR_PATH'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR_PATH'))
    merged_writer = PdfWriter()

    for pdf in sorted(os.listdir(INPUT_DIR)):
        pdf_path = INPUT_DIR / pdf
        output_writer = scrape(pdf_path, query)
        for page in output_writer.pages:
            merged_writer.add_page(page)
    
    output_path = OUTPUT_DIR / f"scraped-{INPUT_DIR.name}.pdf"
    with open(output_path, "wb") as f:
        merged_writer.write(f)

if __name__ == "__main__":
    main()