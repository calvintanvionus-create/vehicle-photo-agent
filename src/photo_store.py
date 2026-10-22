"""Saves each photo under DATA_DIR/photos/ with a file name built from the time, brand and model."""

from datetime import datetime
from pathlib import Path

from .validator import STATUS_NOT_VEHICLE, STATUS_OK, Analysis

NAME_PART_LIMIT = 40
UNKNOWN = "Unknown"
MAX_SAME_NAME = 1000


def save_photo(
    photos_dir: Path,
    received_at: datetime,
    status: str,
    analysis: Analysis | None,
    image_bytes: bytes,
    extension: str = ".jpg",
) -> Path | None:
    """Save the photo and return its path, or None if it could not be saved.

    Never raises: a problem with one photo must not stop the bot.
    """
    try:
        photos_dir.mkdir(parents=True, exist_ok=True)
        stem = _file_stem(photos_dir, received_at, status, analysis, extension)
        return _write_without_overwriting(photos_dir, stem, extension, image_bytes)
    except (OSError, ValueError) as problem:
        print(f"WARNING: could not save the photo ({type(problem).__name__}: {problem})")
        return None


def _file_stem(
    photos_dir: Path,
    received_at: datetime,
    status: str,
    analysis: Analysis | None,
    extension: str,
) -> str:
    """The file name without the extension, e.g. '2026-10-22 14-05-33 Toyota-Corolla'."""
    stamp = f"{received_at:%Y-%m-%d %H-%M-%S}"  # hyphens, not colons: Windows forbids colons

    if status == STATUS_NOT_VEHICLE:
        return f"{stamp} not-a-vehicle"
    if status != STATUS_OK or analysis is None:
        return f"{stamp} recognition-failed"

    # Without Guard 3 the brand and model from Claude go into the file name exactly as given.
    brand_part, model_part = analysis.brand, analysis.model

    # START GUARD 3: brand and model come from Claude (shaped by an untrusted photo), so they are cleaned before they go into a file name
    brand_part = clean_name_part(analysis.brand)
    model_part = clean_name_part(analysis.model)
    planned = (photos_dir / f"{stamp} {brand_part}-{model_part}{extension}").resolve()
    if not planned.is_relative_to(photos_dir.resolve()):
        brand_part, model_part = UNKNOWN, UNKNOWN
    # END GUARD 3

    return f"{stamp} {brand_part}-{model_part}"


def clean_name_part(value: str) -> str:
    """Keep only letters, digits and hyphens. Everything else becomes a hyphen."""
    kept = "".join(char if char.isalnum() else "-" for char in value)
    while "--" in kept:
        kept = kept.replace("--", "-")
    kept = kept.strip("-")[:NAME_PART_LIMIT].strip("-")
    return kept or UNKNOWN


def _write_without_overwriting(photos_dir: Path, stem: str, extension: str, data: bytes) -> Path:
    """Write to the first free name: stem.jpg, stem-2.jpg, stem-3.jpg ... Never overwrites."""
    for number in range(1, MAX_SAME_NAME + 1):
        suffix = "" if number == 1 else f"-{number}"
        path = photos_dir / f"{stem}{suffix}{extension}"
        try:
            with open(path, "xb") as handle:  # "x" = fail if the file already exists
                handle.write(data)
            return path
        except FileExistsError:
            continue
    raise OSError("too many photos with the same name")
