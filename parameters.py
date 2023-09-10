from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Any

from custom_exceptions import InvalidInputData

# Arbitrary limits to avoid making too many requests
DAY_LIMIT = 3
MONTH_LIMIT_IN_DAYS = 90


@dataclass
class Year:
    value: int

    def __post_init__(self) -> None:
        if not (1800 <= self.value <= 2049):
            raise InvalidInputData("Year must be between 1800 and 2049")


@dataclass
class Country:
    value: str

    def __post_init__(self) -> None:
        if not self._is_valid_iso_3166_code(code=self.value):
            raise InvalidInputData(
                "Country must be a valid ISO-3166 code (a string of exactly 2 letters)."
            )

        self.value = self.value.upper()

    @staticmethod
    def _is_valid_iso_3166_code(*, code: str) -> bool:
        """
        Validation function to check if the code is valid ISO-3166 code.

        :param code: The country code to validate (a string of exactly 2 uppercase letters).
        :return: True if the code is valid; False otherwise.
        """
        return len(code) == 2 and code.isalpha()


@dataclass
class Day:
    value: int

    def __post_init__(self) -> None:
        if not (1 <= self.value <= 31):
            raise InvalidInputData("Day must be in the range [1, 31]")


@dataclass
class Month:
    value: int

    def __post_init__(self) -> None:
        if not (1 <= self.value <= 12):
            raise InvalidInputData("Month must be in the range [1, 12]")


@dataclass
class StartDate:
    year: Year
    month: Month
    day: Day

    def __post_init__(self) -> None:
        try:
            self.date: datetime = datetime(
                year=self.year.value, month=self.month.value, day=self.day.value
            )
        except ValueError as e:
            raise InvalidInputData(f"Invalid start date: {e}")


@dataclass
class EndDate:
    year: Year
    month: Month
    day: Day

    def __post_init__(self) -> None:
        try:
            self.date: datetime = datetime(
                year=self.year.value, month=self.month.value, day=self.day.value
            )
        except ValueError as e:
            raise InvalidInputData(f"Invalid end date: {e}")


@dataclass
class CalendarParams:
    countries: list[Country]
    start_date: StartDate
    end_date: EndDate

    def __post_init__(self) -> None:
        if self.start_date.date > self.end_date.date:
            raise InvalidInputData("Start date must be before end date")

    def generate_params(self) -> list[dict[str, Any]]:
        params_list = []
        seen_params = set()
        start_date = self.start_date.date
        end_date = self.end_date.date
        days_diff: int = (end_date - start_date).days

        for country in self.countries:
            current_date = start_date
            while current_date <= end_date:
                country_params = {
                    "country": country,
                    "year": current_date.year,
                    "month": current_date.month
                    if days_diff <= MONTH_LIMIT_IN_DAYS
                    else None,
                    "day": current_date.day if days_diff <= DAY_LIMIT else None,
                }

                param_str = str(country_params)
                if param_str not in seen_params:
                    params_list.append(country_params)
                    seen_params.add(param_str)

                current_date += timedelta(days=1)

        return params_list

    def get_input_data(self) -> dict[str, Any]:
        return {
            "countries": self.countries,
            "start_year": self.start_date.year.value,
            "start_month": self.start_date.month.value,
            "start_day": self.start_date.day.value,
            "end_year": self.end_date.year.value,
            "end_month": self.end_date.month.value,
            "end_day": self.end_date.day.value,
        }

    def get_dates(self) -> dict[str, datetime]:
        return {
            "start_date": self.start_date.date,
            "end_date": self.end_date.date,
        }
