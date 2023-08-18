import os
import discord
from typing import List
from dotenv import load_dotenv

load_dotenv("./token.env")
bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
discord_token = os.getenv("token")


@bot.event
async def on_ready():

    try:
        for guild in bot.guilds:
            tree.copy_global_to(guild=guild)
            await tree.sync(guild=guild)
    except Exception as e:
        print(e)
    print(bot.user.name + " is ready.")


@tree.command(name="find", description="Find an attachment by name.")
@discord.app_commands.describe(name="The name of the Attachment to look for.")
async def find(interaction: discord.Interaction, name: str):

    messages = await fetch_all_messages(interaction.channel)
    matches: List[str] = []

    for message in messages:
        for attachment in message.attachments:
            if name.lower() in attachment.filename.lower():
                matches.append("[" + attachment.filename + "](" + message.jump_url + ")")

    if len(matches) < 1:
        await interaction.response.send_message(embeds=[
            discord.Embed(title="No files found with that name.", description=":shrug:",
                          color=discord.Color.red())])
        return

    separator = ", "
    await interaction.response.send_message(embeds=[
        discord.Embed(title=f"Found {len(matches)} files:", description=f"{separator.join(matches)}",
                      color=discord.Color.green())])


async def fetch_all_messages(channel: discord.TextChannel):
    messages: List[discord.Message] = []
    message = None

    if channel.last_message is not None: message = channel.last_message
    if message is None:
        async for msg in channel.history(limit=1): message = msg

    while message is not None:

        message_page = [_ async for _ in channel.history(limit=100, before=message)]

        for msg in message_page: messages.append(msg)

        if len(message_page) > 0:
            message = message_page[len(message_page) - 1]
            continue

        message = None

    return messages


bot.run(discord_token)
