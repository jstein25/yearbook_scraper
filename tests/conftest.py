from pathlib import Path

import uuid
from fpdf import FPDF
import pytest
from pypdf import PdfReader, PdfWriter

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.fixture()
def pdf_file_path(tmp_path):
    return tmp_path / f"{uuid.uuid4()}.pdf"


@pytest.fixture()
def pdf_with_text(pdf_file_path):
    """Creates multi-page pdf with text on each page.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.cell(0, 10, "Hello World")
    pdf.add_page()
    pdf.cell(0, 10, "Hello Again, World")
    pdf.add_page()
    pdf.cell(0, 10, "Hello for the third time")
    pdf.output(pdf_file_path)
    return pdf_file_path


# scanned pdfs
@pytest.fixture()
def scanned_pdf(pdf_file_path):
    """Creates 3 page pdf from test.pdf in resources.
    """
    reader = PdfReader(RESOURCE_ROOT / "test.pdf")
    writer = PdfWriter()
    for i in range(0, 3):
        writer.add_page(reader.pages[0])
    with open(pdf_file_path, "wb") as f:
        writer.write(f)
    return pdf_file_path