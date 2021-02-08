import pytest
from main import *

def test_extract_number_from_page():
    testpage="/path/to/dir/page_1.jpg"
    number = 1
    ret_number = extract_number_from_page(testpage)
    assert number == ret_number

def test_get_reader_url():
    url = "https://issuu.com/ducatiomaha/docs/ducatiomaha_2015_diavel?e=1222863/13414409"
    reader_url = "https://reader3.isu.pub/ducatiomaha/ducatiomaha_2015_diavel/reader3_4.json"
    assert get_reader_url(url) == reader_url