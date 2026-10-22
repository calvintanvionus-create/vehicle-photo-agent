"""Starts the Vehicle Photo Agent.  Run with:  uv run python -m src.main"""

import shutil
import sys
from datetime import datetime

import discord

from .config import ConfigError, load_config
from .discord_listener import VehicleBot
from .excel_log import ExcelLog


def main() -> int:
    # Names and descriptions can contain any character; never crash while printing them.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")

    try:
        config = load_config()
    except ConfigError as problem:
        print(f"Settings problem: {problem}")
        return 1

    try:
        config.photos_dir.mkdir(parents=True, exist_ok=True)
    except OSError as problem:
        print(f"Cannot create the DATA_DIR folder ({problem}).")
        return 1

    if shutil.which("claude") is None:
        print("WARNING: the 'claude' command was not found. Every photo will end as an Error row.")

    excel = ExcelLog(config.data_dir)
    counts = excel.rebuild_counts(datetime.now().date())
    print(
        f"Today so far: {counts.total} vehicles "
        f"({counts.cars} cars, {counts.motorcycles} motorcycles). Photos and log: {config.data_dir}"
    )

    bot = VehicleBot(config, excel, counts)
    try:
        bot.run(config.discord_token)
    except discord.LoginFailure:
        print("Discord login failed. Check DISCORD_TOKEN in .env (reset it in the Developer Portal if unsure).")
        return 1
    except discord.PrivilegedIntentsRequired:
        print("Message Content Intent is switched off. Turn it on in the Discord Developer Portal (Bot page).")
        return 1
    except KeyboardInterrupt:
        pass
    print("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
