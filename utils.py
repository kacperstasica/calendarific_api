from datetime import datetime


def get_clean_dict(*, data: dict) -> dict:
    return {key: value for key, value in data.items() if value is not None}


def parse_date(*, iso_date: str) -> datetime:
    date_string: str = str(datetime.fromisoformat(iso_date))
    date: list[str] = date_string.split(" ")

    return datetime.strptime(date[0], "%Y-%m-%d")
