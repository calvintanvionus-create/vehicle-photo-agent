from datetime import datetime

import pytest

from src.photo_store import clean_name_part, save_photo
from src.validator import STATUS_ERROR, STATUS_NOT_VEHICLE, STATUS_OK, Analysis

WHEN = datetime(2026, 10, 22, 14, 5, 33)


def vehicle(brand="Toyota", model="Corolla"):
    return Analysis(True, "car", brand, model, 2015, "sedan", 85, "")


def test_file_name_rule(tmp_path):
    path = save_photo(tmp_path / "photos", WHEN, STATUS_OK, vehicle(), b"x")
    assert path.name == "2026-10-22 14-05-33 Toyota-Corolla.jpg"
    assert path.read_bytes() == b"x"


def test_name_never_contains_colons_in_the_time(tmp_path):
    assert ":" not in save_photo(tmp_path, WHEN, STATUS_OK, vehicle(), b"x").name


def test_same_second_same_name_gets_2_then_3_and_nothing_is_overwritten(tmp_path):
    names = [save_photo(tmp_path, WHEN, STATUS_OK, vehicle(), bytes([n])).name for n in range(3)]
    assert names == [
        "2026-10-22 14-05-33 Toyota-Corolla.jpg",
        "2026-10-22 14-05-33 Toyota-Corolla-2.jpg",
        "2026-10-22 14-05-33 Toyota-Corolla-3.jpg",
    ]
    assert (tmp_path / names[0]).read_bytes() == b"\x00"


def test_special_names_for_non_vehicle_and_error(tmp_path):
    assert save_photo(tmp_path, WHEN, STATUS_NOT_VEHICLE, None, b"x").name.endswith(" not-a-vehicle.jpg")
    assert save_photo(tmp_path, WHEN, STATUS_ERROR, None, b"x").name.endswith(" recognition-failed.jpg")


def test_unknown_brand_or_model_name(tmp_path):
    path = save_photo(tmp_path, WHEN, STATUS_OK, vehicle("Honda", "///"), b"x")
    assert path.name == "2026-10-22 14-05-33 Honda-Unknown.jpg"


def test_other_extensions_are_kept(tmp_path):
    assert save_photo(tmp_path, WHEN, STATUS_OK, vehicle(), b"x", ".png").name.endswith(".png")


def test_a_problem_saving_returns_none_instead_of_crashing(tmp_path):
    blocker = tmp_path / "photos"
    blocker.write_text("a file where the folder should be")
    assert save_photo(blocker, WHEN, STATUS_OK, vehicle(), b"x") is None


@pytest.mark.parametrize(
    "dirty, clean",
    [
        ("Corolla Cross", "Corolla-Cross"),
        ("../../x", "x"),
        ("a:b", "a-b"),
        ("Kia/Rio\\x", "Kia-Rio-x"),
        ('CON<>:"|?*', "CON"),
        ("..", "Unknown"),
        ("", "Unknown"),
        ("🚗🚗", "Unknown"),
        ("  --Mazda  MX-5--  ", "Mazda-MX-5"),
        ("a" * 100, "a" * 40),
        ("豐田", "豐田"),
    ],
)
def test_clean_name_part(dirty, clean):
    assert clean_name_part(dirty) == clean
