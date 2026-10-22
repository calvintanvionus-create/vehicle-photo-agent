import json

import pytest

from src.validator import InvalidAnswer, parse_claude_output

GOOD = {
    "is_vehicle": True,
    "vehicle_type": "car",
    "brand": "Toyota",
    "model": "Corolla",
    "estimated_year": 2015,
    "body_type": "sedan",
    "confidence": 85,
    "description": "Silver sedan on a street",
}


def wrapped(answer, **extra):
    """What `claude -p --output-format json` prints: an outer object holding the answer as text."""
    text = answer if isinstance(answer, str) else json.dumps(answer)
    return json.dumps({"type": "result", "is_error": False, "result": text, **extra})


def test_good_vehicle_answer():
    result = parse_claude_output(wrapped(GOOD))
    assert result.is_vehicle and result.vehicle_type == "car"
    assert (result.brand, result.model, result.estimated_year) == ("Toyota", "Corolla", 2015)
    assert result.confidence == 85


def test_answer_inside_a_code_block_and_extra_words_is_accepted():
    text = "Here you go:\n```json\n" + json.dumps(GOOD) + "\n```\nHope that helps"
    assert parse_claude_output(wrapped(text)).brand == "Toyota"


def test_not_a_vehicle():
    answer = {"is_vehicle": False, "vehicle_type": None, "estimated_year": None, "confidence": 90,
              "description": "a bus"}
    result = parse_claude_output(wrapped(answer))
    assert not result.is_vehicle and result.description == "a bus" and result.estimated_year is None


def test_numbers_as_clean_text_are_accepted_and_rounded():
    result = parse_claude_output(wrapped({**GOOD, "confidence": "72.6", "estimated_year": "2015"}))
    assert (result.confidence, result.estimated_year) == (73, 2015)


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        "   ",
        "not json at all",
        "[1, 2, 3]",
        json.dumps({"is_error": True, "result": "boom"}),
        json.dumps({"result": 5}),
        wrapped("I could not tell what this is."),
        wrapped("{broken json"),
        wrapped("[1, 2]"),
    ],
)
def test_unusable_output_is_rejected_not_crashing(stdout):
    with pytest.raises(InvalidAnswer):
        parse_claude_output(stdout)


@pytest.mark.parametrize(
    "change",
    [
        {"confidence": "high"},
        {"confidence": None},
        {"confidence": True},
        {"confidence": float("nan")},
        {"confidence": 101},
        {"confidence": -1},
        {"estimated_year": "unknown"},
        {"estimated_year": "2010s"},
        {"estimated_year": None},
        {"estimated_year": True},
        {"estimated_year": 1700},
        {"estimated_year": 3000},
        {"is_vehicle": "yes"},
        {"is_vehicle": None},
        {"vehicle_type": "truck"},
        {"vehicle_type": None},
        {"brand": ""},
        {"model": None},
    ],
)
def test_bad_fields_are_rejected(change):
    with pytest.raises(InvalidAnswer):
        parse_claude_output(wrapped({**GOOD, **change}))


def test_missing_confidence_is_rejected_even_for_non_vehicles():
    with pytest.raises(InvalidAnswer):
        parse_claude_output(wrapped({"is_vehicle": False, "description": "a cat"}))


def test_text_is_flattened_trimmed_and_cut_and_extra_fields_dropped():
    answer = {**GOOD, "brand": "  Toy\nota\t", "description": "x" * 1000, "evil": "rm -rf"}
    result = parse_claude_output(wrapped(answer))
    assert result.brand == "Toy ota"
    assert len(result.description) == 200
    assert not hasattr(result, "evil")
