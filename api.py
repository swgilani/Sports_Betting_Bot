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

            
            ts = int(event["commence_time"])
            dateTime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            if count <= 10:
                events.append({"id": event['id'],"teams": event['teams'], "odds": event['sites'][0]['odds'], "commence_time": dateTime})
                count = count+1
            else:
                return events
            
        return events

        













        



