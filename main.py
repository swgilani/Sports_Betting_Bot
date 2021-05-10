import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from User import User
import pymongo
from pymongo import MongoClient
from api import *
from datetime import datetime


load_dotenv()
TOKEN = os.getenv("TOKEN")


#initializing the database
cluster = MongoClient("mongodb+srv://wasiq:1234@cluster0.slwju.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster['discord']
collection_userInfo = db['userInfo']
collection_userBets = db['userBets']



#initializing the prefix for the commands that the bot will use
client = commands.Bot(command_prefix=";")

sad_words=['sad','depressed','unhappy','angry','mad','miserable','depressed','depressing']
starter_encouragements=['Cheer up!','Hang in there.','You are a great person!']


#Prints "bot is ready" when running the python file
@client.event  
async def on_ready():
    print('Bot is ready')



@client.event
async def on_command_error(ctx, error):
    await ctx.send("A parameter is missing. Please refer to ;help for more information")

#on message events for all the incoming messages in the discord server
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if any(word in message.content for word in sad_words):
        embed=discord.Embed(title="Hello", url="https://realdrewdata.medium.com/", description=random.choice(starter_encouragements), color=discord.Color.blue())
        await message.channel.send(embed = embed)

    if "reaching" in message.content or "hopping on" in message.content or "coming" in message.content :
        await message.channel.send(":billed_cap:")

    await client.process_commands(message)


#create an account with 1000$ balance
@client.command()
async def register(ctx):
    
    user = User(ctx.author.id,1000)

    try:
        collection_userInfo.insert_one({"_id":user.getId(),"balance": user.getBalance(), "record": []})
        await ctx.send("UserID:"+str(user.getId())+" Balance:"+str(user.getBalance()))
    except:
        await ctx.send(ctx.author.mention+", your account is already registered.")


@client.command()
async def beg(ctx):
    author = ctx.author.id
    
    if collection_userInfo.find({"_id": author}):
        user = collection_userInfo.find_one({"_id": author})
        balance = user['balance']
        balance = balance+5
        collection_userInfo.update_one({"_id":author}, {"$set": {"balance": balance}})
        await ctx.send("Someone gave you a few bucks! You now have $"+str(balance))

    else:
        await ctx.send("You must register before begging. Please type the -register command")


@client.command()
async def superbeg(ctx):
    author = ctx.author.id
    
    if collection_userInfo.find({"_id": author}):
        user = collection_userInfo.find_one({"_id": author})
        balance = user['balance']
        balance = balance+ 10000
        collection_userInfo.update_one({"_id":author}, {"$set": {"balance": balance}})
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

    await ctx.send("Event Id | Teams | Odds | Start Time" )

    try:
        events = getEvents(key)
        output = ""

        for event in events:
            output = output+f"{event['id'][0:3]} | {event['teams'][0]} vs. {event['teams'][1]} | {event['odds']['h2h'][0]} to {event['odds']['h2h'][1]} | {event['commence_time']} \n"
    
        await ctx.send(output)


    except Exception as e:

        await ctx.send(e)


#bet <amount> <team> <event_id> <key>
#bet 500 

@client.command()
async def bet(ctx,bet,team, eventID,key):
    #print(getEventInformation(key, eventID))

    
    #check funds
    try:
        author = ctx.author.id
        if collection_userInfo.find_one({"_id": author}):
            user = collection_userInfo.find_one({'_id': author})
            userBalance = user['balance']
            
            #getting event info 
            event_info = getEventInformation(key, eventID)
            teams = event_info['teams']
            odds = event_info['odds']['h2h']
            commence_time = event_info['commence_time']
            present = datetime.now()
            start = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')
           
            
            

            if ((int(userBalance) < int(bet)) or (present > start) or (int(team) != 1 and int(team) != 2) ):
                await ctx.send("cant bet")
            
            else:
                
                collection_userInfo.update_one({"_id":author}, {"$set": {"balance": int(userBalance) - int(bet)}})
                

                
                post = {"user_id": author, "team": [teams[int(team)-1] , int(team)], "amount": int(bet), "event_id": eventID, "odds": odds, "key": key}
                collection_userBets.insert_one(post)
                await ctx.send(f"Your bet has been placed on {teams[int(team)-1]} for ${bet}")  


                #print(odds)
        
        else: 
            await ctx.send("You need to register your account before betting. Please type ;help for more information.")

    except Exception as e:
        await ctx.send("Something went wrong. Please make sure you are using the correct format ;bet <bet> <team('1' or '2')> <eventID> <eventKey>. Please refer to ;help for more information")
        await ctx.send(e)

  
    #event_id, key, teams[], odds 
    #mongo.db.shows.insert_one(post1)




#view your account balance 
@client.command()
async def balance(ctx):
    author = ctx.author.id
    if collection_userInfo.find_one({"_id": author}):
        user = collection_userInfo.find_one({'_id': author})
        userBalance = user['balance']
        roundedBalance = round(userBalance,2)
        await ctx.send(f"Your balance is ${roundedBalance}")
    else: 
        await ctx.send(f"You need to register your account before betting. Please type ;help for more information.")

#view all your account info 
@client.command()
async def account(ctx):
    author = ctx.author.id

    if collection_userInfo.find_one({"_id": author}):
        user = collection_userInfo.find_one({'_id': author})
        userBalance = user['balance']
        roundedBalance = round(userBalance,2)
        record = user['record']

        print(record)
        #await ctx.send(f"Your balance is ${roundedBalance}")

        #output = roundedBalance + "\n"
        for log in record:
            await ctx.send(log)

        #     output = output+ (log[0] + "|" + log[2] + "|" + log[3] + "\n")
            
        #await ctx.send(f"Account Details: {output}")

    else: 
        await ctx.send(f"You need to register your account before betting. Please type ;help for more information.")

@client.command()
async def payout(ctx,eventID,winner):
    #eventInfo = getEventInformation(key, eventID)
    #teams = {A,B}
    conquisatadors = []
    

    if int(winner) == 1 or int(winner) == 2:
        bets = collection_userBets.find({"event_id": eventID})
        for bet in bets:
            user_id = bet['user_id']
            user = collection_userInfo.find_one({'_id': user_id})

            if int(winner) == int(bet['team'][1]):

                odds = bet['odds'][int(winner)-1]

                #print(user)
                
                #payout logic 
                print(f"odds{odds}")
                payoutMultiplier = getDecimalOdds(odds)
                print(f"multiplier {payoutMultiplier}")
                print(f"user balanec{user['balance']}")
                newBalance = (int(bet['amount']) * payoutMultiplier) + user['balance']

                

                print(f"newbalance{newBalance}")

                earnings = newBalance - (int(user['balance']) + int(bet['amount']))

                print(earnings)

                collection_userInfo.update_one({"_id": user_id}, {"$set": {"balance": newBalance}})
                conquisatadors.append(user_id)

                #post = {"result": "Win","event_id": eventID,"key": bet['key'], "earnings": earnings}

                user_record_temp = user['record']

                new_record = ["Win",eventID,earnings,bet['key']]
                user_record_temp.append(new_record)
                

                collection_userInfo.update_one({"_id":user_id},{"$set": {"record":user_record_temp}})

            else:
                earnings = -1 * int(bet['amount'])
                user_record_temp = user['record']
                new_record = ["Loss",eventID,earnings,bet['key']]
                user_record_temp.append(new_record)
                collection_userInfo.update_one({"_id":user_id},{"$set": {"record":user_record_temp}})

        collection_userBets.delete_many({"event_id": eventID})
        
        output = ""
        print(conquisatadors)
        for conquisatade in conquisatadors:
            output = output+"<@"+str(conquisatade)+"> "

        if conquisatadors:
            await ctx.send(f"Congrats to {output}")  
        else:
            await ctx.send(f"There were no winners. Major L to all.")  
        
            
            
        
        

    else:
        await ctx.send("Please select 1 or 2 for the winner.")







    


client.run(TOKEN)