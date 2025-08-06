"""Unit tests for page getting."""

from pypdf import PdfReader
import pytest
from scraper.tools import pdf_page_utils as utils


@pytest.mark.parametrize(
    "indices,expected_texts",
    [
        ([0, 1, 2], None),  # Will compare full text below
        ([1, 1, 2], None),  # Will check for duplicates below
    ]
)
def test_get_pages_from_nums_texts(pdf_with_text, indices, expected_texts):
    reader = PdfReader(pdf_with_text)
    test_pages = utils.get_pages_from_nums(pdf_with_text, indices).pages
    if indices == [0, 1, 2]:
        test_text = "".join(page.extract_text() for page in test_pages)
        expected_text = "".join(page.extract_text() for page in reader.pages)
        assert test_text == expected_text
    elif indices == [1, 1, 2]:
        assert test_pages[0].extract_text() == reader.pages[1].extract_text()
        assert test_pages[1].extract_text() == reader.pages[1].extract_text()
        assert test_pages[2].extract_text() == reader.pages[2].extract_text()


def test_get_pages_from_nums_invalid_index(pdf_with_text):
    with pytest.raises((IndexError, ValueError)):
        utils.get_pages_from_nums(pdf_with_text, [10])