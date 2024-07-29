import os
from typing import Final

import discord
from discord import Client, Intents, Message, app_commands
from discord.ext import commands
from dotenv import load_dotenv

from responses import get_response

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
# openai.api_key = os.getenv('OPENAI_API_KEY')

# BOT SETUP
intents                 = Intents.default()
intents.message_content = True
client                  = Client(intents=intents)
# client                  = commands.Bot(command_prefix="/", intents=intents)
tree                    = app_commands.CommandTree(client)

# MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
        if not user_message:
                print('(Message was empty because intents were not enabled.)')
                return

        # reply back with user message .. remove the ? from the message.
        if is_private := user_message[0] == '?':
                user_message = user_message[1:]

        try:
                response: str = get_response(user_message)
                await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
                print(e)


# HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
        print(f'{client.user} is now running!')


# HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username    : str = str(message.author)
    user_message: str = message.content
    channel     : str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

# bot = commands.Bot(command_prefix="/", intents=intents)

@tree.command(name='ping')
async def ping(interactions: discord.Interaction):
    await interactions.response.send_message('pong')

@client.event
async def sync(ctx: commands .Context):
    await ctx.send( 'Syncing...')
    await client.tree. sync()

@tree.command(name='sync', description='Owner only')
async def sync(interactions: discord.Interaction):
      if interactions.user.id == os.getenv('OWNER_ID'):
            await tree.sync()

@client.event
async def yourmom(ctx: commands .Context):
        await ctx.send( 'is cool')


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()