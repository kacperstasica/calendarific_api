import copy
import os
import argparse
import json
from typing import Any, Generator

import config
import requests

from custom_exceptions import ClientException
from logger import logger
from parameters import CalendarParams, Day, EndDate, Month, StartDate, Year
from utils import get_clean_dict, parse_date


class CalendarificClient:
    BASE_URL = "https://calendarific.com/api/v2/holidays"

    def __init__(self, *, values: CalendarParams) -> None:
        self.params = values.generate_params()
        self.input_data = values.get_input_data()
        self.dates = values.get_dates()
        self.session = requests.Session()
        self.session.headers.update(**self.headers)

    def run(self, *, output_dir: str) -> None:
        self.write_holidays_to_files(output_dir=output_dir)

    def write_holidays_to_files(self, *, output_dir: str) -> None:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        for country_holidays in self.get_data():
            if not country_holidays:
                continue

            file_name = (
                f"{country_holidays[0]['country']['id']}"
                f"_{self.input_data['start_day']}"
                f"-{self.input_data['start_month']}"
                f"-{self.input_data['start_year']}"
                f"_{self.input_data['end_day']}"
                f"-{self.input_data['end_month']}"
                f"-{self.input_data['end_year']}.txt"
            )
            file_path = os.path.join(output_dir, file_name)

            try:
                with open(file_path, "w") as file:
                    for holiday in country_holidays:
                        holiday_json = json.dumps(holiday)
                        file.write(holiday_json + "\n")
                logger.info(f"Holidays written to {file_path}")
            except Exception as e:
                logger.error(f"Error writing holidays to file: {e}")

    def get_data(self) -> Generator[list[dict[str, Any]], None, None]:
        for country in self.input_data["countries"]:
            response_data: list[dict] = []

            for country_data in self.params:
                if country_data["country"] == country:
                    clean_country_data: dict[str, str] = get_clean_dict(
                        data=country_data
                    )
                    response = self._request(
                        url=self.api_url, params={**clean_country_data}
                    )

                    if (
                        response["meta"]["code"] == 200
                        and response["response"]["holidays"]
                    ):
                        response_data.extend(
                            self._parse_data(holidays=response["response"]["holidays"])
                        )

            yield response_data

    def _request(self, *, url: str, params: dict) -> dict:
        try:
            response = self.session.get(url=url, params=params)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise ClientException(f"Error: {e}")

    def _parse_data(self, *, holidays: list[dict]) -> list[dict]:
        for holiday in copy.deepcopy(holidays):
            date = parse_date(iso_date=holiday["date"]["iso"])
            if date < self.dates["start_date"] or date > self.dates["end_date"]:
                holidays.remove(holiday)

        return holidays

    @property
    def api_url(self) -> str:
        return f"{self.BASE_URL}?api_key={config.API_KEY}"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "User-Agent": "application/json",
            "Accept": "application/json",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get Holiday calendar input_data from the Calendarific API."
    )
    parser.add_argument(
        "--countries", nargs="+", required=True, help="the countries codes"
    )
    parser.add_argument("--start_year", type=int, required=True, help="the start year")
    parser.add_argument(
        "--start_month", type=int, required=True, help="the start month"
    )
    parser.add_argument("--start_day", type=int, required=True, help="the start day")
    parser.add_argument("--end_year", type=int, required=True, help="the end year")
    parser.add_argument("--end_month", type=int, required=True, help="the end month")
    parser.add_argument("--end_day", type=int, required=True, help="the end day")
    args = parser.parse_args()

    client = CalendarificClient(
        values=CalendarParams(
            countries=args.countries,
            start_date=StartDate(
                year=Year(value=args.start_year),
                month=Month(value=args.start_month),
                day=Day(value=args.start_day),
            ),
            end_date=EndDate(
                year=Year(value=args.end_year),
                month=Month(value=args.end_month),
                day=Day(value=args.end_day),
            ),
        )
    )
    client.run(output_dir=config.OUTPUT_DIR)
