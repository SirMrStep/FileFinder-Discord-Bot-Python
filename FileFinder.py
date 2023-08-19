'''
    Packages used:        Version:
      discord.py            2.3.2
      python-dotenv         1.0.0

'''

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
@discord.app_commands.describe(wide_search="Make this 'true' to search the whole discord.")
@discord.app_commands.choices(wide_search=[discord.app_commands.Choice(name="true", value="true"), discord.app_commands.Choice(name="false", value="false")])
async def find(interaction: discord.Interaction, name: str, wide_search: str = "false"):

    await interaction.response.send_message(file=discord.File("./searching.png", filename="searching.png"),
        embed=discord.Embed(title="Searching...", description=f"Searching for {name}", color=discord.Color.yellow()).set_image(url="attachment://searching.png"), ephemeral=True)

    if wide_search == "true":
        messages = await fetch_all_messages(interaction.guild)
    else:
        messages = await fetch_all_messages(interaction.channel)

    matches: List[str] = []

    for message in messages:
        for attachment in message.attachments:
            try:
                if name.lower() in attachment.filename.lower():
                    matches.append("[" + attachment.filename + "](" + message.jump_url + ")")
            except Exception as e:
                continue

    if len(matches) < 1:
        await interaction.edit_original_response(attachments=[discord.File("./not-found.jpg", filename="not-found.jpg")], embed=
            discord.Embed(title="No files found with that name.", description=":shrug:",
                          color=discord.Color.red()).set_image(url="attachment://not-found.jpg"))
        return

    separator = ", "
    await interaction.edit_original_response(attachments=[discord.File("./found.jpg", filename="found.jpg")], embed=
        discord.Embed(title=f"Found {len(matches)} files:", description=f"{separator.join(matches)}",
                      color=discord.Color.green()).set_image(url="attachment://found.jpg"))


async def fetch_all_messages(guild_or_channel: discord.Guild | discord.TextChannel):

    messages: List[discord.Message] = []

    if type(guild_or_channel) is discord.Guild:

        for channel in guild_or_channel.channels:

            if type(channel) is discord.TextChannel:

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

    if type(guild_or_channel) is discord.TextChannel:

        message = None

        if guild_or_channel.last_message is not None: message = guild_or_channel.last_message
        if message is None:
            async for msg in guild_or_channel.history(limit=1): message = msg

        while message is not None:

            message_page = [_ async for _ in guild_or_channel.history(limit=100, before=message)]

            for msg in message_page: messages.append(msg)

            if len(message_page) > 0:
                message = message_page[len(message_page) - 1]
                continue

            message = None

    return messages


bot.run(discord_token)
