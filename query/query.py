from common.tools import get_postgres_connection, close_postgres_connection

def main() -> None:
    # connecting to Postgres
    connection = get_postgres_connection()
    cursor = connection.cursor()

    # querying last 5 years of GDP in South America. Even though using a function like
    # crosstab is possible to make the query smaller and less repetitive, the current
    # approach is clearer and more easily understandable, without any significant loss
    # of performance.
    query = """
    SELECT
        c.id,
        c.name,
        c.iso3_code,
        MAX(CASE WHEN g.year = 2019 THEN g.value/1000000000 ELSE NULL END) AS "2019"
        MAX(CASE WHEN g.year = 2020 THEN g.value/1000000000 ELSE NULL END) AS "2020",
        MAX(CASE WHEN g.year = 2021 THEN g.value/1000000000 ELSE NULL END) AS "2021",
        MAX(CASE WHEN g.year = 2022 THEN g.value/1000000000 ELSE NULL END) AS "2022",
        MAX(CASE WHEN g.year = 2023 THEN g.value/1000000000 ELSE NULL END) AS "2023",
    FROM
        country c LEFT JOIN gdp g on c.id = g.country_id
    GROUP BY
        c.id, c.name, c.iso3_code
    ORDER BY
        c.id
    """

    # Saving as CSV
    output = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

    print("Querying database and generating CSV")

    with open("sa_gdp.csv", "w") as f:
        cursor.copy_expert(output, f)

    # Closing Postgres connection
    close_postgres_connection(cursor, connection)


if __name__ == "__main__":
    main()
