import requests

from common.tools import get_postgres_connection, close_postgres_connection

def main() -> None:
    # connecting to Postgres
    connection = get_postgres_connection()
    cursor = connection.cursor()

    # getting data from API and organizing in a list of values. To populate the
    # database, the incoming data is from the year 2000 to 2024.
    print("Obtaining source data from API")
    result = requests.get(
        "https://api.worldbank.org/v2/country/ARG;BOL;BRA;CHL;COL;ECU;GUY;PRY;PER;SUR;"
        "URY;VEN/indicator/NY.GDP.MKTP.CD?format=json&page=1&per_page=300&date=2000:2024"
    ).json()

    entries = result[1:][0]
    data = [
        (
            entry["country"]["id"],
            entry["date"],
            entry["value"] if entry["value"] else "NULL",
        )
        for entry in entries
    ]

    # upserting "gdp" data based on (country_id, year). Only one entry is possible for
    # each pair country-year, but "value" may receive updates in the source database.
    print("Upserting data")
    upsert_sql = """
        INSERT INTO gdp (country_id, year, value)
        VALUES ('{}', {}, {})
        ON CONFLICT (country_id, year) DO UPDATE SET
        value = EXCLUDED.value;
    """

    for value in data:
        cursor.execute(upsert_sql.format(value[0], value[1], value[2]))

    connection.commit()

    # Closing Postgres connection
    close_postgres_connection(cursor, connection)


if __name__ == "__main__":
    main()
