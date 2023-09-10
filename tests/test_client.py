import tempfile

import pytest
import os
import json
from datetime import datetime

import requests

from calendarific import CalendarificClient
from custom_exceptions import ClientException
from parameters import CalendarParams, Country, StartDate, EndDate, Day, Month, Year


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def calendar_params(request):
    if hasattr(request, "param"):
        params = request.param
    else:
        params = {
            "country": "US",
            "start_year": 2021,
            "start_month": 1,
            "start_day": 1,
            "end_year": 2021,
            "end_month": 12,
            "end_day": 31,
        }

    return CalendarParams(
        countries=[Country(value=params["country"])],
        start_date=StartDate(
            year=Year(value=params["start_year"]),
            month=Month(value=params["start_month"]),
            day=Day(value=params["start_day"]),
        ),
        end_date=EndDate(
            year=Year(value=params["end_year"]),
            month=Month(value=params["end_month"]),
            day=Day(value=params["end_day"]),
        ),
    )


@pytest.mark.parametrize(
    "calendar_params",
    [
        {
            "country": "US",
            "start_year": 2021,
            "start_month": 1,
            "start_day": 1,
            "end_year": 2021,
            "end_month": 12,
            "end_day": 31,
        },
        {
            "country": "CA",
            "start_year": 1900,
            "start_month": 1,
            "start_day": 1,
            "end_year": 2049,
            "end_month": 12,
            "end_day": 31,
        },
    ],
    indirect=True,
)
def test_init(calendar_params):
    client = CalendarificClient(values=calendar_params)

    assert client.params == calendar_params.generate_params()
    assert client.input_data == calendar_params.get_input_data()
    assert client.dates == calendar_params.get_dates()
    assert client.session.headers["Accept"] == "application/json"


@pytest.mark.parametrize(
    "calendar_params, mocked_response",
    [
        (
            {
                "country": "US",
                "start_year": 2021,
                "start_month": 1,
                "start_day": 1,
                "end_year": 2021,
                "end_month": 12,
                "end_day": 31,
            },
            {"meta": {"code": 200}, "response": {"holidays": []}},
        ),
        (
            {
                "country": "CA",
                "start_year": 2022,
                "start_month": 1,
                "start_day": 1,
                "end_year": 2022,
                "end_month": 12,
                "end_day": 31,
            },
            {"meta": {"code": 200}, "response": {"holidays": []}},
        ),
    ],
    indirect=["calendar_params"],
)
def test_request(calendar_params, mocked_response, requests_mock):
    client = CalendarificClient(values=calendar_params)

    requests_mock.get(client.BASE_URL, json=mocked_response)

    response = client._request(url=client.BASE_URL, params=client.params[0])
    assert response == mocked_response


@pytest.mark.parametrize(
    "exception",
    [
        requests.HTTPError,
        requests.ConnectionError,
        requests.Timeout,
    ],
)
def test_request_error(exception, calendar_params, requests_mock):
    client = CalendarificClient(values=calendar_params)
    requests_mock.get(url=client.BASE_URL, exc=exception)

    with pytest.raises(ClientException):
        client._request(url=client.BASE_URL, params=client.params[0])


@pytest.mark.parametrize(
    "calendar_params, holidays, expected_holidays, start_date, end_date",
    [
        (
            {
                "country": "US",
                "start_year": 2021,
                "start_month": 3,
                "start_day": 1,
                "end_year": 2021,
                "end_month": 10,
                "end_day": 1,
            },
            [
                {"name": "New Year's Day", "date": {"iso": "2021-01-01"}},
                {"name": "Christmas Day", "date": {"iso": "2021-12-25"}},
                {"name": "Independence Day", "date": {"iso": "2021-07-04"}},
            ],
            [
                {"name": "Independence Day", "date": {"iso": "2021-07-04"}},
            ],
            datetime.strptime("2021-03-01", "%Y-%m-%d"),
            datetime.strptime("2021-10-01", "%Y-%m-%d"),
        ),
    ],
    indirect=["calendar_params"],
)
def test_parse_data(calendar_params, holidays, expected_holidays, start_date, end_date):
    client = CalendarificClient(values=calendar_params)
    client.dates = {"start_date": start_date, "end_date": end_date}

    result = client._parse_data(holidays=holidays)

    assert result == expected_holidays


@pytest.mark.parametrize(
    "calendar_params, mocked_response",
    [
        (
            {
                "country": "ua",
                "start_year": 1992,
                "start_month": 7,
                "start_day": 7,
                "end_year": 1992,
                "end_month": 9,
                "end_day": 18,
            },
            {
                "meta": {"code": 200},
                "response": {
                    "holidays": [
                        {
                            "name": "Independence Day",
                            "description":
                                "Ukraine’s Independence Day is annually celebrated on August 24 "
                                "to mark the anniversary of the country’s declaration of independence in 1991.",
                            "country": {"id": "ua", "name": "Ukraine"},
                            "date": {
                                "iso": "1992-08-24",
                                "datetime": {"year": 1992, "month": 8, "day": 24},
                            },
                            "type": ["National holiday"],
                            "primary_type": "National holiday",
                            "canonical_url": "https://calendarific.com/holiday/ukraine/independence-day",
                            "urlid": "ukraine/independence-day",
                            "locations": "All",
                            "states": "All",
                        }
                    ]
                },
            },
        )
    ],
    indirect=["calendar_params"],
)
def test_run(calendar_params, mocked_response, temp_dir, requests_mock):
    client = CalendarificClient(values=calendar_params)
    requests_mock.get(url=client.BASE_URL, json=mocked_response)

    output_dir = temp_dir

    client.run(output_dir=output_dir)

    file_name = "ua_7-7-1992_18-9-1992.txt"
    file_path = os.path.join(output_dir, file_name)

    assert os.path.isfile(file_path)

    with open(file_path, "r") as file:
        holidays = file.readlines()

    assert json.loads(holidays[0]) == mocked_response["response"]["holidays"][0]
