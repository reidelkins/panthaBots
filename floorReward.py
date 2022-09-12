import http.client
import json
import os
from datetime import datetime

#working
def getActivities(offset):
    print(offset)
    conn = http.client.HTTPSConnection("api-mainnet.magiceden.dev")
    payload = ''
    headers = {}
    conn.request("GET", f"/v2/collections/hello_pantha/activities?offset={offset}&limit=1000", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)

#working
def getListings():
    offset = 0
    returnedData = True
    first = True
    with open("./listings.json", "w") as f:
        f.write('[\n')
    while(returnedData):
        conn = http.client.HTTPSConnection("api-mainnet.magiceden.dev")
        payload = ''
        headers = {}
        conn.request("GET", f"/v2/collections/hello_pantha/listings?offset={offset}", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        listings =  json.loads(data)
        with open("./listings.json", "a+") as f:
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
    with open("./listings.json", "a+") as f:
        f.write(']')

#working
def findFloor():
    floor = {}
    #TODO grab old floor price from somewhere
    floorPrice = 1000
    with open('./listings.json', 'r') as f:
        listings = json.load(f)
    print(len(listings))
    for listing in listings:
        if listing['price'] < floorPrice:
            floorPrice = listing['price']
            floor = {'price': listing['price'], 'address':[listing['tokenAddress']], 'seller': [listing['seller']]}
        elif listing['price'] == floorPrice:
            floor['address'].append(listing['tokenAddress'])
            floor['seller'].append(listing['seller'])
    print(floor)
    return floor

#working
def rewardFloorBuyer():
    #TODO need to actually get this data from somewhere
    oldFloor = {'price': 0.8, 'address': ['FM52aAk7YckrpSdSMV6VzXHaoekYMUCn4C6UVwbW5MoB', 'HDewQoqUwxF3sD45Yb6FPiCQKbiK8xxKbtUXUMcW9tp1', '864WqXVmCHps7jRLd9gAV28GpDSftsMisweiKcF1GKPu'], 'seller': ['5Zw3y4qTQ3gcXSD25bQpEej6LJBRzZHwRpS7FYWLkprV', 'BpLX9fmSS74vRxrPBEM2VD576ubxEnvajNhqRhQ9Mfi2', '12gKpnK5A7V9h8Mshe3Htd9pjiLScm4LZu2vWwCSHqcN']}
    with open("./activities.json", "r") as f:
        data = json.load(f)
    print(len(data))
    for d in data:
        if d['tokenMint'] in oldFloor['address'] and d['seller'] in oldFloor['seller']:
            print(d)
            #randomReward = getRandomReward()
            os.system("solana config set -k ~/.config/solana/xyz.json")
            os.system("solana config set -u m")
            #os.system(f"spl-token transfer popwcrLzjetHAFCH91LBTK78zapZ54Rftpc7PGoHpuh {randomReward} {d['buyer']} --allow-unfunded-recipient")

    return

#working
def getAllBuys():
    offset = 0
    returnedData = True
    first = True
    with open("./activities.json", "w") as f:
        f.write('[\n')
    while(returnedData):
        jsonData = []
        data = getActivities(offset)
        if data:
            for i in range(len(data)):
                if data[i]['type'] == "buyNow":
                    
                    jsonData.append(data[i])

            with open("./activities.json", "a+") as f:
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
            offset += len(data)
    with open("./activities.json", "a+") as f:
        f.write(']')

def sweepTracker():
    start = datetime(2022, 9, 4).timestamp()
    with open("./activities.json", "r") as f:
        data = json.load(f)
    print(len(data))
    sweepers = {}
    for d in data:
        if d['blockTime'] > start:
            if d["buyer"] in sweepers:
                sweepers[d["buyer"]] += 1
            else:
                sweepers[d["buyer"]] = 1
    print(sweepers)

def bountyCheck():
    #TODO could modify this to just check if its between start and end time of bounty
    #bountied = getBountiedNFTs
    bountied = {"token": [], "price": [], "seller": []}
    getAllBuys()
    with open("./activities.json", "r") as f:
        data = json.dumps(f)
    for d in data:
        if d['tokenMint'] in bountied['token']:
            i = bountied['token'].index('tokenMint')
            if d['seller'] == bountied["seller"][i] and d['price'] == bountied["price"][i]:
                print("found one")
                #getRandomReward
                randomReward = ""
                os.system("solana config set -k ~/.config/solana/xyz.json")
                os.system("solana config set -u m")
                if randomReward["type"] == "SOL":
                    os.system(f"solana transfer {d['buyer']} {randomReward['ammount']}")

def main():
    #getAllBuys()
    rewardFloorBuyer()
    sweepTracker()
    
getAllBuys()
sweepTracker()