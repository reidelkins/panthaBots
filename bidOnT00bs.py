import http.client
import json


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
        conn.request("GET", f"/v2/collections/t00bs/listings?offset={offset}", payload, headers)
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

def makeBids():
    buyer="CpXgc3vWKHJLj1Bzk1VqAHYaBrVkn1YqTpjD7jfRLDc3"
    price = 1.55
    expiry = 3600
    with open("./listings.json", "r") as f:
        data = json.load(f)
    for d in data:
        tokenAddress = d['tokenAddress']
        auctionHouse = d['auctionHouse']
        conn = http.client.HTTPSConnection("api-mainnet.magiceden.dev")
        payload = ''
        headers = {}
        conn.request("GET", f"/v2/instructions/buy?buyer={buyer}&auctionHouseAddress={auctionHouse}&tokenMint={tokenAddress}&price={price}&buyerReferral=&expiry={expiry}", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        print(data)
        return
    


def main():
    # getListings()
    makeBids()


main()