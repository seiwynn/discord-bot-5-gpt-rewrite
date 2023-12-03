import os
import discord
from discord import app_commands

from src.client import Client

from utils.logger import logger
from utils.fileio import read
from utils.message import send


def get_cli_with_cogs(token: str, prompt: str = "") -> discord.Client:

    client = Client(token=token, prompt=prompt)

    @client.event
    async def on_ready():
        # Replace GUILD_ID with the actual guild ID
        guild = discord.Object(id=os.getenv("TESTING_GUILD_ID"))
        await client.tree.sync(guild=guild)
        logger.info(
            f"Logged in as {client.user} and synced commands to guild ID {guild.id}"
        )
        client.current_channel = int(guild.id)

        # this will sync, but slower
        await client.tree.sync()

    @client.event
    async def on_message(message: discord.Message):
        # skip self (and other bots)
        # apparently you don't need to skip slash commands
        if (message.author == client.user) or message.author.bot:  # must use ==, not 'is'
            return

        # flags to identify source of message
        is_dm = not message.guild
        is_mentioned = client.user in message.mentions
        if message.reference:
            # type: discord.Message
            msg_replied = await message.channel.fetch_message(message.reference.message_id)

        # only handle dms and mentions
        if not (is_dm or is_mentioned):
            return

        client.log_interaction(
            called_method="on_message",
            content=message.content,
            user=message.author,
            channel=message.channel
        )

        # if there's a kafka message queue in the future, this is where it would go
        async with message.channel.typing():
            gpt_reply = await client.chat(message)
            if is_dm:
                await send(gpt_reply, message.channel.send)
            elif is_mentioned:
                await send(gpt_reply, message.reply)

    @client.tree.command(
        name="help",
        description="use guide"
    )
    async def help(interaction: discord.Interaction):
        # this should be relative to root directory
        help_doc_location = "assets/docs/help.md"
        help_message = read(help_doc_location)
        # ephemeral=True means hidden reply
        await interaction.response.defer(ephemeral=False)
        await send(help_message, callback=interaction.followup.send)

    @client.tree.command(
        name="reset",
        description="reset chat"
    )
    async def reset(interaction: discord.Interaction):
        client.chatbot.reset()
        logger.info(
            f"chat reset from slash command in channel {interaction.channel_id}")

    @client.tree.command(
        name="whisper",
        description="if you want to talk to me secretly, you can!"
    )
    async def whisper(interaction: discord.Interaction, *, content: str):
        # ephemeral=True means hidden reply
        await interaction.response.defer(ephemeral=True)

        client.log_interaction(
            called_method="/whisper",
            content=content,
            user=interaction.user,
            channel=interaction.channel
        )

        reply = await client.chat(content)
        reply = client.get_cmd_header(
            id=interaction.user.id,
            title=content
        ) + reply
        await send(reply, callback=interaction.followup.send)

    return client
