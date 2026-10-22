"""The Discord side: receives messages, picks out photos, adds the ⏳, fills the queue."""

import asyncio
from pathlib import PurePosixPath

import discord

from .config import Config
from .excel_log import DayCounts, ExcelLog
from .worker import WAITING_REACTION, MessageGroup, QueueItem, Worker

NOTE_LIMIT = 1000

# Picture types the bot accepts, by the type Discord reports, and by file ending as a fallback.
IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
IMAGE_ENDINGS = {".jpg": ".jpg", ".jpeg": ".jpg", ".png": ".png", ".webp": ".webp", ".gif": ".gif"}


def image_extension(attachment) -> str | None:
    """The file ending to use if this attachment is a supported image, otherwise None."""
    content_type = (attachment.content_type or "").split(";")[0].strip().lower()
    if content_type in IMAGE_TYPES:
        return IMAGE_TYPES[content_type]
    if content_type and not content_type.startswith("image/"):
        return None  # Discord says it is not a picture (a PDF, a video, ...)
    return IMAGE_ENDINGS.get(PurePosixPath(attachment.filename or "").suffix.lower())


class VehicleBot(discord.Client):
    def __init__(self, config: Config, excel: ExcelLog, counts: DayCounts):
        intents = discord.Intents.default()
        intents.message_content = True  # must also be switched on in the Developer Portal
        super().__init__(intents=intents)
        self.config = config
        self.excel = excel
        self.counts = counts
        self.worker: Worker | None = None

    async def setup_hook(self) -> None:
        self.worker = Worker(self.config, self.excel, self.counts, bot_user=self.user)
        asyncio.create_task(self.worker.run_forever())

    async def on_ready(self) -> None:
        print(f"Connected to Discord as {self.user}. Listening to channel {self.config.channel_id}.")

    async def on_message(self, message: discord.Message) -> None:
        try:
            await self._handle(message)
        except Exception as problem:  # never let one message stop the bot
            print(f"ERROR while reading a message ({type(problem).__name__}: {problem})")

    async def _handle(self, message: discord.Message) -> None:
        if message.author.bot or message.channel.id != self.config.channel_id:
            return

        photos = [(a, image_extension(a)) for a in message.attachments]
        photos = [(attachment, ext) for attachment, ext in photos if ext]
        if not photos or self.worker is None:
            return

        try:
            await message.add_reaction(WAITING_REACTION)
        except Exception as problem:
            print(f"WARNING: could not add the {WAITING_REACTION} reaction ({type(problem).__name__})")

        group = MessageGroup(message=message, remaining=len(photos))
        for attachment, ext in photos:
            self.worker.submit(
                QueueItem(
                    group=group,
                    attachment=attachment,
                    extension=ext,
                    uploader_name=message.author.display_name,
                    uploader_id=message.author.id,
                    note=message.content[:NOTE_LIMIT],
                    message_link=message.jump_url,
                )
            )
