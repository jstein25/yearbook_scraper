"""Unit tests for text pdfs: text detection and search."""

from pathlib import Path

import pytest

from scraper.tools import text_pdfs as text


TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def test_pdf_with_text_has_text(pdf_with_text):
    assert text.pdf_has_text(pdf_with_text)


def test_scanned_pdf_has_no_text(scanned_pdf):
    assert not text.pdf_has_text(scanned_pdf)


def test_yearbook_is_scanned():
    yearbook_path = RESOURCE_ROOT / "1966-education-yearbook.pdf"
    assert not text.pdf_has_text(yearbook_path)


@pytest.mark.parametrize(
    "query,expected",
    [
        ("Hello World", [0]),
        ("Hello Again, World", [1]),
        ("World", [0, 1]),
        ("Hello", [0, 1, 2]),
        ("What?!?", []),
    ],
)
def test_search_returns_expected_pages(pdf_with_text, query, expected):
    page_nums = text.get_page_nums_from_query_text(pdf_with_text, query)
    assert page_nums == expected