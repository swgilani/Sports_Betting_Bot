import sys
sys.path.insert(0, '/')
import image_scraper
#from .. import image_scraper
import pytest

def test_unage_scraper_with_no_input():
    with pytest.raises(Exception) as e_info:
        events = image_scraper.imageSearch() #Successfully raises exception when no arguments provided.