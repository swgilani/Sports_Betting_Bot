import requests
from datetime import datetime, timezone,timedelta
import pytz
from tzlocal import get_localzone # $ pip install tzlocal



def getSports():
    response = requests.get("https://api.the-odds-api.com/v3/sports/?apiKey=64fb42ebaba9cf4af62539cdf4dfdc8e")
    response_data = response.json()  

    sports = []

    for data in response_data["data"]:

        if data["key"].startswith('soccer'):
            if data['key'] == "soccer_efl_champ" or data['key'] == "soccer_efl_champ" or data['key'] == "soccer_epl" or data['key'] == "soccer_usa_mls" or data['key'] == "soccer_england_league1" or data['key'] == "soccer_england_league2":
                sports.append({"name": data['details'], "key": data['key']})
        else:
            sports.append({"name": data['details'], "key": data['key']})

    return sports


def getEvents(key):
        response = requests.get("https://api.the-odds-api.com/v3/odds/?apiKey=64fb42ebaba9cf4af62539cdf4dfdc8e&sport="+key+"&region=us&mkt=h2h&dateFormat=unix&oddsFormat=american")
        response_data = response.json()

        events = []

        #teams, h2h, commence time, id
        count = 0
        for event in response_data["data"]:

        
            dateTime = switch_timezone(event["commence_time"])

            if count <= 15:
                events.append({"id": event['id'],"teams": event['teams'], "odds": event['sites'][0]['odds'], "commence_time": dateTime, "sport_nice": event['sport_nice']})
                count = count+1
            else:
                return events
            
        return events


def getEventInformation(key, eventID):

    response = requests.get("https://api.the-odds-api.com/v3/odds/?apiKey=64fb42ebaba9cf4af62539cdf4dfdc8e&sport="+key+"&region=us&mkt=h2h&dateFormat=unix&oddsFormat=american")
    response_data = response.json()

    
    event_information_temp = {}
    for event in response_data['data']:

        api_event_id_substring = event['id'][0:3]
       
        if str(eventID) == api_event_id_substring:
            event_information_temp = event
        
    if event_information_temp:
        
        dateTime = switch_timezone(int(event_information_temp['commence_time']))
        event_information = {"id": event_information_temp['id'],"sport_key": event_information_temp['sport_key'],"teams": event_information_temp['teams'],
        "odds": event_information_temp['sites'][0]['odds'],"commence_time": dateTime
        }   
        return event_information

    else:
        return "null"


def switch_timezone(time):
    ts = int(time)
    dateTime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return dateTime

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)



#convert american odds to decimal odds
def getDecimalOdds(americanOdds):
    if americanOdds >= 0:
        return (1 + (float(americanOdds)/100))
    else:
        return (1 - (100/float(americanOdds)))



    

        













        



