import discord
from discord.ext import tasks
from discord import option
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime, timedelta
from subprocess import check_output, Popen, PIPE
import http.client
import json

load_dotenv()
TOKEN = os.getenv('FLOOR_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

with open("./oldBounties.json", "r") as f:
        oldBounties = json.load(f)

with open("./currBounties.json", "r") as f:
        currBounties = json.load(f)

with open("./collections.json", "r") as f:
        collections = json.load(f)

# def sweepTracker():
#     start = datetime(2022, 9, 4).timestamp()
#     with open("./activities.json", "r") as f:
#         data = json.load(f)
#     print(len(data))
#     sweepers = {}
#     for d in data:
#         if d['blockTime'] > start:
#             if d["buyer"] in sweepers:
#                 sweepers[d["buyer"]] += 1
#             else:
#                 sweepers[d["buyer"]] = 1
#     print(sweepers)

def getEmbedTemplate():
    embed=discord.Embed()
    # title="Pantha Games Bot",
    #     url="https://pantha.gitbook.io/pantha-games/about/info",
    #     # description="Here are some ways to format text",
    #     color=discord.Color.blue())
    embed.set_image(url="attachment://filename.png")
    embed.set_author(name="Brought to you by Hello Pantha", url="https://twitter.com/HelloPantha", icon_url="https://y2kumgw6aoqh3hbr3qgog7wlgbybnuxwcmhlvmpuy7fmlmepu7ba.arweave.net/xpVGGt4DoH2cMdwM437LMHAW0vYTDrqx9MfKxbCPp8I")
    embed.set_footer(text="Purchase a Pantha: https://magiceden.com/marketplace/hello_pantha")
    return embed

def getExistingBounties(server):
    existingRewards = {}
    for i in range(len(currBounties[server]['bounties'])):
        nft = list(currBounties[server]['bounties'][i].keys())[0]
        if currBounties[server]['bounties'][i][nft]['reward'] in existingRewards:
            existingRewards[currBounties[server]['bounties'][i][nft]['reward']] += currBounties[server]['bounties'][i][nft]['amount']
        else:
            existingRewards[currBounties[server]['bounties'][i][nft]['reward']] = currBounties[server]['bounties'][i][nft]['amount']
    return existingRewards

def checkTokenBalance(server, amount, reward):
    path = Path(f"/Users/reidelkins/Solana/HelloPanthers/WhitelistTool/collabBot/{server}.json")
    if path.is_file():
        # Popen(["solana", "config", "set", "-k", f"./{server}.json"])
        if reward == "SOL":
            balance = (check_output(f"solana balance ./{server}.json" , shell=True).decode("utf-8"))
            balance = float(balance.split(" ")[0])
        else:
            balance = float(check_output(f"spl-token balance {reward} --owner ./{server}.json" , shell=True).decode("utf-8"))
        if amount > balance:
            return False
        existingRewards = getExistingBounties(server)
        if reward not in existingRewards:
            return True
        elif existingRewards[reward] + amount > balance:
            return False
        else:
            return True
    else:
        return "ERROR"

def hasSOL(server):
    path = Path(f"/Users/reidelkins/Solana/HelloPanthers/WhitelistTool/collabBot/{server}.json")
    if path.is_file():
        # Popen(["solana", "config", "set", "-k", f"./{server}.json"])
        balance = (check_output(f"solana balance ./{server}.json" , shell=True).decode("utf-8"))
        balance = float((balance.split(" "))[0])
        if balance > 0:
            return True
    return False

def hasPOP(server):
    return True
    path = Path(f"/Users/reidelkins/Solana/HelloPanthers/WhitelistTool/collabBot/{server}.json")
    if path.is_file():
        try:
            Popen(["solana", "config", "set", "-k", f"./{server}.json"])
            balance = float(check_output(f"spl-token balance popwcrLzjetHAFCH91LBTK78zapZ54Rftpc7PGoHpuh --owner ./{server}.json" , shell=True).decode("utf-8"))
        except:
            return False
        if balance >= 50:
            return True
    return False

def getListings(server):
    offset = 0
    returnedData = True
    first = True
    with open(f"./{server}_listings.json", "w") as f:
        f.write('[\n')
    while(returnedData):
        conn = http.client.HTTPSConnection("api-mainnet.magiceden.dev")
        payload = ''
        headers = {}
        conn.request("GET", f"/v2/collections/{collections[server]}/listings?offset={offset}", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        listings =  json.loads(data)
        with open(f"./{server}_listings.json", "a+") as f:
            for d in listings:
                if not first:
                    f.write(',')
                else:
                    first = False
                d = json.dumps(d)
                d = d.strip()
                
                f.writelines(d)
                f.write('\n')
        print(offset)
        if len(listings) == 0:
            returnedData = False
        else: 
            offset += len(listings)
    with open(f"./{server}_listings.json", "a+") as f:
        f.write(']')


def getActivities(server, offset):
    conn = http.client.HTTPSConnection("api-mainnet.magiceden.dev")
    payload = ''
    headers = {}
    conn.request("GET", f"/v2/collections/{server}/activities?offset={offset}&limit=1000", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)


def getAllBuys(server):
    offset = 0
    returnedData = True
    first = True
    with open(f"./{server}_activities.json", "w") as f:
        f.write('[\n')
    while(returnedData):
        jsonData = []
        data = getActivities(collections[server], offset)
        if data:
            for i in range(len(data)):
                if data[i]['type'] == "buyNow":
                    jsonData.append(data[i])
            blockTime = data[i]['blockTime']
            if blockTime < currBounties[server]['start']:
                returnedData = False
            
            with open(f"./{server}_activities.json", "a+") as f:
                for d in jsonData:
                    if not first:
                        f.write(',')
                    else:
                        first = False
                    d = json.dumps(d)
                    d = d.strip()
                    f.writelines(d)
                    f.write('\n')
        if len(data) == 0:
            returnedData = False 
        else:
            print(offset)
            offset += len(data)
    with open(f"./{server}_activities.json", "a+") as f:
        f.write(']')


def getOneActivity(collection):
    conn = http.client.HTTPSConnection("api-mainnet.magiceden.dev")
    payload = ''
    headers = {}
    conn.request("GET", f"/v2/collections/{collection}/activities?offset=0&limit=10", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)


def checkIfNFTExists(nft, server):
    getListings(server)
    path = Path(f"/Users/reidelkins/Solana/HelloPanthers/WhitelistTool/collabBot/{server}_listings.json")
    if path.is_file():
        with open(f"{server}_listings.json", "r") as f:
            listings = json.load(f)
        for listing in listings:
            if listing['tokenAddress'] == nft:
                return True
        return False
    else:
        return "ERROR"


def getBountyInfo(server):
    getAllBuys(server)
    currBounties[server]['lastChecked'] = datetime.now().timestamp()
    with open("./currBounties.json", "w") as f:
        json.dump(currBounties, f)
    with open(f"./{server}_activities.json", "r") as f:
        allBuys = json.load(f)
    for purchase in allBuys:
        for i in range(len(currBounties[server]['bounties'])):
            nft = list(currBounties[server]['bounties'][i].keys())[0]
            if purchase['tokenMint'] == nft:
                if currBounties[server]['bounties'][i][nft]['status'] == 'alive':
                    currBounties[server]['bounties'][i][nft]['status'] = "Awaiting Payment"
                    currBounties[server]['bounties'][i][nft]['buyer'] = purchase['buyer']
                    with open("./currBounties.json", "w") as f:
                        json.dump(currBounties, f)

def getBountyAdmin(server):
    with open(f"./currBounties.json", "r") as f:
        data = json.load(f)
    bounties = data[server]['bounties']
    value = "**Row Info: NFT, Status, Amount, Reward**\n "
    for i in range(len(bounties)):
        nft = list(currBounties[server]['bounties'][i].keys())[0]
        value += f"**{i+1}.** {nft} {currBounties[server]['bounties'][i][nft]['status']} {currBounties[server]['bounties'][i][nft]['amount']} {currBounties[server]['bounties'][i][nft]['reward']}\n\n"
    
    return value

def getBounty(server, embed):
    with open(f"./currBounties.json", "r") as f:
        data = json.load(f)
    bounties = data[server]['bounties']
    for i in range(len(bounties)):
        nft = list(currBounties[server]['bounties'][i].keys())[0]
        if currBounties[server]['bounties'][i][nft]['status'] == "alive":
            if currBounties[server]['bounties'][i][nft]['reward'] == "3E83XeuLtb4yVTTfTTYx99pjFZ3WvZRyGvN8sE2fzGeZ":
                value = f"**Not Found Yet** | {currBounties[server]['bounties'][i][nft]['amount']} | AI Pantha WL\n\n"
            else:
                value = f"**Not Found Yet** | {currBounties[server]['bounties'][i][nft]['amount']} | {currBounties[server]['bounties'][i][nft]['reward']}\n\n"
            embed.add_field(name=f"**{i+1}.**", value=value, inline=False)
        else:
            value = f"**{currBounties[server]['bounties'][i][nft]['status']}** | {nft} | {currBounties[server]['bounties'][i][nft]['amount']} | {currBounties[server]['bounties'][i][nft]['reward']}\n"
            value += f"Winner  🎉 - {currBounties[server]['bounties'][i][nft]['buyer']}\n\n"
            embed.add_field(name=f"**{i+1}.**", value=value, inline=False)
    return embed

@bot.slash_command(name="create_dao_wallet")
async def create_dao_wallet(ctx):
    embed=getEmbedTemplate()
    server = str(ctx.guild).replace(" ", "_")
    path = Path(f"./{server}.json")
    if path.is_file():
        address = (check_output(f"solana address -k ./{server}.json" , shell=True).decode("utf-8"))
        embed.add_field(name="Error", value=f"Dao Wallet already exists. The Public Key is {address}", inline=False)
    else:
        Popen(["solana-keygen", "new", "--outfile", f"./{server}.json", "--no-bip39-passphrase"], stdin=PIPE)
        address = (check_output(f"solana address -k ./{server}.json" , shell=True).decode("utf-8"))
        embed.add_field(name="Success", value=f"Your wallets Public Key is {address}! Make sure you fund it so you can start your own Pantha Games!", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="add_collection_name")
async def add_collection_name(ctx, collection_name: str):
    server = str(ctx.guild).replace(" ", "_")
    embed=getEmbedTemplate()
    request = getOneActivity(collection_name)
    if len(request) == 0:
        embed.add_field(name="Error", value=f"We did not get any data back when checking for {collection_name}, if you think this is wrong, then please try again.", inline=False)
    else:
        collections[server] = collection_name
        with open("./collections.json", "w") as f:
             json.dump(collections, f)
        embed.add_field(name="Success", value=f"{collection_name} set as the collection for your server!", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="create_bounty_contest")
@option(
    "attachment",
    discord.Attachment,
    description="A screenshot of the listed NFTs from ME",
    required=True  # The default value will be None if the user doesn't provide a file.
)
async def create_bounty_contest(ctx, screenshot: discord.Attachment, weeks: int=0, days: int=0,):
    server = str(ctx.guild).replace(" ", "_")
    file = await screenshot.to_file()
    await screenshot.save(f"./{server}_bountySS.jpg")
    embed=getEmbedTemplate()
    if server not in collections:
        embed.add_field(name="Error", value=f"No collection set. Please use the add_collection_name command before creating your first bounty!", inline=False)
    elif weeks == 0 and days == 0:
        embed.add_field(name="Error", value=f"A duration for the bounty contest is needed (i.e. set the weeks or days variable)", inline=False)
    elif hasSOL(server):
        if hasPOP(server):
            if server in currBounties:
                embed.add_field(name="Error", value=f"You already have an active bounty contest. Please end it before you start a new one.", inline=False)
            else:
                currBounties[server] = {}
                # Popen(["spl-token", "transfer", "popwcrLzjetHAFCH91LBTK78zapZ54Rftpc7PGoHpuh", "50", "7C1U6TADmn5Ayhq5S5J48ipWU11qsjZ9wYCiJbMpgys3", "--owner", f"./{server}.json"])
                currBounties[server]['start'] = (datetime.now() + timedelta(hours=5)).timestamp()
                currBounties[server]['lastChecked'] = (datetime.now() - timedelta(hours=1) + timedelta(hours=5)).timestamp()
                days += (weeks * 7)
                currBounties[server]['end'] = (datetime.now() + timedelta(days = days) + timedelta(hours=5)).timestamp()
                currBounties[server]['bounties'] = []
                with open("./currBounties.json", "w") as f:
                    json.dump(currBounties, f)
                embed.add_field(name="Success", value=f"Bounty Contest Started! It will end at {datetime.fromtimestamp(currBounties[server]['end'])} UTC. Make sure you add rewards to your bounty!", inline=False)
        else:
            embed.add_field(name="Error", value=f"To start a new bounty contest it costs 50 $POP. Please go to https://famousfoxes.com/tokenmarket to purchase more!", inline=False)
    else:
        embed.add_field(name="Error", value=f"Please fund this wallet with a little SOL so you will be able to pay gas fees for the rewards!", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="add_bounty")
async def add_bounty(ctx, nft: str, amount: float, reward: str="SOL"):
    server = str(ctx.guild).replace(" ", "_")
    embed=getEmbedTemplate()
    if server not in currBounties:
        embed.add_field(name="Error", value=f"You do not have a current bounty contest going. Make one with the create_bounty_contest command.", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        await ctx.defer()
        foundNFT = checkIfNFTExists(nft, server)
        foundEnoughToken = checkTokenBalance(server, amount, reward)
        if foundNFT == "ERROR":
            embed.add_field(name="Error", value=f"There was an issue retrieving listing results. Please try the command again", inline=False)
        elif foundEnoughToken == "ERROR":
            embed.add_field(name="Error", value=f"There was an error trying to check your account balances. Please make sure you have created a dao wallet and try the command again.", inline=False)
        elif not foundNFT:
            embed.add_field(name="Error", value=f"Did not find that {nft} listed on MagicEden.", inline=False)
        elif not foundEnoughToken:
            embed.add_field(name="Error", value=f"Either did not find the {reward} token in your DAO wallet or there is not enough of that along with the rest of the current bounties.", inline=False)
        else:
            for i in range(len(currBounties[server]['bounties'])):
                if nft in currBounties[server]['bounties'][i].keys():
                    embed.add_field(name="error", value=f"There is already a bounty for {nft}.")
                    await ctx.followup.send(embed=embed, ephemeral=True)
                    return
            currBounties[server]['bounties'].append({nft: {"reward":reward, "amount":amount, "status":"alive"}})
            with open("./currBounties.json", "w") as f:
                json.dump(currBounties, f)
            embed.add_field(name="Success", value=f"Bounty added on {nft}. The reward will be {amount} {reward}.", inline=False)
    await ctx.followup.send(embed=embed, ephemeral=True)


@bot.slash_command(name="remove_bounty")
async def remove_bounty(ctx, nft: str):
    server = str(ctx.guild).replace(" ", "_")
    notFound = True
    embed=getEmbedTemplate()
    if server not in currBounties:
        embed.add_field(name="Error", value=f"You do not have a current bounty contest going. Make one with the create_bounty_contest command.", inline=False)
    else:
        for i in range(len(currBounties[server]['bounties'])):
            if nft in currBounties[server]['bounties'][i].keys():
                if currBounties[server]['bounties'][i][nft]['status'] == 'alive':
                    del currBounties[server]['bounties'][i]
                    with open("./currBounties.json", "w") as f:
                        json.dump(currBounties, f)
                    embed.add_field(name="Success", value=f"You have removed the bounty for {nft}", inline=False)
                else:
                    embed.add_field(name="Error", value=f"You cannot remove a bounty that has already been awarded.", inline=False)                
                await ctx.respond(embed=embed, ephemeral=True)
                return
        embed.add_field(name="Error", value=f"The {nft} NFT is not currently part of your bounty contest.", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)


#TODO
@bot.slash_command(name="check_bounty_admin")
async def check_bounty_admin(ctx):
    server = str(ctx.guild).replace(" ", "_")
    embed=getEmbedTemplate()
    if server not in currBounties:
        embed.add_field(name="Error", value=f"You do not have a current bounty contest going. Make one with the create_bounty_contest command.", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        file = discord.File(f"./{server}_bountySS.jpg")
        if datetime.now() - timedelta(minutes=10) > datetime.fromtimestamp(currBounties[server]['lastChecked']):
            await ctx.defer()
            getBountyInfo(server)
            value = getBountyAdmin(server)
            embed.add_field(name=f"Bounty Contest - Ends at {str(datetime.fromtimestamp(currBounties[server]['end']))[:16]} UCT", value=value, inline=False)
            await ctx.followup.send(embed=embed, ephemeral=True, file=file)
        else:
            value = getBountyAdmin(server)
            embed.add_field(name=f"Bounty Contest - Ends at {str(datetime.fromtimestamp(currBounties[server]['end']))[:16]} UCT", value=value, inline=False)
            await ctx.respond(embed=embed, ephemeral=True, file=file)
    

@bot.slash_command(name="check_bounty")
async def check_bounty(ctx):
    server = str(ctx.guild).replace(" ", "_")
    embed=getEmbedTemplate()
    if server not in currBounties:
        embed.add_field(name="Error", value=f"There is not a current bounty countest, please contact an admin to start one!", inline=False)
        await ctx.respond(embed=embed)
    else:
        file = discord.File(f"./{server}_bountySS.jpg")
        if datetime.now() - timedelta(minutes=10) > datetime.fromtimestamp(currBounties[server]['lastChecked']):
            await ctx.defer()
            getBountyInfo(server)
            embed.add_field(name=f"Bounty Contest - Ends at {str(datetime.fromtimestamp(currBounties[server]['end']))[:16]} UCT", value="Good Luck!", inline=False)
            embed = getBounty(server, embed)
            await ctx.followup.send(embed=embed, file=file)
        else:
            embed.add_field(name=f"Bounty Contest - Ends at {str(datetime.fromtimestamp(currBounties[server]['end']))[:16]} UCT", value="Good Luck!", inline=False)
            embed = getBounty(server, embed)
            await ctx.respond(embed=embed, file=file)



@bot.slash_command(name="send_rewards")
async def send_rewards(ctx):
    server = str(ctx.guild).replace(" ", "_")
    embed=getEmbedTemplate()
    if server in currBounties:
        for i in range(len(currBounties[server]['bounties'])):
            nft = list(currBounties[server]['bounties'][i].keys())[0]
            if currBounties[server]['bounties'][i][nft]['status'] == "Awaiting Payment":
                if currBounties[server]['bounties'][i][nft]['reward'] == "SOL":
                    Popen(["solana", "transfer", currBounties[server]['bounties'][i][nft]['buyer'], str(currBounties[server]['bounties'][i][nft]['amount']), "--allow-unfunded-recipient", "--from", f"./{server}.json"])
                else:
                    Popen(["spl-token", "transfer", "--fund-recipient", currBounties[server]['bounties'][i][nft]['reward'], str(currBounties[server]['bounties'][i][nft]['amount']), currBounties[server]['bounties'][i][nft]['buyer'], "--owner", f"./{server}.json"])
            currBounties[server]['bounties'][i][nft]['status'] = "Sent Payment"
            with open("./currBounties.json", "w") as f:
                json.dump(currBounties, f)
        embed.add_field(name="Success", value=f"All winners awaiting payments have been sent their awards!", inline=False)
    else:
        embed.add_field(name="Error", value=f"You do not have an active bounty contest to send rewards for!", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(name="end_bounty")
async def end_bounty(ctx):
    server = str(ctx.guild).replace(" ", "_")
    embed=getEmbedTemplate()
    if server in currBounties:
        if server in oldBounties:
            oldBounties[server].append(currBounties[server])
            with open("./oldBounties.json", "w") as f:
                json.dump(oldBounties, f)
        else:
            oldBounties[server] = [currBounties[server]]
            with open("./oldBounties.json", "w") as f:
                json.dump(oldBounties, f)
        del currBounties[server]
        with open("./currBounties.json", "w") as f:
                json.dump(currBounties, f)
        embed.add_field(name="Success", value="Bounty contest ended, you can now start a new one.", inline=False)
    else:
        embed.add_field(name="Error", value="There is not an active bounty contest to end.", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)
    pass

# @bot.slash_command(name="test_embed")
# async def test_embed(ctx):
#     embed=getEmbedTemplate()
#     embed.add_field(name="*Italics*", value="Surround your text in asterisks (\*)", inline=False)
#     embed.add_field(name="**Bold**", value="Surround your text in double asterisks (\*\*)", inline=False)
#     embed.add_field(name="__Underline__", value="1. Surround your text in double underscores (\_\_)\n2. This is some other data", inline=False)
#     embed.add_field(name="~~Strikethrough~~", value="Surround your text in double tildes (\~\~)", inline=False)
#     embed.add_field(name="`Code Chunks`", value="Surround your text in backticks (\`)", inline=False)
#     embed.add_field(name="Blockquotes", value="> Start your text with a greater than symbol (\>)", inline=False)
#     embed.add_field(name="Secrets", value="||Surround your text with double pipes (\|\|)||", inline=False)
#     await ctx.respond(embed=embed, ephemeral=True)

#TODO check that currBounty is still active everywhere

bot.run(TOKEN)
