import requests
from datetime import datetime



def getSports():
    response = requests.get("https://api.the-odds-api.com/v3/sports/?apiKey=210e8d4049b78eae5a7e0ab14ba177ca")
    response_data = response.json()  

    sports = []

    for data in response_data["data"]:

        if data["key"] == "basketball_nba" or data["key"] == "mma_mixed_martial_arts" or data["key"] == "soccer_epl":
        
            sports.append({"name": data['details'], "key": data['key']})

    return sports


def getEvents(key):
        response = requests.get("https://api.the-odds-api.com/v3/odds/?apiKey=210e8d4049b78eae5a7e0ab14ba177ca&sport="+key+"&region=us&mkt=h2h&dateFormat=unix&oddsFormat=american")
        response_data = response.json()

        events = []

        #teams, h2h, commence time, id
        count = 0
        for event in response_data["data"]:

        
            dateTime = switch_timezone(event["commence_time"])

            if count <= 10:
                events.append({"id": event['id'],"teams": event['teams'], "odds": event['sites'][0]['odds'], "commence_time": dateTime})
                count = count+1
            else:
                return events
            
        return events


def getEventInformation(key, eventID):

    response = requests.get("https://api.the-odds-api.com/v3/odds/?apiKey=210e8d4049b78eae5a7e0ab14ba177ca&sport="+key+"&region=us&mkt=h2h&dateFormat=unix&oddsFormat=american")
    response_data = response.json()

    
    event_information_temp = {}
    for event in response_data['data']:

        api_event_id_substring = event['id'][0:3]
       
        if str(eventID) == api_event_id_substring:
            event_information_temp = event
        
    if event_information_temp:
        
        dateTime = switch_timezone(event_information_temp['commence_time'])
        event_information = {"id": event_information_temp['id'],"sport_key": event_information_temp['sport_key'],"teams": event_information_temp['teams'],
        "odds": event_information_temp['sites'][0]['odds'],"commence_time": dateTime
        }   
        return event_information

    else:
        return "null"


def switch_timezone(time):
    ts = int(time)
    dateTime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return dateTime



#convert american odds to decimal odds
def getDecimalOdds(americanOdds):
    if americanOdds >= 0:
        return (1 + (float(americanOdds)/100))
    else:
        return (1 - (100/float(americanOdds)))



    

        













        



