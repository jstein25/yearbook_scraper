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
            print(f"[DEBUG] query found in text: {text}")
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