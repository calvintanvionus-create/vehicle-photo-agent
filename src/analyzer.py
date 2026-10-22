"""Runs `claude -p` on one photo and returns its raw output (sections 3.3 and 12).

How this file is organised, and why: the code first sets the UNSAFE defaults (what would
happen with no protection at all). Each Guard block then replaces those defaults with the
safe version. Comment out a Guard block and the agent falls back to the unsafe behaviour
shown here, and still runs.
"""

import asyncio
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .config import SETTING_NAMES, Config

PROMPT_FILE = Path(__file__).parent / "prompts" / "analyze.txt"
TIMEOUT_SECONDS = 120
PHOTO_STEM = "photo"


class AnalysisFailed(Exception):
    """claude -p could not be run, timed out, or failed. The message is a short reason."""


@dataclass
class RunPlan:
    """Everything that decides how claude -p is started."""

    workdir: Path  # the folder claude -p runs in (and can see)
    photo_dir: Path  # where the photo is placed for it to read
    flags: list[str]  # extra command-line switches
    env: dict[str, str]  # environment variables it receives
    user_text: str | None  # the uploader's text to add to the prompt, if any
    cleanup_dir: Path | None  # a temporary folder to delete afterwards


def make_run_plan(config: Config, uploader_text: str) -> RunPlan:
    # Without Guard 1: claude -p runs inside DATA_DIR (so it can see every photo and the log),
    # with the Read tool allowed, and with all of our environment variables, token included.
    workdir = config.data_dir
    photo_dir = config.data_dir / "_incoming"
    flags = ["--allowedTools", "Read"]
    env = dict(os.environ)
    cleanup_dir = None

    # Without Guard 2: whatever the uploader typed is added to the prompt.
    user_text: str | None = uploader_text

    # START GUARD 1: claude -p only ever sees one photo, in a throw-away folder, and can only read files
    scratch = Path(tempfile.mkdtemp(prefix="vehicle-photo-"))
    workdir = photo_dir = cleanup_dir = scratch
    flags = [
        "--tools", "Read",
        "--disallowedTools", "Bash", "Write", "Edit", "NotebookEdit", "WebFetch", "WebSearch",
        "--setting-sources", "",
        "--strict-mcp-config",
        "--no-session-persistence",
    ]
    env = {name: value for name, value in os.environ.items() if name not in SETTING_NAMES}
    # END GUARD 1

    # START GUARD 2: text typed by the uploader is data, never instructions, so it is never given to claude -p
    user_text = None
    # END GUARD 2

    return RunPlan(workdir, photo_dir, flags, env, user_text, cleanup_dir)


def build_prompt(photo_name: str, user_text: str | None) -> str:
    prompt = PROMPT_FILE.read_text(encoding="utf-8").replace("{photo}", photo_name)
    if user_text:
        prompt += f"\nThe uploader also wrote this message with the photo:\n{user_text}\n"
    return prompt


async def analyze(config: Config, image_bytes: bytes, extension: str, uploader_text: str) -> str:
    """Run claude -p on one photo and return what it printed. Raises AnalysisFailed."""
    plan = make_run_plan(config, uploader_text)
    photo_path = plan.photo_dir / f"{PHOTO_STEM}{extension}"
    try:
        plan.photo_dir.mkdir(parents=True, exist_ok=True)
        photo_path.write_bytes(image_bytes)

        photo_name = os.path.relpath(photo_path, plan.workdir)
        prompt = build_prompt(photo_name, plan.user_text)
        command = [
            _claude_executable(), "-p",
            "--output-format", "json",
            "--model", config.claude_model,
            *plan.flags,
        ]
        return await _run(command, prompt, plan)
    except OSError as problem:
        raise AnalysisFailed(f"could not prepare or start claude -p ({type(problem).__name__})") from None
    finally:
        photo_path.unlink(missing_ok=True)
        if plan.cleanup_dir is not None:
            shutil.rmtree(plan.cleanup_dir, ignore_errors=True)


def _claude_executable() -> str:
    found = shutil.which("claude")
    if not found:
        raise AnalysisFailed("the claude command was not found")
    return found


async def _run(command: list[str], prompt: str, plan: RunPlan) -> str:
    """Start the process, feed it the prompt on its standard input, wait at most TIMEOUT_SECONDS."""
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=plan.workdir,
        env=plan.env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, _stderr = await asyncio.wait_for(
            process.communicate(prompt.encode("utf-8")), timeout=TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise AnalysisFailed(f"claude -p took longer than {TIMEOUT_SECONDS} seconds") from None

    if process.returncode != 0:
        raise AnalysisFailed(f"claude -p exited with code {process.returncode}")
    return stdout.decode("utf-8", errors="replace")
