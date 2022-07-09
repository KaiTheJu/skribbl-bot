import os
import discord
import asyncio
from discord.ext import commands
import json

hstr = '''Guide:
skribbl add <Wort> -- Fügt ein Wort hinzu
skribbl list -- Listet alle Wörter auf
skribbl remove <Wort> -- Entfernt ein Wort
skribbl status -- Zeigt an, ob der Bot aktiv ist'''

class customHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        await self.get_destination().send(hstr)
    
    async def send_command_help(self, command):
        await self.get_destination().send(command.description)

client = commands.Bot(command_prefix = ('skribbl ', 'ß', 'skribble '), help_command=customHelp())

async def getData(name):
    try:
        with open(name + '.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(name + '.json', 'w') as f:
            json.dump([], f)
        return []
    except json.decoder.JSONDecodeError:
        with open(name + '.json', 'w') as f:
            json.dump([], f)
        return []

async def saveData(name, data):
    with open(name + '.json', 'w') as f:
        json.dump(data, f)

async def snorm(string):
    return str(string).lower().strip()

async def norm(x):
    for index, i in enumerate(x):
        x[index] = await snorm(i)
        if len(i) > 30 or not i:
            x.remove(i)
    x = list(set(x))
    x.sort()
    return x

@client.event
async def on_ready():
    print(f'Logged in as "{client.user.name}" with ID "{client.user.id}"')
    print('On The following servers:')
    for server in client.guilds:
        print(server.name)
    print('------\n')

@client.command(description = 'Zeigt an, ob der Bot aktiv ist')
async def status(ctx):
    await ctx.send('Ich stehe zur Verfügung, Sir!')

@client.command(description = 'Fügt ein Wort hinzu.\nEs können auch mehrere Wörter mithilfe von Kommas hinzugefügt werden.')
async def add(ctx, *, message):
    data = await getData(ctx.guild.name)
    for i in message.split(','):
        data.append(i)
    data = await norm(data)
    await saveData(ctx.guild.name, data)
    await ctx.send('gespeichert')

@client.command(description = 'Listet alle Wörter auf', aliases = ['list', 'ls'])
async def words(ctx):
    data = await getData(ctx.guild.name)
    if not data:
        print('Keine Einträge vorhanden.')
    message = ''
    for i in await norm(data):
        message += i + ', '
    if message:
        try:
            await ctx.send(message)
        except discord.errors.HTTPException:
            with open('message.txt', 'w') as f:
                f.write(message)
            await ctx.send(file=discord.File('message.txt'))
            os.remove('message.txt')
    else:
        await ctx.send('Keine Einträge vorhanden')

@client.command(description = 'remove <Wort> -- Entfernt ein Wort')
async def remove(ctx, *, message):
    data = await getData(ctx.guild.name)
    data.remove(message)
    await saveData(ctx.guild.name, await norm(data))
    await ctx.send('Wort entfernt')

token = ''
with open('.token', 'r') as f:
    token = f.read()
client.run(token)
