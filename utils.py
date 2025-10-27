from pathlib import Path
from discord.ext import commands

def get_main_file_path() -> Path:
    import __main__
    main_file = getattr(__main__, "__file__", None)
    if main_file:
        return Path(main_file).resolve()


async def read_all_quotes(client: commands.Bot, server_id: int, channel_id: int) -> list[str]:
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"Error: {server_id} - Quotes channel with ID {channel_id} not found.")
        return []

    messages = []
    async for message in channel.history(limit=None):
        # Send text content
        content = message.content or ""

        # Handle attachments (images, files, etc.)
        files = []
        for attachment in message.attachments:
            fp = await attachment.to_file()
            files.append(fp)

        # Handle embeds if you want (Discord limits re-sending foreign embeds)
        embeds = message.embeds if message.embeds else []

        messages.append((content, files, embeds))

    print(f'{server_id} - Found {len(messages)} messages in the quotes channel.')
    return messages
