# Cloudwalk technical challenge
## by Piero Desenzi

This software leverages Docker, Docker Compose, PostgreSQL and AirFlow to obtain the GDP of South American countries for the past 5 years.

## Installation

Assuming the user already has Docker installed with Docker Compose v2, the necessary steps are:

1) Install the requirements related to Airflow, by running on the project root:

```
pip install -r requirements.txt
```

2) Create a secret for the database connection, by:

    a) Creating a docker secret:
    ```
    echo "my_password" | docker secret create postgres_password -
    ```
    b) Inserting this value in `secrets/postgres_password.txt`, as explained on [the official Docker documentation for using secrets with Docker Compose](https://docs.docker.com/compose/use-secrets/).

3) Adding the project's DAG path to airflow.cfg, under dags_folder
```
[core]
# The folder where your airflow pipelines live, most likely a
# subfolder in a code repository. This path must be absolute.
#
# Variable: AIRFLOW__CORE__DAGS_FOLDER
#
dags_folder = /home/my_user/path_to_project/airflow/dags

```