"""

"""

import os
from dotenv import load_dotenv
from pypdf import PdfReader, PdfWriter
from tools.tables import get_tables_from_file

load_dotenv()
DIR_PATH = os.getenv('DIR_PATH')

def export_pdf_to_output():
    output_pdf = PdfWriter()

    for file_name in sorted(os.listdir(DIR_PATH)):
        pdf_path = os.path.join(DIR_PATH, file_name)
        
# TODO: make this so it will scan files based on user input...