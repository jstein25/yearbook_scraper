"""Unit tests for ocr functionality."""

import pytest
from pathlib import Path
from scraper.tools import ocr as ocr

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.mark.parametrize(
    "pdf,query,expected",
    [
        (RESOURCE_ROOT / "test.pdf", "dog", [0]),
        (RESOURCE_ROOT / "test.pdf", "cat", []),
    ],
)
def test_ocr_single_page_search(pdf, query, expected):
    page_nums = ocr.get_page_nums_from_query_ocr(pdf, query, 0, 1)
    assert page_nums == expected


@pytest.mark.parametrize(
    "query,expected",
    [
        ("this", [0, 1, 2]),
        ("hello", []),
    ],
)
def test_ocr_multi_page_search(scanned_pdf, query, expected):
    page_nums = ocr.get_page_nums_from_query_ocr(scanned_pdf, query, 0, 3)
    assert page_nums == expected