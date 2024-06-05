import os
from time import sleep

import psycopg2


def read_docker_secret(secret_name: str) -> str:
    """
    Reads a secret from Docker's secret management.

    Args:
        secret_name (str): name of the secret to read.

    Returns:
        str: the value of the secret.

    Raises:
        RuntimeError: if the secret file is not found.
    """
    secret_path = f"/run/secrets/{secret_name}"
    try:
        with open(secret_path, "r") as secret_file:
            secret = secret_file.read().strip()
        return secret
    except FileNotFoundError:
        raise RuntimeError(f"Secret {secret_name} not found")


def get_postgres_connection() -> psycopg2.extensions.connection:
    """
    Establishes a connection to a Postgres service

    Connects to the database using environment variables and Docker secrets.

    Returns:
        psycopg2.extensions.connection: the Postgres "connection" object.

    Raises:
        ConnectionError: if unable to connect to Postgres after 15 attempts.
    """
    print("Connecting to Postgres...")
    connection = None
    connection_attempts = 0
    while not connection:
        try:
            connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=read_docker_secret("db_password"),
                host=os.getenv("DB_HOST"),
                port="5432",
            )
        except psycopg2.OperationalError as e:
            # OperationalError will happen if the Postgres service is starting.
            # After 15 seconds, if the connection was not established, the error might
            # be on the parameters of either this or Postgre's container.
            print("Waiting for postgres to start...")
            connection_attempts += 1
            if connection_attempts == 15:
                raise ConnectionError(
                    "Could not connect to Postgres container after 15 attempts."
                )
            sleep(1)
    return connection


def close_postgres_connection(
    cursor: psycopg2.extensions.connection, connection: psycopg2.extensions.connection
) -> None:
    """
    Closes the given PostgreSQL cursor and connection.

    Args:
        cursor (psycopg2.extensions.cursor): Postgres cursor object.
        connection (psycopg2.extensions.connection): Postgres connection object.
    """
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
