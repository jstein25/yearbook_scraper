from pathlib import Path

import pytest

from scraper.tools import tablelist_utils as tbl

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


class DummyImage:
    """A dummy image class to mock OCR results."""
    def __init__(self, text):
        self.text = text
        self.size = (1000, 1000)

    def crop(self, box):
        return self
    
    # Simulate pytesseract.image_to_string
    def __str__(self):
        return self.text


def dummy_image_to_string(image, lang=None):
    return image.text


def test_ocr_right_column(monkeypatch):
    img = DummyImage("Right column English text")
    monkeypatch.setattr("pytesseract.image_to_string", dummy_image_to_string)
    result = tbl.ocr_right_column(img)
    assert result == "Right column English text"


def test_get_table_list_start_page(monkeypatch):
    images = [DummyImage("not here")] * 5 + [DummyImage("List of Tables")] + [DummyImage("other")]
    monkeypatch.setattr("pytesseract.image_to_string", dummy_image_to_string)
    idx = tbl.get_table_list_start_page(images)
    assert idx == 5


def test_get_table_list_start_page_not_found(monkeypatch):
    images = [DummyImage("just some non-table text here")] * 12
    monkeypatch.setattr("pytesseract.image_to_string", dummy_image_to_string)
    with pytest.raises(tbl.TableListNotFoundError):
        tbl.get_table_list_start_page(images)


def test_get_english_table_list_stops_after_xx(monkeypatch):
    # First 2 pages are before table list, next 2 are English, then a page with XX, then a non-XX page
    images = [
        DummyImage("skip"), DummyImage("skip"),
        DummyImage("English Table 1"),           # idx=2
        DummyImage("English Table 2"),           # idx=3
        DummyImage("XX Table List End Marker"),  # idx=4, triggers near_end
        DummyImage("Body page"),         # idx=5, should stop here
        DummyImage("Should not be included"),    # idx=6
    ]
    monkeypatch.setattr(tbl, "ocr_right_column", lambda img: img.text)
    result = tbl.get_english_table_list(images, start_page=2)
    # Should include up to and including the XX page, but not after
    assert result == [
        "English Table 1",
        "English Table 2",
        "XX Table List End Marker"
    ]


def test_search_table_list_found_full_page(monkeypatch):
    # Simulate a table list as a single full-page string
    table_list_text = (
        "Table 1.1 Population ............ 23\n"
        "Table 2.2 GDP ............ 2020\n"
        "Table 3.3 Unemployment ............ 45\n"
    )
    monkeypatch.setattr(tbl, "extract_first_n_images", lambda pdf, n: [DummyImage(table_list_text)])
    monkeypatch.setattr(tbl, "get_table_list_start_page", lambda images: 0)
    monkeypatch.setattr(tbl, "get_english_table_list", lambda images, start: [table_list_text])
    monkeypatch.setattr(tbl, "get_first_num_after_query", lambda text, query: 2020 if query == "GDP" else 23 if query == "Population" else 45 if query == "Unemployment" else None)
    result = tbl.search_table_list("dummy.pdf", "GDP")
    assert result is not None  # or assert result == expected_page_number