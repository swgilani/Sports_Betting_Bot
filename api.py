import requests
from datetime import datetime, timezone,timedelta
import pytz
from tzlocal import get_localzone # $ pip install tzlocal
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
#from db import *

load_dotenv()
oddsKey = str(os.getenv("oddsKey"))
MONGO_CONNECT = str(os.getenv("MONGO_CONNECT"))

#initializing the database
cluster = MongoClient(MONGO_CONNECT)
db = cluster['discord']
collection_userInfo = db['userInfo']
collection_userBets = db['userBets']
collection_custom_events = db['custom_events']


def getSports():
    response = requests.get("https://api.the-odds-api.com/v3/sports/?apiKey="+ oddsKey)
    response_data = response.json()  

    sports = []
    sports.append({"name": "CUSTOM EVENTS", "key": "custom"})

    for data in response_data["data"]:

        if data["key"].startswith('soccer'):
            if data['key'] == "soccer_epl" or data['key'] == "soccer_england_league1" or data['key'] == "soccer_uefa_european_championship":
                sports.append({"name": data['details'], "key": data['key']})
        else:
            sports.append({"name": data['details'], "key": data['key']})

    
    return sports


def getEvents(key):

        if key.lower() == "custom":

            events = []

            data = collection_custom_events.find({})

            if not data:
                return events

            for event in data:
                events.append({"id": event['_id'],"teams": event['teams'], "odds": event['odds'], "commence_time": event['commence_time'], "sport_nice": event['sport_nice']})

            return events 


        response = requests.get("https://api.the-odds-api.com/v3/odds/?apiKey=" +oddsKey + "&sport="+key+"&region=us&mkt=h2h&dateFormat=unix&oddsFormat=american")
        response_data = response.json()

        events = []

        #teams, h2h, commence time, id
        count = 0
        if response_data["success"] == True:
            for event in response_data["data"]:

            
                dateTime = switch_timezone(int(event["commence_time"]))

                if count <= 15:
                    events.append({"id": event['id'],"teams": event['teams'], "odds": event['sites'][0]['odds'], "commence_time": dateTime, "sport_nice": event['sport_nice']})
                    count = count+1
                else:
                    return events

        elif response_data["success"] == False:
            return response_data
            
        return events


def getEventInformation(key, eventID):

    if key.lower() == "custom":  
        response_data = {"data": [collection_custom_events.find_one({"_id": eventID})]}


    else:
        response = requests.get("https://api.the-odds-api.com/v3/odds/?apiKey=" +oddsKey +"&sport="+key+"&region=us&mkt=h2h&dateFormat=unix&oddsFormat=american")
        response_data = response.json()

    
    event_information_temp = {}
    for event in response_data['data']:

        if key.lower() == "custom":
            api_event_id_substring = event['_id']
        else:
            api_event_id_substring = event['id'][0:3]

        if str(eventID) == api_event_id_substring:
            event_information_temp = event
        
    if event_information_temp:

        if key.lower() == "custom":
            event_information = {"id": event_information_temp['_id'],"sport_key": event_information_temp['sport_nice'],"teams": event_information_temp['teams'],
            "odds": event_information_temp['odds'],"commence_time": event_information_temp['commence_time']
            }
        else:
            dateTime = switch_timezone(int(event_information_temp['commence_time']))
            event_information = {"id": event_information_temp['id'],"sport_key": event_information_temp['sport_key'],"teams": event_information_temp['teams'],
            "odds": event_information_temp['sites'][0]['odds'],"commence_time": dateTime
            }   
        return event_information

    else:
        return "suckit"

#takes unix time and creates a datetime object in EST 
#assuming the unix time from the API is in est 
def switch_timezone(time):
    #print("Switch timezone type: ", type(time))
    ts = int(time)
    dateTime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    dt_object = datetime.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
    # print(type(dt_object))
    # print(dt_object)
    return dt_object


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


#convert american odds to decimal odds
def getDecimalOdds(americanOdds):
    if americanOdds >= 0:
        return (1 + (float(americanOdds)/100))
    else:
        return (1 - (100/float(americanOdds)))


def shorten_date(word, needle, n):
    start = word.find(needle)
    while start >= 0 and n > 1:
        start = word.find(needle, start+len(needle))
        n -= 1

    if word[start+2].isspace():
        return word[:start+2]

    return word[:start+1]
    

def shorten_date_index(word, needle, n):
    start = word.find(needle)
    while start >= 0 and n > 1:
        start = word.find(needle, start+len(needle))
        n -= 1
    return start



        













        



