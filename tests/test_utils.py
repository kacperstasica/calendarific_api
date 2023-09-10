from datetime import datetime

import pytest
from utils import get_clean_dict, parse_date


@pytest.mark.parametrize(
    "input_dict, expected_result",
    [
        ({"a": 1, "b": None, "c": 3, "d": None}, {"a": 1, "c": 3}),
        ({}, {}),
        ({"x": 10, "y": 20, "z": 30}, {"x": 10, "y": 20, "z": 30}),
        (
            {"name": "John", "age": 30, "city": None, "active": True, "address": None},
            {"name": "John", "age": 30, "active": True},
        ),
        (
            {"countries": ["ua"], "start_year": 1992, "month": None, "day": None},
            {"countries": ["ua"], "start_year": 1992},
        ),
    ],
)
def test_get_clean_dict(input_dict, expected_result):
    cleaned_dict = get_clean_dict(data=input_dict)

    assert cleaned_dict == expected_result


@pytest.mark.parametrize(
    "date_string, expected_date",
    [
        ("2023-09-10T12:34:56", datetime(2023, 9, 10)),
        ("2022-03-15T10:00:00", datetime(2022, 3, 15)),
        ("2021-12-31T23:59:59", datetime(2021, 12, 31)),
        ("2020-01-01T00:00:00", datetime(2020, 1, 1)),
        ("2020-01-21", datetime(2020, 1, 21)),
    ],
)
def test_parse_date(date_string, expected_date):
    parsed_date = parse_date(iso_date=date_string)

    assert parsed_date == expected_date
