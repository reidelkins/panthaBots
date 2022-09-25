import os
import psycopg2
import http.client
from datetime import datetime
import sys
import boto3

import discord
from discord.ext import tasks
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
WL = os.getenv('DISCORD_WL_ROLE')

ENDPOINT=os.getenv('ENDPOINT')
PORT=os.getenv('PORT')
USER=os.getenv('USER')
REGION=os.getenv('REGION')
DBNAME=os.getenv('DBNAME')
PASSWORD=os.getenv('PASSWORD')

# gets the credentials from .aws/credentials
session = boto3.Session()
db = session.client('rds', region_name=REGION)

# token = db.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    f.start()
    g.start()
               

@tasks.loop(minutes=1) # alternatively, minutes=60, seconds=3600, etc.
async def f():
    wlRoles = {}
    try:
        conn = psycopg2.connect(
            database="NWL",
            user="hellopantha",
            password="Rokdow-wefto0-cocjuf",
            host="database-1.ckwrxecwlp35.us-east-1.rds.amazonaws.com",
            port='5432',
            sslmode="disable"
        )
        with conn.cursor() as curs:
            sql = """
                SELECT * FROM "Projects" 
            """
            curs.execute(sql)
            query_results = curs.fetchall()
            for query in query_results:
                wlRoles[query[0]] = [query[3], query[12], []]
            # query = """select * from {table} where {pkey} = %s""".format(
            # table=psycopg2.sql.Identifier('CollabRequests'),
            # pkey=psycopg2.sql.Identifier('status'))
            sql = """
                SELECT * FROM "CollabRequests" 
            """
            curs.execute(sql)
            query_results = curs.fetchall()
            for query in query_results:
                if query[4] == 'SUBMITTED':
                    for name in query[5]:
                        wlRoles[query[1]][2].append(name)
            wlRoles[10] = ["tigger's server", 'test1', ["spenceradolph#7564", "tigger#5567", "Highkey#2222", "Gelo#9634"]]
                    
    except Exception as e:
        print("Database connection failed due to {}".format(e))

    for guild in client.guilds:
        print(guild.name)
        for id in wlRoles:
            if wlRoles[id][0] == guild.name:
                for i in range(len(guild.roles)):
                    if guild.roles[i].name == wlRoles[id][1]:
                        role = guild.roles[i]
                    
                for member in guild.members:
                    name = f"{member.name}#{member.discriminator}"
                    if name in wlRoles[id][2]:
                        if wlRoles[id][1] not in member.roles:
                            await member.add_roles(role)
                            print("added")
    print("DONE")

@tasks.loop(seconds=30)
async def g():
    print("sup")

client.run(TOKEN)    
