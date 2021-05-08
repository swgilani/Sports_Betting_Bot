import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from User import User
import pymongo
from pymongo import MongoClient
from api import *


load_dotenv()
TOKEN = os.getenv("TOKEN")


#initializing the database
cluster = MongoClient("mongodb+srv://wasiq:1234@cluster0.slwju.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster['discord']
collection = db['userInfo']



#initializing the prefix for the commands that the bot will use
client = commands.Bot(command_prefix=";")

sad_words=['sad','depressed','unhappy','angry','mad','miserable','depressed','depressing']
starter_encouragements=['Cheer up!','Hang in there.','You are a great person!']


#Prints "bot is ready" when running the python file
@client.event  
async def on_ready():
    print('Bot is ready')

#on message events for all the incoming messages in the discord server
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if any(word in message.content for word in sad_words):
        await message.channel.send(random.choice(starter_encouragements))

    if "reaching" in message.content or "hopping on" in message.content or "coming" in message.content :
        await message.channel.send(":billed_cap:")

    await client.process_commands(message)


#create an account with 1000$ balance
@client.command()
async def register(ctx):
    
    user = User(ctx.author.id,1000)

    try:
        collection.insert_one({"_id":user.getId(),"balance": user.getBalance()})
        await ctx.send("UserID:"+str(user.getId())+" Balance:"+str(user.getBalance()))
    except:
        await ctx.send(ctx.author.mention+", your account is already registered.")


@client.command()
async def beg(ctx):
    author = ctx.author.id
    
    if collection.find({"_id": author}):
        user = collection.find_one({"_id": author})
        balance = user['balance']
        balance = balance+5
        collection.update_one({"_id":author}, {"$set": {"balance": balance}})
        await ctx.send("Someone gave you a few bucks! You now have $"+str(balance))

    else:
        await ctx.send("You must register before begging. Please type the -register command")


@client.command()
async def sports(ctx):
    

    sports = getSports()
    output = ""

    for sport in sports:
        output = output+f"{sport['name']} - {sport['key']} \n"
    
    await ctx.send("View all the events for a sport with -events <sport_id>\n"+output)


@client.command()
async def events(ctx, key):

    print (getEvents(key))
    try:
        events = getEvents(key)
        output = ""

        for event in events:
            output = output+f"{event['id']} - {event['teams']} - {event['odds']} - {event['commence_time']} \n"
    
        await ctx.send(output)


    except Exception as e:

        await ctx.send(e)


#bet <amount> <team> <event_id> <key>
#bet 500 

@client.command()
async def bet(ctx, amount, team, event_id, key ):




    
    return
    
    


    

    


@client.command()
async def test(ctx):
    await ctx.send(ctx.author.id)

    
    
    

    

client.run(TOKEN)