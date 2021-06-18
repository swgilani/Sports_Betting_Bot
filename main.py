import discord
from discord.utils import get
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

#rexy greetings
greetings_rexy = ["Greetings!", "Hello!", "Hey,", "Rexy here,", "Whats poppin!", "Hey everyone,","Hi everyone,", "Hey guys!", "Hi people,","Sup y'all,"]


#rexy greetings

#ben greetings
greetings_ben = ["Greetings!", "Hello!", "Hey,", "Benjamin here,", "Whats poppin!", "Hey everyone,","Hi everyone,", "Hey guys!", "Hi people,","Sup y'all,"]
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
    
    default_bal = 1000.00
    user = User(ctx.author.id,default_bal)
    user_name = ctx.author.mention

    try:

        collection_userInfo.insert_one({"_id":user.getId(),"balance": user.getBalance(), "record": []})
        embed=discord.Embed(title="Account Created", description=f"{user_name}Your account was successfully created", color=0x11ff00)
        embed.add_field(name=";account", value="Please use the above command to view your account information", inline=False)
        await ctx.send(embed=embed) 
    except:
        embed=discord.Embed(title="Error creating your account", description=f"{user_name}, your account is already registered.", color=0xc70014)
        await ctx.send(embed=embed)


@client.command()
async def beg(ctx):
    await ctx.send("This command has been turned off for this season.")
    # author = ctx.author.id
    # beg_amount = 500.00
    
    # if collection_userInfo.find({"_id": author}):

    #     #if the users balance is <500 and they have no current bets 
    #     user = collection_userInfo.find_one({"_id": author})
    #     if user['balance'] < beg_amount and not collection_userBets.find_one({"user_id":author}):
    #         collection_userInfo.update_one({"_id":author}, {"$set": {"balance": beg_amount}})
    #         await ctx.send("Someone gave you a few bucks! You now have $"+str(beg_amount))
        
    #     else: 
    #         await ctx.send("You must have less than $500 (with no active bets) to beg. ")

    #     # balance = user['balance']
    #     # balance = balance+5
    #     # collection_userInfo.update_one({"_id":author}, {"$set": {"balance": balance}})
    #     #fook da meyweddas 

    # else:
    #     await ctx.send("You must register before begging. Please type the -register command")



@client.command(pass_context=True)
@commands.has_any_role("Papa")
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
    embed.set_footer(text="Please use the ;events <Sport ID> command to view the current events for the sports.\nExample: ;events custom")
    await ctx.send(embed=embed)
    


@client.command()
async def events(ctx, key):

  try:
    events = getEvents(key)
    output = ""
    output_id = ""
    output_teams = ""
    output_teams2 = ""
    output_odds_and_time = ""
    output_date = ""

    if not events:
        embed=discord.Embed(title=f"Could not find any events for this sport. Please try again later.",color=0x001cf0)
        await ctx.send(embed=embed)
    
    else:    
        for event in events:

            #logic for 24hr formatting
            conv_date = event['commence_time'].ctime()
            shortened_date = conv_date[:len(conv_date)-8 ]

            #logic for 12hr formatting 
            #print(conv_date)
            # conv_date_for_date = shorten_date(conv_date, " ", 3)
            # conv_date_for_time = shorten_date(conv_date, ":", 2)
            # time_index = shorten_date_index(conv_date_for_time, ":", 1)
            # time = conv_date_for_time[time_index-2:time_index+3]
            # time_conversion = datetime.strptime(time, "%H:%M")
            # time_conversion = time_conversion.strftime("%I:%M %p")

            #2021-06-12 18:00:00 2021


            #output_date = output_date+f"{conv_date_for_date}, {time_conversion}\n"
            output_date = output_date+f" {shortened_date}\n"
            #output = output+f"{event['id'][0:3]} | {event['teams'][0]} vs. {event['teams'][1]} | {event['odds']['h2h'][0]} to {event['odds']['h2h'][1]} | {datetime} \n"
            output_id = output_id+f"{event['id'][0:3]} \n"
            output_teams = output_teams+f"{event['teams'][0]} vs. {event['teams'][1]} \n"
            output_teams2 = output_teams2+f"{event['teams'][0]} vs. {event['teams'][1]} ({event['id'][0:3]}) \n" 
            team1odds = round(getDecimalOdds(event['odds']['h2h'][0]),2)
            team2odds = round(getDecimalOdds(event['odds']['h2h'][1]),2)
            output_odds_and_time = output_odds_and_time+f"{team1odds}x to {team2odds}x \n"
            name = event['sport_nice']
        
        embed=discord.Embed(title=f"Upcoming events for {name}", description="Event information for upcoming events",color=0x001cf0)
        embed.add_field(name="Event ID", value=output_id, inline=True)
        embed.add_field(name="Teams (1 & 2)", value=output_teams, inline=True)
        embed.add_field(name="Odds", value=output_odds_and_time, inline=True)
        embed.set_footer(text=f"Please use the ';bet <amount> <team number> <event ID> <Sport ID>' to place a bet. \nExample: ;bet 100 2 4w1 {key}")
        
        embed2=discord.Embed(title=f"Date & time of {name} events", description="Time information for the events",color=0x001cf0)
        embed2.add_field(name="Teams (1 & 2)", value=output_teams2, inline=True)
        embed2.add_field(name="Commence Time", value=output_date, inline=True)
        embed2.set_footer(text=f"Please use the ';bet <amount> <team number> <event ID> <Sport ID>' to place a bet. \nExample: ;bet 100 2 4w1 {key}")
        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)
        
        

  except Exception as e:

    await ctx.send("The key you inputting was incorrect or missing. Please type ;help for more information. "+str(e))


@events.error
async def on_command_error(ctx, error):
    await ctx.send("Please use the command as follows: ;events <sport key>. You can get the sports key from typing the ;sports command.")

@client.command()
async def bet(ctx,bet,team,eventID,key):


    author = ctx.author.id
    present = datetime.now()

    if collection_userInfo.find_one({"_id": author}):
        
        user = collection_userInfo.find_one({'_id': author})
        userBalance = user['balance']

        #for bet all 
        if (str(bet).lower() == "all"):
            bet = round(userBalance,2)
        

        
        #getting event info 
        if key.lower() == "custom":  
            event_info = collection_custom_events.find_one({"_id": eventID})
            #print(event_info)
            teams = event_info['teams']
            teamsvs_string = f"{teams[0]} vs {teams[1]}"
            odds = event_info['odds']['h2h']
            start = event_info['commence_time']
            
        
        else: 
            event_info = getEventInformation(key, eventID)
            #print(event_info)

            teams = event_info['teams']
            teamsvs_string = f"{teams[0]} vs {teams[1]}"
            odds = event_info['odds']['h2h']
            start = event_info['commence_time']

            
        if (int(userBalance) < int(bet) or int(userBalance) == 0):
            await ctx.send(f"Insufficient Funds. You have ${userBalance} to spend.")
        
        elif (int(team) != 1 and int(team) != 2):
            await ctx.send("Please enter a valid team (1 or 2) and check the betting format.")
        
        elif (present > start):
            await ctx.send("Sorry, you cannot bet for a custom event once it has started. This is because the odds don't change as the match goes on :(")

        # #checks if the user has enough money and chose the right team numbers
        # if ( (key.lower() != "custom") and ((int(userBalance) < int(bet)) or (int(team) != 1 and int(team) != 2)) ):
        #         await ctx.send("Unable to process your bet. Please check your balance and betting format")

        # elif ((key.lower() == "custom") and ((int(userBalance) < int(bet)) or (present > start) or (int(team) != 1 and int(team) != 2))):
        #         await ctx.send("Unable to process your bet. Please check your balance and betting format")
            
        else:
            
            collection_userInfo.update_one({"_id":author}, {"$set": {"balance": int(userBalance) - int(bet)}})
            post = {"user_id": author, "team": [teams[int(team)-1] , int(team)], "amount": int(bet), "event_id": eventID, "odds": odds, "key": key, "event_teams": teams, "commence_time": start}
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
    print(error)
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

        bets = collection_userBets.find({"user_id": author})
        amount_in_bets = 0
        if bets: 
            for bet in bets:        
                amount_in_bets += bet['amount']


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

            for item in reversed(record):
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
            embed.add_field(name="Account Balance", value=f"${roundedBalance} + (${amount_in_bets})", inline=True)
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
                newBalance = (float(bet['amount']) * payoutMultiplier) + user['balance']
                earnings = newBalance - (float(user['balance']) + float(bet['amount']))
                collection_userInfo.update_one({"_id": user_id}, {"$set": {"balance": newBalance}})
                conquisatadors.append(user_id)

                #post = {"result": "Win","event_id": eventID,"key": bet['key'], "earnings": earnings}

                user_record_temp = user['record']

                new_record = ["Win",eventID,earnings,bet['key'], bet['event_teams']]
                user_record_temp.append(new_record)
                

                collection_userInfo.update_one({"_id":user_id},{"$set": {"record":user_record_temp}})

            else:
                earnings = -1 * float(bet['amount'])
                user_record_temp = user['record']
                new_record = ["Loss",eventID,earnings,bet['key'], bet['event_teams']]
                user_record_temp.append(new_record)
                collection_userInfo.update_one({"_id":user_id},{"$set": {"record":user_record_temp}})


        if key.lower() == "custom":
            collection_custom_events.delete_one({"_id": eventID})

        collection_userBets.delete_many({"event_id": eventID})
        
        output = ""
        
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
        #tim
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
    

@client.command(pass_context=True)
@commands.has_any_role("Papa")
async def payoutlist(ctx):
    
    author = ctx.author.id

    bets = collection_userBets.find({})

    #event_id, teams

    output = []
    output2 = []

    if bets.count() == 0: 
        await ctx.send("There are no current events to be paid out.")
    else: 

        #get the list of all the events from all the bets, and remove duplicates from the array 
        for bet in bets:   

            if not output: 
                output.append(bet)
                output2.append(bet['event_id'])

            else: 
                if bet['event_id'] not in output2:
                    #print(f"{bet['event_id']}  ==  {output[i]['event_id']}")
                    #print(f"{bet['event_id']}  ==  {output[i]['event_id']}")
                    output.append(bet)
                    output2.append(bet['event_id'])
            


        eventNumber = ""
        eventID = ""
        eventTeams=""
        commenceTimes=""

        for i in range(len(output)):
            eventNumber = eventNumber+f"{i+1} \n"
            eventID = eventID+f"{output[i]['event_id']}  \n"
            eventTeams = eventTeams+ f"{output[i]['event_teams'][0]} vs. {output[i]['event_teams'][1]} \n"

            #formatting time for the payout list 

            #logic for 24hr formatting 
            conv_date = output[i]['commence_time'].ctime()
            shortened_date = conv_date[:len(conv_date)-8 ]
            #print(conv_date)

            #logic for 12hr formattig
            # conv_date_for_date = shorten_date(conv_date, " ", 3)

            # conv_date_for_time = shorten_date(conv_date, ":", 2)
            # time_index = shorten_date_index(conv_date_for_time, ":", 1)
            # time = conv_date_for_time[time_index-2:time_index+3]
            # time_conversion = datetime.strptime(time, "%H:%M")
            # time_conversion = time_conversion.strftime("%I:%M %p")

            #commenceTimes = commenceTimes + f"{conv_date_for_date}, {time_conversion} \n"
            commenceTimes = commenceTimes + f"{shortened_date} \n"

        
        # print(f"eventNumber: {eventNumber}")
        # print(f"eventID: {eventID}")
        # print(f"eventTeams: {eventTeams}")
        #print(f"commence times: {commenceTimes}")

        # if eventNumber == "":
        #     eventID = "x"
        #     eventNumber ="x"
        #     eventTeams = "x"



        embed=discord.Embed(title="All Current Events", description=f" These are all the events which have not been paid out.", color=0xf5cb42)
        #embed.add_field(name="#", value=eventNumber, inline=True)
        embed.add_field(name="Event ID", value=eventID, inline=True)
        embed.add_field(name="Teams", value=eventTeams, inline=True)
        embed.add_field(name="Commence Time", value=commenceTimes, inline=True)
        embed.set_footer(text="To payout use: ;payout <eventID> <Winning Team> ")
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
        
        event_info = getEventInformation(delete['key'], delete['event_id'])
        
        start = event_info['commence_time']
        present = datetime.now()

        # diff = start - present
        # days, seconds = diff.days, diff.seconds
        # hours = days * 24 + seconds // 3600
        # minutes = (seconds % 3600) // 60
        # seconds = seconds % 60
        ##################################################################################
        #NEED TO FINISH CODE. ONLY ALLOWED TO DELTETE IF EVENT IS A SPECIFIC TIME AWAY. 
        #CANCELLING A BET ALSO HAS A PENALTY
        if present > start :
            embed=discord.Embed(title="Denied", description=f"{ctx.author.mention}, This bet could not be deleted.", color=0xf50000)
            embed.set_thumbnail(url="https://lh3.googleusercontent.com/proxy/jDyt5HBuNMwTe1ugtGAEKsaJn9n4XmmEvxydQcLtBp1Km4rT5XgcAyOTGIq31DPbbH0sgafWwHohuaxXNtpUPlcf7CmXTLNQVky3PeJM1-v43j-k9Cln2O1YMh1h5HBMWeP1brKZ5rwVEj2zcQFxfjS4xKn5Ys8")
            embed.add_field(name="Reason", value=f"A bet cannot be deleted after the event has started.", inline=True)
            await ctx.send(embed=embed)

        else:
            
            user = collection_userInfo.find_one({'_id': author})
            userBalance = user['balance']
            paybackAmount = delete["amount"]
            collection_userBets.delete_one(delete)
            collection_userInfo.update_one({"_id":author}, {"$set": {"balance": userBalance + paybackAmount}})

            embed=discord.Embed(title="Bet Deleted", description=f"{ctx.author.mention}, the specified bet has been removed.", color=0x2309ec)
            embed.set_footer(text="NOTE: You can NOT delete a bet after the event has started.")
            await ctx.send(embed=embed)

    @deletebet.error
    async def on_command_error(ctx, error):
        await ctx.send("Please input a valid bet index to delete.")




@client.command()
async def help(ctx):
    embed=discord.Embed(title="Help Guide for Me!", description="This guide provides with all the commands users and admins can perform and what they do.", color=0x001df5)
    embed.add_field(name=";register", value="You must be registered first to make any bets. Once you register, you automatically get $1000 for betting. ", inline=False)
    embed.add_field(name=";account", value="Shows your account information", inline=False)
    embed.add_field(name=";balance", value="Shows your current balance", inline=False)
    embed.add_field(name=";beg", value="If user has less than $500 and no active bets, then the user can use this command to gain $500.", inline=False)
    embed.add_field(name=";sports", value="This command will give the user a list of sports that they can bet on and their sport ID. Users will use the sport ID to find events for that specific sport, as well as making bets.", inline=False)
    embed.add_field(name=";events <sport id>", value="This command takes in one argument: <sport id>. This id can be found by using the ;sports command. Users can use this command to find out all the upcoming events for a specific sport for betting purposes. Users will be given an event id for all the events. They will use this id to place their bets for those events.", inline=False)
    embed.add_field(name=";bet <bet amount> <team #> <event id> <sport id>", value="This command takes in four arguments. The first argument <bet> is the amount of money users want to bet or 'all'. The second argument <team #> is the team they would like to bet on. Valid entries for team are either 1 or 2. Third argument is the event ID which users can find using the ;events <sport id> command. And finally, the last argument is the <sport id>, which users can find using the ;sports command. All of these together will allow users to bet on their team of their liking.", inline=False)
    embed.add_field(name=";mybets", value="Shows your current ongoing bets", inline=False)
    embed.add_field(name=";deletebet <bet #> ", value="Delete any of your ongoing bets using your bet # obtained from ;mybets. NOTE: You are unable to delete bets for events that have already started", inline=False)
    embed.add_field(name=";help", value="self explanatory ", inline=False)
    embed.set_footer(text="Developed by Wowsixk & Fry")
    await ctx.send(embed=embed)


@client.command()
async def admin(ctx):
    embed=discord.Embed(title="Admin Commands", description="If you are not an admin, close your eyes", color=0x8c6ef0)
    embed.add_field(name=";payout <eventID> <winner>", value="The winner must be values '1' or '2'. This command payouts everyone with a bet for a given ID and then deletes their bet. ", inline=False)
    embed.add_field(name=";addEvent <team1> <team2> <odds1> <odds2> <commence_time> ", value="Adds a custom event. time format (24hr) example: '2021-06-05 04:51:34' *use quotes", inline=False)
    
    embed.add_field(name=";payoutlist ", value="This command will display all the active events", inline=False)
    embed.add_field(name=";admin", value="This command displays this embed xd", inline=False)
    embed.set_footer(text="Developed by Wowsixk & Fry")
    await ctx.send(embed=embed)

@client.command(pass_context=True)
@commands.has_any_role("Papa")
async def addEvent(ctx, team1,team2, odds1, odds2, commence_time):

    #generate random 3 char id 
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    #date1 = '22-May-2050 19:54:36'
    teams = [team1,team2]
    odds = {"h2h":[int(odds1),int(odds2)]}
    commence_time_object = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')

    collection_custom_events.insert_one({"_id": x.lower(),"teams": teams, "odds": odds, "commence_time": commence_time_object, "sport_nice": "custom"})
    #collection_userBets.insert_one({"_id": eventID})
    await ctx.send("New Event Created")

#making the Season 1 end announcement 
@client.command(pass_context=True)
@commands.has_any_role("Papa")
async def announce2(ctx):

    channel = client.get_channel(694110022895927347)

    embed=discord.Embed(title=f"Hello Everyone!", description=f" :moneybag: {ctx.message.guild.default_role}, we will be removing the ;beg command at 9 PM tonight and all betting will stop on June 30th to wrap up season 1 of Sports Betting. You can still make bets and redeem prizes until June 31st but you are unable to ;beg if you lose it all.:moneybag: \n\n Thanks to everyone who participated in the betting and I will see you all in season 2!", color=0x7cff6b)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/694049574637010955/851032093115023360/cute-hamster-cartoon_167995-717.png")
    embed.set_footer(text=f"All the winners will be announced at the end of the season. - Ben")
    await channel.send(embed=embed)


#making the initial announcement with Ben
@client.command(pass_context=True)
@commands.has_any_role("Papa")
async def announce(ctx):

    channel = client.get_channel(694110022895927347)

    embed=discord.Embed(title=f"Hello Everyone!", description=f" :moneybag: {ctx.message.guild.default_role}, I'm Benjamin (aka ben) and I'm the server's betting bot. You can use me to bet on sports and other events in <#842884441361743903> . You can spend your winnings to redeem prizes! <:PogU:764011454256119809> Type ;help in betting for instructions. <:HYPERS:765321182202691664> :moneybag: ", color=0x7cff6b)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/694049574637010955/851032093115023360/cute-hamster-cartoon_167995-717.png")
    embed.add_field(name="$$ SALE $$ Current ben role: $1000 :robot: ", value="• Get full control of benjamin for 3 days", inline=True )
    embed.add_field(name="Shot-Caller (Tier 1: $10 000) :fire: ", value="• Discord Nitro Classic \n• $5 Gift Card (Tim Hortons, Amazon, Uber Eats) \n", inline=False)
    embed.add_field(name="Oracle (Tier 2: $20 000) :crystal_ball:", value="• Discord Nitro (1 month)  \n• $15 Gift Card (Tim Hortons, Amazon, Uber Eats) \n", inline=False)
    embed.add_field(name="Highroller (Tier 3: $30 000) <:gachiGASM:765786036391247882>", value="• XL RGB Gaming Mousepad  \n• $30 Gift Card (Tim Hortons, Amazon, Uber Eats) \n", inline=False)
    embed.add_field(name="Top Doggo (Tier 4: $100 000) <:emoji_80:656309281120976896>", value="• Nintendo Switch (qty: 1) \n• Razer Deathadder V2 Gaming Mouse  \n• Logitech G413 Gaming Keyboard", inline=False)
    embed.set_footer(text=f"Thanks to everyone who tested the Beta, all the accounts have been reset xD. Good Luck Everyone!")
    await channel.send(embed=embed)
    

@client.command(pass_context=True)
@commands.has_any_role("current ben","Papa")
async def talk(ctx, msg):

    channel = client.get_channel(842884441361743903)
    #user = client.get_user(user_id)

    
    #embed=discord.Embed(title=random.choice(greetings_rexy), description=f"{msg}", color=0x7cff6b)
    embed=discord.Embed(title=random.choice(greetings_ben), description=f"{msg}", color=0x7cff6b)


    #271441561844318208 
    #ben pic 
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/694049574637010955/851032093115023360/cute-hamster-cartoon_167995-717.png")
    #ben footer
    embed.set_footer(text=f"-Benjamin (aka ben)")

    
    #rexy stuff 
    #zawars dinosaur 
    #embed.set_thumbnail(url="https://lumiere-a.akamaihd.net/v1/images/open-uri20150422-20810-1pw6dak_23081c6b.jpeg")
    
    #rexy footer 
    #embed.set_footer(text=f"-Rexy")


    await channel.send(embed=embed)

client.run(TOKEN)
    

