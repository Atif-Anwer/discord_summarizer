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
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

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

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

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
# Command with a group response
@bot.tree.command(name="summarize")
@app_commands.describe(no_messages="Last n Number of messages")
@app_commands.describe(txt="Text to summarize")
async def grp1(interaction: discord.Interaction, *, no_messages: str, txt: str) -> None:
    await interaction.response.send_message(f'Group 1 response: {no_messages}', ephemeral=True)


# --------------------------------------#
# Command to send the user ID
@bot.tree.command(name="user_id", description='Sends the user ID for a given user.')
async def user_id(interaction: discord.Interaction, member: discord.Member = None) -> None:
    if member is None:
        member = interaction.user

    member_id = member.id
    await interaction.response.send_message(f"ID for {member.name}: {member_id}")

# --------------------------------------#
# Example cog class
class Example(commands.Cog):
    @app_commands.command()
    async def example(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("This is an example command.", ephemeral=True)

# --------------------------------------#
#                 SETUP                 #
# --------------------------------------#
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Example())

# Main entry point
def main() -> None:
    bot.run(TOKEN)

# --------------------------------------#
if __name__ == '__main__':
    main()

# --------------------------------------#
# References
# 1. https://youtu.be/GX5Ez0hO_6k
