from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def add_page_with_text(text):
    """Creates page with bold centered text and returns
    it to be added to a new PDF.

    Uses intermittent text_page.pdf in directory to 
    Args:
        text:
            String to be written to page.
    Returns:
        The created text page.
    """
    c = canvas.Canvas("text_page.pdf")
    width, height = A4
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2, height / 2, text)
    c.save()
    return PdfReader("text_page.pdf").pages[0]

def getPagesNear(page_num, pdf):
    """
    Args:
        page_num:
            Int for given page number,
    Returns:
        List of pages near page number.
    """
    pages = []
    page_num = page_num + 20
    for i in range(page_num - 10, page_num + 10):
        pages.append(pdf.pages[i])
    return pages