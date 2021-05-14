import sys
sys.path.insert(0, '/')
import api
#from .. import api
import pytest

def test_len_getSports_api():
    assert len(api.getSports()) > 0

# def test_getEvents_with_wrongKey():
#     events = api.getEvents("invalid")
#     assert events['success'] == False

def test_getEvents_with_noKey():
    with pytest.raises(Exception) as e_info:
        events = api.getEvents() #Successfully raises exception when no arguments provided.
        
@pytest.mark.parametrize("a,b", [(0,1),(10,1.1),(20,1.2),(50,1.5),(500,6),(-100,2), (-500,1.2),(-1000,1.1)])
def test_oddsConversion_correct(a,b):
    assert api.getDecimalOdds(a) == b

def test_oddsConversion_false():
    assert api.getDecimalOdds(300) != 300

#def test_switch_timezone():
    #assert api.switch_timezone(1620868228) == "2021-05-12 21:10:28"

def test_switch_timezone_noInput():
    with pytest.raises(Exception) as e_info:
        events = api.switch_timezone() #Successfully raises exception when no arguments provided.














