import pymongo
from pymongo import MongoClient


#initializing the database
cluster = MongoClient("mongodb+srv://wasiq:1234@cluster0.slwju.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster['discord']
collection_userInfo = db['userInfo']
collection_userBets = db['userBets']
collection_custom_events = db['custom_events']