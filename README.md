# Calendarific API Client

This is a Python application that uses a script to retrie holiday calendar data from the [Calendarific API](https://calendarific.com/).

### Prerequisites
- [Poetry 1.6.1](https://python-poetry.org/docs/#installation) 
- [Python 3.11](https://www.python.org/downloads/)

### How to run locally

#### .env
Create the `.env` file, where sensitive variables, required to run the project, are placed:
```
cp .env.example .env
```
In order to be able to use the Calendarific API, fill in the OUTPUT_DIR with the proper directory name for the results and API_KEY parameter with the proper api key value.

#### poetry

In order to install needed requirements, run this inside the root directory:
```
poetry install
```
After successful installation, run, to activate the virtual environment:
```
poetry shell
```

#### Running tests

In order to run tests, run this inside the root directory:
```
pytest tests/
```

## Usage

To use the script, follow these steps:

1. Open your terminal or command prompt.

2. Navigate to the directory where the application is located.

3. Run the script with the following command:

    ```bash
    python calendarific.py --countries COUNTRY_CODES --start_year START_YEAR --start_month START_MONTH --start_day START_DAY --end_year END_YEAR --end_month END_MONTH --end_day END_DAY
    ```

    Replace the following placeholders with your specific input data:

    - `COUNTRY_CODES`: Provide one or more country codes separated by spaces.
    - `START_YEAR`, `START_MONTH`, `START_DAY`: Specify the start date of your desired date range. The year should be in the range 1800-2049, and months and days should be in the ranges 1-12 and 1-31, respectively.
    - `END_YEAR`, `END_MONTH`, `END_DAY`: Specify the end date of your desired date range. The year should be in the range 1800-2049, and months and days should be in the ranges 1-12 and 1-31, respectively.

4. The script will use your input parameters to retrieve holiday calendar data from the Calendarific API.

5. The retrieved data will be saved to the output directory specified in the script as `config.OUTPUT_DIR`.

## Example

Here's an example command to run the script:

```bash
python calendarific.py --countries ua us gb --start_year 1992 --start_month 7 --start_day 7 --end_year 1992 --end_month 9 --end_day 18
```
