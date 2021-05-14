import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random, string
from User import User
import pymongo
from pymongo import MongoClient
from api import *
from datetime import datetime
from image_scraper import *
#from db import *
from datetime import datetime, timezone,timedelta
Test syntax error


load_dotenv()
TOKEN = os.getenv("TOKEN")
MONGO_CONNECT = str(os.getenv("MONGO_CONNECT"))


#initializing the database
cluster = MongoClient(MONGO_CONNECT)
db = cluster['discord']
collection_userInfo = db['userInfo']
collection_userBets = db['userBets']
collection_custom_events = db['custom_events']




#initializing the prefix for the commands that the bot will use
client = commands.Bot(command_prefix=";",help_command=None)

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
        embed=discord.Embed( description=random.choice(starter_encouragements), color=discord.Color.blue())
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
    output_name = ""
    output_key = ""

    for sport in sports:
        output = output+f"{sport['name']} - {sport['key']} \n"
        output_name = output_name+f"{sport['name']} \n"
        output_key = output_key+f"{sport['key']} \n"
        


    embed=discord.Embed(title="Sports Betting", description="The list of current sports that you can bet on.",color=0x001cf0)
    embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQj84vwyPYMqE6DB-4BBK1LBBrfnpEoR--MOw&usqp=CAU")
    embed.add_field(name='Sport', value=output_name, inline=True)
    embed.add_field(name="Sport ID", value=output_key, inline=True)
    embed.set_footer(text="Please use the ;event <ID> command to view the current events for the sports.")
    await ctx.send(embed=embed)
    


@client.command()
async def events(ctx, key):

# try:
    events = getEvents(key)
    output = ""
    output_id = ""
    output_teams = ""
    output_odds_and_time = ""
    
    for event in events:
        datetime_object = datetime.strptime(event['commence_time'], '%Y-%m-%d %H:%M:%S')
        datetime_object = datetime_object.date()
        output = output+f"{event['id'][0:3]} | {event['teams'][0]} vs. {event['teams'][1]} | {event['odds']['h2h'][0]} to {event['odds']['h2h'][1]} | {datetime_object} \n"
        output_id = output_id+f"{event['id'][0:3]} \n"
        output_teams = output_teams+f"{event['teams'][0]} vs. {event['teams'][1]} \n"
        output_odds_and_time = output_odds_and_time+f"{event['odds']['h2h'][0]} to {event['odds']['h2h'][1]} \n"
        name = event['sport_nice']
    embed=discord.Embed(title=f"Upcoming events for {name}", description="Event information for upcoming events",color=0x001cf0)
    embed.add_field(name="Event ID", value=output_id, inline=True)
    embed.add_field(name="Teams (1 & 2)", value=output_teams, inline=True)
    embed.add_field(name="Odds", value=output_odds_and_time, inline=True)
    embed.set_footer(text="Please use the ;bet < amount > <team number> <event ID> <sport ID> place a bet.")
    await ctx.send(embed=embed)

# except Exception as e:
#   await ctx.send("The key you inputting was incorrect or missing. Please type ;help for more information")


@events.error
async def on_command_error(ctx, error):
    await ctx.send("Please use the command as follows: ;events <sport key>. You can get the sports key from typing the ;sports command.")

@client.command()
async def bet(ctx,bet,team, eventID,key):
   

    author = ctx.author.id
    if collection_userInfo.find_one({"_id": author}):
        user = collection_userInfo.find_one({'_id': author})
        userBalance = user['balance']
        
        #getting event info 
        if key.lower() == "custom":  
            event_info = collection_custom_events.find_one({"_id": eventID})
        else: 
            event_info = getEventInformation(key, eventID)

        print(event_info)
        teams = event_info['teams']
        teamsvs_string = f"{teams[0]} vs {teams[1]}"
        odds = event_info['odds']['h2h']
        commence_time = event_info['commence_time']
        present = datetime.now()
        start = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')

        if ((int(userBalance) < int(bet)) or (present > start) or (int(team) != 1 and int(team) != 2) ):
            await ctx.send("cant bet")
        
        else:
            
            collection_userInfo.update_one({"_id":author}, {"$set": {"balance": int(userBalance) - int(bet)}})
            post = {"user_id": author, "team": [teams[int(team)-1] , int(team)], "amount": int(bet), "event_id": eventID, "odds": odds, "key": key, "event_teams": teams}
            collection_userBets.insert_one(post)
            
            embed=discord.Embed(title="Your bet was successfully placed!", description=f"{ctx.author.mention}, you placed ${bet} on {teams[int(team)-1]}. Good luck!", color=0x44ff00)
            embed.set_footer(text="Enter the command ;mybets to view your active bets")
            #embed.set_thumbnail(url=str(imageSearch(teamsvs_string)))
            embed.set_image(url=str(imageSearch(teamsvs_string)))
            await ctx.send(embed=embed)


            # await ctx.send(f"Your bet has been placed on {teams[int(team)-1]} for ${bet}")  


            #print(odds)
    
    else: 
        await ctx.send("You need to register your account before betting. Please type ;help for more information.")

    

@bet.error
async def on_command_error(ctx, error):
    await ctx.send("Please make sure you've entered your bet correctly (;bet <bet amount> <team #> <event id> <sport id>). Type ;help for more information.")



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





        win_counter=0
        loss_counter=0
        result_record = ""
        event_record = ""
        payout_record = ""
        net_profit = 0

        if not record:
            embed=discord.Embed(title="Account Summary", description=f"{ctx.author.mention}'s W/L Record: 0-0", color=0x001df5)
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.add_field(name="Res.", value="X", inline=True)
            embed.add_field(name="Event", value="X", inline=True)
            embed.add_field(name="Payout", value="X", inline=True)
            embed.add_field(name="Account Balance", value=f"${roundedBalance}", inline=True)
            embed.add_field(name="Net Profit", value=net_profit, inline=True)
            embed.set_footer(text="Use ;help for more information about all the commands.")
            await ctx.send(embed=embed)

        else:


    
            for item in record:
                net_profit = net_profit + item[2]
                roundedPayout = round(item[2],2)
                if item[0] == "Win":
                    win_counter = win_counter+1
                elif item[0] == "Loss":
                    loss_counter = loss_counter+1
                result_record = result_record+f"{item[0]} \n"
                event_record = event_record+f"{item[4][0]} vs. {item[4][1]} \n"
                payout_record = payout_record+f"{roundedPayout} ($)\n"

            net_profit = round(net_profit,2)
            if int(net_profit) > 0:
                net_profit = f"+{net_profit} ($)"
            else:
                net_profit = f"{net_profit} ($)"
        
            embed=discord.Embed(title="Account Summary", description=f"{ctx.author.mention}'s W/L Record: {win_counter}-{loss_counter}", color=0x001df5)
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.add_field(name="Res.", value=result_record, inline=True)
            embed.add_field(name="Event", value=event_record, inline=True)
            embed.add_field(name="Payout", value=payout_record, inline=True)
            embed.add_field(name="Account Balance", value=f"${roundedBalance}", inline=True)
            embed.add_field(name="Net Profit", value=net_profit, inline=True)
            embed.set_footer(text="Use ;help for more information about all the commands.")
            await ctx.send(embed=embed)


    else: 
        await ctx.send(f"You need to register your account before betting. Please type ;help for more information.")

@client.command(pass_context=True)
@commands.has_any_role("Papa")
async def payout(ctx,eventID,winner):
    #eventInfo = getEventInformation(key, eventID)
    #teams = {A,B}
    conquisatadors = []
    key = ""
    

    if int(winner) == 1 or int(winner) == 2:
        bets = collection_userBets.find({"event_id": eventID})
        for bet in bets:
            user_id = bet['user_id']
            user = collection_userInfo.find_one({'_id': user_id})
            key = bet['key']

            if int(winner) == int(bet['team'][1]):

                odds = bet['odds'][int(winner)-1]

                #print(user)
                
                #payout logic 
               
                payoutMultiplier = getDecimalOdds(odds)
                newBalance = (int(bet['amount']) * payoutMultiplier) + user['balance']
                earnings = newBalance - (int(user['balance']) + int(bet['amount']))
                collection_userInfo.update_one({"_id": user_id}, {"$set": {"balance": newBalance}})
                conquisatadors.append(user_id)

                #post = {"result": "Win","event_id": eventID,"key": bet['key'], "earnings": earnings}

                user_record_temp = user['record']

                new_record = ["Win",eventID,earnings,bet['key'], bet['event_teams']]
                user_record_temp.append(new_record)
                

                collection_userInfo.update_one({"_id":user_id},{"$set": {"record":user_record_temp}})

            else:
                earnings = -1 * int(bet['amount'])
                user_record_temp = user['record']
                new_record = ["Loss",eventID,earnings,bet['key'], bet['event_teams']]
                user_record_temp.append(new_record)
                collection_userInfo.update_one({"_id":user_id},{"$set": {"record":user_record_temp}})


        if key.lower() == "custom":
            collection_custom_events.delete_one({"_id": eventID})

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

@payout.error
async def on_command_error(ctx, error):
    await ctx.send("NOTE: THIS IS AN ADMIN COMMAND. Please use ;payout <event id> <winner> to use this command")



@client.command()
async def mybets(ctx):
    author = ctx.author.id
    bets = collection_userBets.find({"user_id": author})
    output = []
    for bet in bets:        
        output.append({"teams": bet['event_teams'], "amount": bet['amount'], "event_id":bet['event_id'], "user_team": bet['team'][0]})


    if not output:
        await ctx.send("You currently have no active bets.")
        #a random comment
        #a random commment 2
    else:
        bet_indices = ""
        bet_amount = ""
        bet_event = ""
        for i in range(len(output)):
            bet_indices = bet_indices+f"{i+1} \n"
            bet_amount = bet_amount+f"{output[i]['user_team']} (${output[i]['amount']}) \n"
            bet_event = bet_event+f"{output[i]['teams'][0]} vs. {output[i]['teams'][1]} \n "

        embed=discord.Embed(title="Current bets", description=f"{ctx.author.mention}, these are all your current bets", color=0x2309ec)
        embed.add_field(name="#", value=bet_indices, inline=True)
        embed.add_field(name="Bet/Amount", value=bet_amount, inline=True)
        embed.add_field(name="Event", value=bet_event, inline=True)
        embed.set_footer(text="Enter ;deletebet <bet #> if you would wish to delete a bet. Type ;help for more information.")
        await ctx.send(embed=embed)



@client.command()
async def deletebet(ctx, index):
    delete = {}
    author = ctx.author.id
    bets = collection_userBets.find({"user_id": author})
    counter = 0 
    for bet in bets:
        if counter == int(index)-1:
            delete = bet
        counter=counter+1

    if not delete:
        await ctx.send("Could not find the bet in your record. Please try again.")

    else:
        print(delete)
        event_info = getEventInformation(delete['key'], delete['event_id'])
        print (event_info)
        commence_time = event_info['commence_time']
        present = datetime.now()
        start = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')
        print(start)
        diff = start - present
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        ##################################################################################
        #NEED TO FINISH CODE. ONLY ALLOWED TO DELTETE IF EVENT IS A SPECIFIC TIME AWAY. 
        #CANCELLING A BET ALSO HAS A PENALTY
        if hours <= 24:
            embed=discord.Embed(title="Denied", description=f"{ctx.author.mention}, This bet could not be deleted.", color=0xf50000)
            embed.set_thumbnail(url="https://lh3.googleusercontent.com/proxy/jDyt5HBuNMwTe1ugtGAEKsaJn9n4XmmEvxydQcLtBp1Km4rT5XgcAyOTGIq31DPbbH0sgafWwHohuaxXNtpUPlcf7CmXTLNQVky3PeJM1-v43j-k9Cln2O1YMh1h5HBMWeP1brKZ5rwVEj2zcQFxfjS4xKn5Ys8")
            embed.add_field(name="Reason", value=f"A bet cannot be deleted if event is less than 24 hours away. The specified event is {hours} hour away.", inline=True)
            await ctx.send(embed=embed)

        else:
            collection_userBets.delete_one(delete)
            embed=discord.Embed(title="Bet Deleted", description=f"{ctx.author.mention}, the specified bet has been removed.", color=0x2309ec)
            embed.set_footer(text="NOTE: You can NOT delete a bet if the event starts in less than 24 hours.")
            await ctx.send(embed=embed)

# @deletebet.error
# async def on_command_error(ctx, error):
#     await ctx.send("Please input a valid bet index to delete.")




@client.command()
async def help(ctx):
    embed=discord.Embed(title="Help Guide for Me!", description="This guide provides with all the commands users and admins can perform and what they do.", color=0x001df5)
    embed.add_field(name=";register", value="You must be registered first to make any bets. Once you register, you automatically get $1000 for betting. ", inline=False)
    embed.add_field(name=";sports", value="This command will give the user a list of sports that they can bet on and their sport ID. Users will use the sport ID to find events for that specific sport, as well as making bets.", inline=False)
    embed.add_field(name=";events <sport id>", value="This command takes in one argument: <sport id>. This id can be found by using the ;sports command. Users can use this command to find out all the upcoming events for a specific sport for betting purposes. Users will be given an event id for all the events. They will use this id to place their bets for those events.", inline=False)
    embed.add_field(name=";bet <bet amount> <team #> <event id> <sport id>", value="This command takes in four arguments. The first argument <bet> is the amount of money users want to bet. The second argument <team #> is the team they would like to bet on. Valid entries for team are either 1 or 2. Third argument is the event ID which users can find using the ;events <sport id> command. And finally, the last argument is the <sport id>, which users can find using the ;sports command. All of these together will allow users to bet on their team of their liking.", inline=False)
    embed.add_field(name=";mybets", value="Shows your current ongoing bets", inline=False)
    embed.add_field(name=";deletebets <bet #> ", value="Delete any of your ongoing bets using your bet # obtained from ;mybets. NOTE: You are unable to delete bets for events that start in less than 24 hours.", inline=False)
    embed.add_field(name=";help", value="self explanatory ", inline=False)
    embed.set_footer(text="Developed by Wowsixk & Fry")
    await ctx.send(embed=embed)


#create a new event under the FEATURED EVENTS sport
@client.command(pass_context=True)
@commands.has_any_role("Papa")
async def addEvent(ctx, team1,team2, odds1, odds2):

    #generate random 3 char id 
  
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    date1 = '22-May-2050 19:54:36'

    teams = [team1,team2]
    odds = {"h2h":[int(odds1),int(odds2)]}
    timing = datetime.strptime(date1,'%d-%b-%Y %X')

    collection_custom_events.insert_one({"_id": x.lower(),"teams": teams, "odds": odds, "commence_time": str(timing), "sport_nice": "custom"})
    #collection_userBets.insert_one({"_id": eventID})
    await ctx.send("New Event Created")

    
    

