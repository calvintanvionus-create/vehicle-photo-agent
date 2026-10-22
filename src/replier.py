"""Builds the text of the reply posted in the channel (section 10)."""

import re

from .excel_log import DayCounts
from .validator import STATUS_NOT_VEHICLE, STATUS_OK, Analysis

LOW_CONFIDENCE_BELOW = 50
ERROR_REPLY = "Recognition failed, please send the photo again"

# Characters that Discord would turn into formatting, links or mentions.
_DISCORD_MARKUP = re.compile(r"[<>@`*_~|\[\]]")


def build_reply(status: str, analysis: Analysis | None, counts: DayCounts) -> str:
    if status == STATUS_OK and analysis is not None:
        return _vehicle_line(analysis) + "\n" + _today_line(counts)

    if status == STATUS_NOT_VEHICLE and analysis is not None:
        seen = _safe(analysis.description)
        detail = f" (I see: {seen})" if seen else ""
        return f"I couldn't find a car or motorcycle in this photo{detail}.\n" + _today_line(counts)

    return ERROR_REPLY


def is_low_confidence(confidence: int) -> bool:
    return confidence < LOW_CONFIDENCE_BELOW


def _vehicle_line(analysis: Analysis) -> str:
    if analysis.vehicle_type == "motorcycle":
        icon, kind = "🏍️", "Motorcycle"
    else:
        icon, kind = "🚗", "Car"

    parts = [f"{_safe(analysis.brand)} {_safe(analysis.model)}"]
    if analysis.body_type:
        parts.append(_safe(analysis.body_type))
    if analysis.estimated_year is not None:
        parts.append(f"about {analysis.estimated_year}")

    line = f"{icon} {kind}: {', '.join(parts)} ({analysis.confidence}% sure)"
    if is_low_confidence(analysis.confidence):
        line = f"🤔 I'm not sure, but my best guess: {line}"
    return line


def _today_line(counts: DayCounts) -> str:
    return (
        f"Today: {_count(counts.total, 'vehicle')} "
        f"({_count(counts.cars, 'car')}, {_count(counts.motorcycles, 'motorcycle')})"
    )


def _count(number: int, word: str) -> str:
    return f"{number} {word}" if number == 1 else f"{number} {word}s"


def _safe(text: str) -> str:
    return _DISCORD_MARKUP.sub("", text).strip()
