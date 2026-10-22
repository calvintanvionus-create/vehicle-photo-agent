# Vehicle Photo Agent

A Discord agent that identifies cars and motorcycles from photos using `claude -p`. Post a photo in one channel and the bot replies with the vehicle type, brand, model, approximate year and body type, and adds a row to an Excel file.

How it is built and why: `docs/architecture.md` (read this first). The original wish list: `docs/requirements.md`.

## Set up (Windows)

1. Create your Discord server, channel and bot: follow `docs/discord-server-setup.md` and then `docs/discord-bot-setup.md`.
2. Install [uv](https://docs.astral.sh/uv/) and Claude Code, and log in to Claude Code once by running `claude` in a terminal.
3. In this folder, install the packages: `uv sync`
4. Copy `.env.example` to a new file called `.env` and fill in the four values:
   - `DISCORD_TOKEN`: the bot token. **Never share it, paste it into a chat, or commit it.**
   - `CHANNEL_ID`: the channel the bot listens to.
   - `CLAUDE_MODEL`: the Claude model for `claude -p` (for example `sonnet`).
   - `DATA_DIR`: a folder outside this project for the photos and the Excel log.

## Run

```
uv run python -m src.main
```

Leave the window open while the bot is working. Press Ctrl+C to stop it. Photos posted while the bot is off are ignored.

You will find the results in `DATA_DIR`:

- `photos/` the saved photos
- `vehicle_log.xlsx` the log (one row per photo, new rows are added at the bottom)
- `pending_rows.jsonl` only appears if the Excel file was open and rows had to wait; they are added automatically later

If you keep `vehicle_log.xlsx` open in Excel, the bot prints a warning and retries, then keeps the row in the backup file. Close Excel and it catches up on the next photo.

## Test

```
uv run pytest
```

## The four security Guards

The code for each Guard sits between `# START GUARD n` and `# END GUARD n` comments:

| Guard | File | What it does |
|---|---|---|
| 1 | `src/analyzer.py` | `claude -p` sees one photo in a throw-away folder, can only read, and gets no secrets |
| 2 | `src/analyzer.py` | Text typed by the uploader is never passed to `claude -p` |
| 3 | `src/photo_store.py` | Brand and model are cleaned before they become part of a file name |
| 4 | `src/excel_log.py` | Text starting with `=`, `+`, `-` or `@` is stored as plain text in Excel |

For the class demo, comment out a whole block (select the lines between the markers and press Ctrl+/ in your editor). The agent still runs and falls back to the unsafe behaviour: `claude -p` runs inside `DATA_DIR` with the Read tool allowed, the uploader's text is added to the prompt, the raw brand is used in file names, and formulas go into Excel as formulas. `tests/test_guards_off.py` checks this for all four Guards.
