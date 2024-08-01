"""
Main module for Discord bot with GPT integration and various commands.
"""

import asyncio
import os
from typing import Final

import discord
from discord import Intents, Message, app_commands
from discord.ext import commands
from dotenv import load_dotenv

from responses import get_response_from_gpt

# Load the token from the environment
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Bot setup with intents
intents                 = Intents.default()
intents.message_content = True
bot                     = commands.Bot(command_prefix="/", intents=intents)

# --------------------------------------#
#              SEND MESSAGE             #
# --------------------------------------#
async def send_message_to_gpt(interaction: discord.Interaction, user_message: str) -> None:
    """
    Send a message to GPT and handle the response.

    Args:
        interaction (discord.Interaction): The interaction object.
        user_message (str): The user's message to process.
    """
    if not user_message:
        return

    # Check if the message is private
    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message[1:]

    response: str = get_response_from_gpt(user_message)
    if is_private:
        print(f'response: >> {response}')
        await interaction.user.send(response)
    else:
        print(f'response: >> {response}')
        await interaction.followup.send(response, ephemeral=False)

# Handling the startup for the bot
# --------------------------------------#
#               ON READY                #
# --------------------------------------#
@bot.event
async def on_ready() -> None:
    """Handle bot startup and command synchronization."""
    print(f'{bot.user} is now running!')
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except discord.HTTPException as e:
        print(f"HTTP error occurred while syncing commands: {e}")
    except discord.errors.DiscordException as e:
        print(f"Discord-related error occurred while syncing commands: {e}")

@bot.event
async def on_message(message: Message) -> None:
    """
    Handle incoming messages.

    Args:
        message (Message): The incoming message object.
    """
    if message.author == bot.user:
        return

    username     = str(message.author)
    user_message = message.content
    channel      = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message_to_gpt(message, user_message)

# --------------------------------------#
#             SLASH COMMANDS            #
# --------------------------------------#
# Command to reply with 'pong'
@bot.tree.command(name='ping', description='Replies with pong')
async def ping(interaction: discord.Interaction) -> None:
    """Simple ping command to check bot responsiveness."""
    await interaction.response.send_message(f'{interaction.user.mention} pong', ephemeral=True)

# --------------------------------------#
# Summarize command with three options
class Summarize(commands.Cog):
    """Cog for summarization-related commands."""

    def __init__(self, bot_instance):
        self.bot = bot_instance

    @app_commands.command(  name        ="last_messages",
                            description ="Summarize the last n messages from a user")
    @app_commands.describe( no_messages ="Provide the number of last messages to summarize",
                            user        ="The user to get the last n messages from")
    async def last_messages(self,
                            interaction: discord.Interaction,
                            no_messages: int,
                            user: discord.User) -> None:
        """
        Summarize the last n messages from a specific user.

        Args:
            interaction (discord.Interaction): The interaction object.
            no_messages (int): Number of messages to summarize.
            user (discord.User): The user whose messages to summarize.
        """
        await interaction.response.defer()  # Defer the response immediately

        messages = []
        async for message in interaction.channel.history(limit=None):
            if message.author == user:
                messages.append(message.content)
                if len(messages) == no_messages:
                    break

        if not messages:
            await interaction.followup.send(f"No messages found from {user.name}.", ephemeral=True)
            return

        messages.reverse()  # Reverse to get chronological order
        text_input = "\n".join(messages)

        await interaction.followup.send(
            f'Summarizing last {len(messages)} messages from {user.name}', ephemeral=True)
        await send_message_to_gpt(interaction, text_input)

    @app_commands.command(  name        ="text",
                            description ="Summarize the provided text")
    @app_commands.describe( text_input  ="Input text to summarize")
    async def text(self, interaction: discord.Interaction, text_input: str) -> None:
        """
        Summarize the provided text.

        Args:
            interaction (discord.Interaction): The interaction object.
            text_input (str): The text to summarize.
        """
        await interaction.response.defer()  # Acknowledge the interaction
        await send_message_to_gpt(interaction, text_input)

    @app_commands.command(  name        ="link",
                            description ="Summarize the provided link")
    @app_commands.describe( weblink     ="Weblink to summarize")
    async def link(self, interaction: discord.Interaction, weblink: str) -> None:
        """
        Summarize the content of a provided web link.

        Args:
            interaction (discord.Interaction): The interaction object.
            weblink (str): The web link to summarize.
        """
        await interaction.response.send_message(
            f'Summarizing the link: {weblink}', ephemeral=True)
        # TODO: Implement web scraping and summarization logic

@bot.tree.command(name="user_id", description='Sends the user ID for a given user.')
async def user_id(interaction: discord.Interaction, member: discord.Member = None) -> None:
    """
    Get the user ID for a given user or the command invoker.

    Args:
        interaction (discord.Interaction): The interaction object.
        member (discord.Member, optional): The member to get the ID for. Defaults to None.
    """
    if member is None:
        member = interaction.user

    member_id = member.id
    await interaction.response.send_message(f"ID for {member.name}: {member_id}")


# --------------------------------------#
#                 SETUP                 #
# --------------------------------------#
async def setup(bot) -> None:
    """Set up the bot by adding cogs."""
    await bot.add_cog(Summarize(bot))

async def main() -> None:
    """Main entry point for the bot."""
    await setup(bot)
    await bot.start(TOKEN)
# --------------------------------------#

if __name__ == '__main__':
    asyncio.run(main())

# References
# 1. https://youtu.be/GX5Ez0hO_6k