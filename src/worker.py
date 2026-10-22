"""Takes photos from the queue one at a time and does everything for each (section 4)."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime

from . import analyzer, photo_store, replier, validator
from .config import Config
from .excel_log import DayCounts, ExcelLog
from .validator import STATUS_ERROR, STATUS_NOT_VEHICLE, STATUS_OK, Analysis

WAITING_REACTION = "⏳"
ATTEMPTS = 2  # the first run plus one retry; each run uses the owner's Claude allowance


@dataclass
class MessageGroup:
    """The photos of one Discord message. The ⏳ comes off when the last one is done."""

    message: object  # a discord.Message
    remaining: int


@dataclass
class QueueItem:
    group: MessageGroup
    attachment: object  # a discord.Attachment
    extension: str
    uploader_name: str
    uploader_id: int
    note: str  # the text the uploader typed; goes to the log only (Guard 2)
    message_link: str
    received_at: datetime = field(default_factory=datetime.now)


class Worker:
    def __init__(self, config: Config, excel: ExcelLog, counts: DayCounts, bot_user, analyze=analyzer.analyze):
        self.config = config
        self.excel = excel
        self.counts = counts
        self.bot_user = bot_user
        self.analyze = analyze
        self.queue: asyncio.Queue[QueueItem] = asyncio.Queue()

    def submit(self, item: QueueItem) -> None:
        self.queue.put_nowait(item)

    async def run_forever(self) -> None:
        """One photo at a time, forever. Nothing that goes wrong with one photo stops the loop."""
        while True:
            item = await self.queue.get()
            try:
                await self.process(item)
            except Exception as problem:  # the safety net: the bot must never crash
                print(f"ERROR while handling a photo ({type(problem).__name__}: {problem})")
            finally:
                self.queue.task_done()

    async def process(self, item: QueueItem) -> None:
        print(f"Analysing a photo from {item.uploader_name} ...")
        image_bytes = await self._download(item)

        status, analysis, reason = STATUS_ERROR, None, "could not download the photo"
        if image_bytes is not None:
            status, analysis, reason = await self._identify(item, image_bytes)

        today = item.received_at.date()
        self.counts.roll_to(today)
        if status == STATUS_OK and analysis is not None:
            self.counts.add(analysis.vehicle_type)

        photo_path = None
        if image_bytes is not None:
            photo_path = await asyncio.to_thread(
                photo_store.save_photo,
                self.config.photos_dir,
                item.received_at,
                status,
                analysis,
                image_bytes,
                item.extension,
            )

        row = self._build_row(item, status, analysis, reason, photo_path)
        await self.excel.append_row(row)

        await self._reply(item, replier.build_reply(status, analysis, self.counts))
        await self._finish_message(item)
        print(f"  -> {status}")

    async def _download(self, item: QueueItem) -> bytes | None:
        try:
            return await item.attachment.read()
        except Exception as problem:
            print(f"WARNING: could not download the photo ({type(problem).__name__})")
            return None

    async def _identify(self, item: QueueItem, image_bytes: bytes) -> tuple[str, Analysis | None, str]:
        """Ask claude -p (with one retry). Returns (status, analysis, reason for an error)."""
        reason = "unknown problem"
        for attempt in range(1, ATTEMPTS + 1):
            try:
                output = await self.analyze(self.config, image_bytes, item.extension, item.note)
                analysis = validator.parse_claude_output(output)
            except (analyzer.AnalysisFailed, validator.InvalidAnswer) as problem:
                reason = str(problem)
            except Exception as problem:  # anything unexpected is also just a failed attempt
                reason = f"unexpected problem ({type(problem).__name__})"
            else:
                status = STATUS_OK if analysis.is_vehicle else STATUS_NOT_VEHICLE
                return status, analysis, ""
            print(f"  attempt {attempt} of {ATTEMPTS} failed: {reason}")
        return STATUS_ERROR, None, reason

    def _build_row(self, item, status, analysis, reason, photo_path) -> dict:
        counts = self.counts
        row = {
            "Time": item.received_at,
            "Uploader name": item.uploader_name,
            "Uploader ID": str(item.uploader_id),  # text: Excel would round a number this long
            "Status": status,
            "Note": item.note,
            "Photo file": str(photo_path) if photo_path else "",
            "Discord message link": item.message_link,
            "Today's total": counts.total,
            "Today's cars": counts.cars,
            "Today's motorcycles": counts.motorcycles,
        }
        if status == STATUS_OK and analysis is not None:
            row.update(
                {
                    "Vehicle type": analysis.vehicle_type.capitalize(),
                    "Brand": analysis.brand,
                    "Model": analysis.model,
                    "Estimated year": analysis.estimated_year,
                    "Body type": analysis.body_type,
                    "Confidence": analysis.confidence,
                    "Low confidence": "Yes" if replier.is_low_confidence(analysis.confidence) else "",
                    "Description": analysis.description,
                }
            )
        elif status == STATUS_NOT_VEHICLE and analysis is not None:
            row.update({"Brand": "Not a vehicle", "Description": analysis.description})
        else:
            row["Description"] = reason
        return row

    async def _reply(self, item: QueueItem, text: str) -> None:
        # Imported here so the tests can run the worker without Discord installed.
        import discord

        try:
            await item.group.message.reply(
                text,
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except Exception as problem:
            print(f"WARNING: could not post the reply ({type(problem).__name__})")

    async def _finish_message(self, item: QueueItem) -> None:
        item.group.remaining -= 1
        if item.group.remaining > 0:
            return
        try:
            await item.group.message.remove_reaction(WAITING_REACTION, self.bot_user)
        except Exception as problem:
            print(f"WARNING: could not remove the {WAITING_REACTION} reaction ({type(problem).__name__})")
