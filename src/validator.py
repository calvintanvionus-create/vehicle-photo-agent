"""Checks claude -p's answer strictly (section 5 of docs/architecture.md).

Claude's answer is untrusted: it was shaped by a photo anyone could have faked. Nothing
leaves this file unless it has the exact shape we expect.
"""

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime

STATUS_OK = "OK"
STATUS_NOT_VEHICLE = "Not a vehicle"
STATUS_ERROR = "Error"

VEHICLE_TYPES = ("car", "motorcycle")
FIRST_YEAR = 1885
TEXT_LIMIT = 100
DESCRIPTION_LIMIT = 200


class InvalidAnswer(Exception):
    """The answer from claude -p cannot be used. The message is a short reason."""


@dataclass(frozen=True)
class Analysis:
    is_vehicle: bool
    vehicle_type: str  # "car" or "motorcycle"; "" when not a vehicle
    brand: str
    model: str
    estimated_year: int | None
    body_type: str
    confidence: int
    description: str


def parse_claude_output(stdout: str) -> Analysis:
    """Turn the raw output of `claude -p --output-format json` into a checked Analysis."""
    return validate_answer(_load_answer(_answer_text(stdout)))


def _answer_text(stdout: str) -> str:
    """Pull Claude's answer text out of the outer wrapper that claude -p prints."""
    if not stdout or not stdout.strip():
        raise InvalidAnswer("claude -p printed nothing")

    try:
        wrapper = json.loads(stdout)
    except ValueError:
        return stdout  # not a wrapper; maybe the answer itself

    if not isinstance(wrapper, dict):
        raise InvalidAnswer("claude -p output was not a JSON object")
    if wrapper.get("is_error"):
        raise InvalidAnswer("claude -p reported an error")
    if "is_vehicle" in wrapper:
        return stdout  # the answer itself, without a wrapper

    result = wrapper.get("result")
    if not isinstance(result, str) or not result.strip():
        raise InvalidAnswer("claude -p gave no answer text")
    return result


def _load_answer(text: str) -> dict:
    """Take the part between the first { and the last } and parse it as JSON."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise InvalidAnswer("answer contains no JSON")
    try:
        answer = json.loads(text[start : end + 1])
    except ValueError:
        raise InvalidAnswer("answer is not valid JSON") from None
    if not isinstance(answer, dict):
        raise InvalidAnswer("answer JSON is not an object")
    return answer


def validate_answer(answer: dict) -> Analysis:
    is_vehicle = answer.get("is_vehicle")
    if not isinstance(is_vehicle, bool):
        raise InvalidAnswer("is_vehicle must be true or false")

    confidence = _whole_number(answer.get("confidence"), "confidence")
    if not 0 <= confidence <= 100:
        raise InvalidAnswer("confidence must be between 0 and 100")

    description = _clean_text(answer.get("description"), DESCRIPTION_LIMIT)

    if not is_vehicle:
        return Analysis(False, "", "", "", None, "", confidence, description)

    vehicle_type = answer.get("vehicle_type")
    if not isinstance(vehicle_type, str) or vehicle_type.strip().lower() not in VEHICLE_TYPES:
        raise InvalidAnswer("vehicle_type must be car or motorcycle")

    brand = _clean_text(answer.get("brand"), TEXT_LIMIT)
    model = _clean_text(answer.get("model"), TEXT_LIMIT)
    if not brand or not model:
        raise InvalidAnswer("brand and model are required for a vehicle")

    year = _whole_number(answer.get("estimated_year"), "estimated_year")
    last_year = datetime.now().year + 1
    if not FIRST_YEAR <= year <= last_year:
        raise InvalidAnswer(f"estimated_year must be between {FIRST_YEAR} and {last_year}")

    return Analysis(
        is_vehicle=True,
        vehicle_type=vehicle_type.strip().lower(),
        brand=brand,
        model=model,
        estimated_year=year,
        body_type=_clean_text(answer.get("body_type"), TEXT_LIMIT),
        confidence=confidence,
        description=description,
    )


def _whole_number(value: object, name: str) -> int:
    """A real number, or text that converts cleanly to one. Rounded to a whole number."""
    if isinstance(value, bool):  # True/False are not numbers here
        raise InvalidAnswer(f"{name} must be a number")
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            raise InvalidAnswer(f"{name} must be a number") from None
    else:
        raise InvalidAnswer(f"{name} must be a number")

    if math.isnan(number) or math.isinf(number):
        raise InvalidAnswer(f"{name} must be a number")
    return round(number)


def _clean_text(value: object, limit: int) -> str:
    """Trim, flatten line breaks and control characters, and cut to a sensible length."""
    if not isinstance(value, str):
        return ""
    flat = re.sub(r"[\x00-\x1f\x7f\s]+", " ", value).strip()
    return flat[:limit].rstrip()
