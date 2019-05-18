import asyncio
import io
import logging
import os
import sys

import aiohttp
import discord
from discord import File

sys.path.append(os.getcwd())

from sof_client.protocol import SOFClientProtocol

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='../../logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

AUTH_TOKEN = 'NTcxNDYwMDMzNzk2Mzc0NTQz.XMOKAw.6ZB-CZ1XXOoRE8XrmHm3fP_PKuQ'
DEFAULT_EXTENSION = 'jpg'


async def process_image_data(url, file_name):
    try:
        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_connection(
            lambda: SOFClientProtocol(file_name, loop), '127.0.0.1', 8888)

        session = aiohttp.ClientSession()
        async with session.get(url) as resp:
            # Get a reference to the event loop as we plan to use
            # low-level APIs.
            payload = await resp.read()
            protocol.send_image(transport, payload)

        await session.close()
        processed_image = await protocol.get_processed_image()
        return processed_image

    except Exception:
        logger.exception("Failed to send img")


class ReactiveClient(discord.Client):
    async def on_message(self, message):
        if message.author == self.user:
            return

        if len(message.attachments):
            url = message.attachments[0].url
            id = message.attachments[0].id
            ext = DEFAULT_EXTENSION
            channel = message.channel

            file_name = "{}.{}".format(id, ext)

            img = await process_image_data(url, file_name)
            await channel.send("Bravo retarde", file=File(io.BytesIO(img),
                                                          filename="{}{}".format("processed_",
                                                                                 file_name)))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = ReactiveClient(loop=loop)

    try:
        client.run(AUTH_TOKEN)
    except KeyboardInterrupt:
        logger.info('Received signal to terminate bot and event loop.')
