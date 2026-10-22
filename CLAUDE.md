# Vehicle Photo Agent

A Discord agent that identifies cars and motorcycles from photos using `claude -p`.

## Rules

- Always read `docs/architecture.md` before starting any work.
- Each of the four Guards (see section 12 of `docs/architecture.md`) must be wrapped in clear `START GUARD n` / `END GUARD n` comments. All four are enabled initially.
- Never commit `.env`.
- Never commit the photos or the Excel log in `DATA_DIR` (including `pending_rows.jsonl`).
