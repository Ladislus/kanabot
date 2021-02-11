from discord import Client, Message
from discord.utils import get
from command import Command
from config import globalconfig
from utils import isValidCommand
import env


client = Client()

globalCfg = globalconfig.globalConfig_from_file()


@client.event
async def on_ready():
    # Problem while fetching the discord guild
    guild = get(client.guilds, name=env.GUILD)
    if guild is None:
        exit()
    # Else, save the guild informations
    globalCfg._guild = guild

    print(f'{client.user.name} is connected to the following guild: {guild.name}\n')
    print(globalCfg)


@client.event
async def on_message(msg: Message):
    if isValidCommand(msg, globalCfg):
        print('ok')
        com: Command = Command(msg)
        print(com)


client.run(env.TOKEN)