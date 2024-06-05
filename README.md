# Cloudwalk technical challenge
## by Piero Desenzi

This software leverages Docker, Docker Compose, PostgreSQL and Airflow to obtain the GDP of South American countries for the past 5 years.

It's steps are defined in an Airflow DAG:
1) Create a Docker network for the services to communicate between themselves
2) Using Docker Compose, create secrets, a volume, and three services:

    a) one for Postgres, which will create the database and the tables;

    b) one for the data extraction from the World Bank's API and upsertion into the database;

    c) one that will connect to Postgres and do the desired query, storing the result in a CSV file.

3) Copy the CSV from the container to the host machine
4) Bring down the Docker Compose services

Each Python container that is instantiated will have installed the contents of the respective folder's `requirements.txt` and the contents of the folder `common`, which has another `requirements.txt` and a file called `tools.py`, with functions that are used for database connection and secrets retrieval.

> Notes:
>
>1) `query/requirements.txt` is empty, but as a good practice, in name of standardization and being ready for possible future changes, it was kept there
>2) For the logging, `print()` was chosen instead of `logger` because the former does show up on the Docker logs


## Installation

Assuming the user already has Docker installed with Docker Compose v2, the necessary steps are:

1) Install the requirements related to Airflow, by running on the project root:

```
pip install -r requirements.txt
```

2) Initialize Airflow
```
airflow db migrate
```

3) Create an Airflow user
```
airflow users create \
    --username admin \
    --firstname FIRST_NAME \
    --lastname LAST_NAME \
    --role Admin \
    --email admin@example.com
```

4) Add the project's DAG path to airflow.cfg, under dags_folder
```
[core]
# The folder where your airflow pipelines live, most likely a
# subfolder in a code repository. This path must be absolute.
#
# Variable: AIRFLOW__CORE__DAGS_FOLDER
#
dags_folder = /home/my_user/path_to_project/airflow/dags

```
5) Create a secret for the database connection, by:

    a) Creating a Docker secret:
    ```
    echo "my_password" | docker secret create postgres_password -
    ```
    b) Inserting this value in `secrets/postgres_password.txt`, as explained on [the official Docker documentation for using secrets with Docker Compose](https://docs.docker.com/compose/use-secrets/).
    ```
    my_password
    ```


## Usage

1) Run Airflow and enter the Web UI
2) Start the "sa_gdp_dag" DAG
3) Collect the resulting CSV from the project's `result` folder