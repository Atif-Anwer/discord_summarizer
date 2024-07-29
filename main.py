import asyncio
import os
from typing import Final

import discord
from discord import Intents, Message, app_commands
from discord.ext import commands
from dotenv import load_dotenv

from responses import get_response

# Load the token from the environment
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Bot setup with intents
intents                 = Intents.default()
intents.message_content = True
bot                     = commands.Bot(command_prefix="/", intents=intents)

# Send message functionality
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled.)')
        return

    # Check if the message is private
    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)

# Handling the startup for the bot
# --------------------------------------#
#               ON READY                #
# --------------------------------------#
@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("Error occurred:", e)

# Handling incoming messages
@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    username     = str(message.author)
    user_message = message.content
    channel      = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

# --------------------------------------#
#             SLASH COMMANDS            #
# --------------------------------------#
# Command to reply with 'pong'
@bot.tree.command(name='ping', description='Replies with pong')
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(f'{interaction.user.mention} pong', ephemeral=True)

# --------------------------------------#
# Summarize command with three options
class Summarize(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Summarize last n messages from the user
    @app_commands.command(name="last_messages", description="Summarize the last n messages from a user")
    @app_commands.describe(no_messages="Provide the number of last messages to summarize", user="The user to get the last n messages from")
    async def last_messages(self, interaction: discord.Interaction, no_messages: int, user: discord.User) -> None:
        await interaction.response.send_message(f'Summarizing last {no_messages} messages from {user.name}', ephemeral=True)

    # Summarize the input text
    @app_commands.command(name="text", description="Summarize the provided text")
    @app_commands.describe(text_input="Input text to summarize")
    async def text(self, interaction: discord.Interaction, text_input: str) -> None:
        await interaction.response.send_message(f'Summarizing the text: {text_input}', ephemeral=True)

    # Logic to summarize the weblink
    @app_commands.command(name="link", description="Summarize the provided link")
    @app_commands.describe(weblink="Weblink to summarize")
    async def link(self, interaction: discord.Interaction, weblink: str) -> None:
        await interaction.response.send_message(f'Summarizing the link: {weblink}', ephemeral=True)
# --------------------------------------#
# Command to send the user ID
@bot.tree.command(name="user_id", description='Sends the user ID for a given user.')
async def user_id(interaction: discord.Interaction, member: discord.Member = None) -> None:
    if member is None:
        member = interaction.user

    member_id = member.id
    await interaction.response.send_message(f"ID for {member.name}: {member_id}")


# --------------------------------------#
#                 SETUP                 #
# --------------------------------------#
async def setup(bot) -> None:
    await bot.add_cog(Summarize(bot))

# Main entry point
async def main() -> None:
    await setup(bot)
    await bot.start(TOKEN)

# --------------------------------------#
if __name__ == '__main__':
    asyncio.run(main())

# --------------------------------------#
# References
# 1. https://youtu.be/GX5Ez0hO_6k
