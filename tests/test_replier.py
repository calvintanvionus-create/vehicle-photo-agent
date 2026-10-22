from datetime import date

from src.excel_log import DayCounts
from src.replier import ERROR_REPLY, build_reply
from src.validator import STATUS_ERROR, STATUS_NOT_VEHICLE, STATUS_OK, Analysis

COUNTS = DayCounts(day=date(2026, 10, 22), total=12, cars=9, motorcycles=3)


def car(confidence=85, **changes):
    values = dict(is_vehicle=True, vehicle_type="car", brand="Toyota", model="Corolla",
                  estimated_year=2015, body_type="sedan", confidence=confidence, description="")
    values.update(changes)
    return Analysis(**values)


def test_car_reply_has_every_field_and_todays_totals():
    assert build_reply(STATUS_OK, car(), COUNTS) == (
        "🚗 Car: Toyota Corolla, sedan, about 2015 (85% sure)\n"
        "Today: 12 vehicles (9 cars, 3 motorcycles)"
    )


def test_motorcycle_reply():
    text = build_reply(STATUS_OK, car(vehicle_type="motorcycle", brand="Honda", model="CB500F"), COUNTS)
    assert text.startswith("🏍️ Motorcycle: Honda CB500F")


def test_low_confidence_wording_below_50_only():
    assert build_reply(STATUS_OK, car(confidence=42), COUNTS).startswith("🤔 I'm not sure, but my best guess: 🚗 Car:")
    assert "not sure" not in build_reply(STATUS_OK, car(confidence=50), COUNTS)


def test_not_a_vehicle_reply_includes_what_was_seen_and_totals():
    analysis = Analysis(False, "", "", "", None, "", 90, "bus")
    assert build_reply(STATUS_NOT_VEHICLE, analysis, COUNTS) == (
        "I couldn't find a car or motorcycle in this photo (I see: bus).\n"
        "Today: 12 vehicles (9 cars, 3 motorcycles)"
    )


def test_error_reply_is_the_exact_wording_without_totals():
    assert build_reply(STATUS_ERROR, None, COUNTS) == "Recognition failed, please send the photo again"
    assert ERROR_REPLY == "Recognition failed, please send the photo again"


def test_singular_words():
    one = DayCounts(day=date(2026, 10, 22), total=1, cars=1, motorcycles=0)
    assert build_reply(STATUS_OK, car(), one).endswith("Today: 1 vehicle (1 car, 0 motorcycles)")


def test_discord_markup_and_mentions_are_removed_from_claudes_words():
    text = build_reply(STATUS_OK, car(brand="@everyone", model="[click](http://x) <@123>"), COUNTS)
    assert "@" not in text and "<" not in text and "[" not in text
