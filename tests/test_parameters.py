import pytest

from datetime import datetime

from custom_exceptions import InvalidInputData
from parameters import (
    Year,
    Month,
    Day,
    StartDate,
    EndDate,
    Country,
    CalendarParams,
)


def test_year_valid_input():
    year = Year(value=2021)

    assert year.value == 2021


def test_year_invalid_input(caplog):
    with pytest.raises(InvalidInputData):
        Year(value=2050)

        assert "Year must be between 1800 and 2049" in caplog.text


def test_country_valid_input():
    country = Country(value="US")

    assert country.value == "US"


def test_country_invalid_input(caplog):
    with pytest.raises(InvalidInputData):
        Country(value="USA")

        assert "Country must be a valid ISO-3166 code" in caplog.text


def test_day_valid_input():
    day = Day(value=1)

    assert day.value == 1


def test_day_invalid_input(caplog):
    with pytest.raises(InvalidInputData):
        Day(value=32)

        assert "Day must be in the range [1, 31]" in caplog.text


def test_month_valid_input():
    month = Month(value=1)

    assert month.value == 1


def test_month_invalid_input(caplog):
    with pytest.raises(InvalidInputData):
        Month(value=13)

        assert "Month must be in the range [1, 12]" in caplog.text


def test_start_date_valid_input():
    start_date = StartDate(Year(value=2021), Month(value=1), Day(value=1))

    assert start_date.date == datetime(2021, 1, 1)


def test_start_date_invalid_input(caplog):
    with pytest.raises(InvalidInputData):
        StartDate(Year(value=2050), Month(value=2), Day(value=31))

        assert "Invalid start date: day is out of range for month" in caplog.text


def test_end_date_valid_input():
    end_date = EndDate(Year(value=2021), Month(value=1), Day(value=1))

    assert end_date.date == datetime(2021, 1, 1)


def test_end_date_invalid_input(caplog):
    with pytest.raises(InvalidInputData):
        EndDate(Year(2050), Month(1), Day(1))

        assert "Invalid end date" in caplog.text


def test_start_date_greater_than_end_date(caplog):
    with pytest.raises(InvalidInputData):
        CalendarParams(
            countries=[Country(value="US")],
            start_date=StartDate(Year(2021), Month(1), Day(2)),
            end_date=EndDate(Year(2021), Month(1), Day(1)),
        )

        assert "Start date must be before end date" in caplog.text


def test_calendar_params_generate_params():
    start_date = StartDate(Year(2021), Month(1), Day(1))
    end_date = EndDate(Year(2021), Month(1), Day(3))
    calendar_params = CalendarParams([Country("US")], start_date, end_date)
    params_list = calendar_params.generate_params()

    assert params_list == [
        {"country": Country(value="US"), "day": 1, "month": 1, "year": 2021},
        {"country": Country(value="US"), "day": 2, "month": 1, "year": 2021},
        {"country": Country(value="US"), "day": 3, "month": 1, "year": 2021},
    ]


def test_calendar_params_get_input_data():
    start_date = StartDate(Year(value=2021), Month(value=1), Day(value=1))
    end_date = EndDate(Year(value=2021), Month(value=1), Day(value=3))
    calendar_params = CalendarParams([Country("US")], start_date, end_date)
    input_data = calendar_params.get_input_data()

    assert input_data == {
        "countries": [Country(value="US")],
        "end_day": 3,
        "end_month": 1,
        "end_year": 2021,
        "start_day": 1,
        "start_month": 1,
        "start_year": 2021,
    }


def test_calendar_params_get_dates():
    start_date = StartDate(Year(value=2021), Month(value=1), Day(value=1))
    end_date = EndDate(Year(value=2021), Month(value=1), Day(value=3))
    calendar_params = CalendarParams([Country("US")], start_date, end_date)
    dates = calendar_params.get_dates()

    assert dates["start_date"] == datetime(2021, 1, 1)
    assert dates["end_date"] == datetime(2021, 1, 3)
