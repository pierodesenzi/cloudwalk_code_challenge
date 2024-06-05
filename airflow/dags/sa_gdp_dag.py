from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

# Get the absolute path of the software
base_directory = Path(__file__).resolve().parent.parent.parent

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# defing DAG
dag = DAG(
    "sa_gdp_dag",
    default_args=default_args,
    description="DAG for obtaining csv with South America's GDP per country over the past 5 years.",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Task: create common Docker network or skip if the network already exists
create_common_network = BashOperator(
    task_id="create_common_network",
    bash_command=f"docker network create --driver bridge dc_network || true",
    dag=dag,
)

# Task: start services for 1) Postgres 2) extract and load data
up_el = BashOperator(
    task_id="docker_compose_el_up",
    bash_command=f"docker compose -f {base_directory}/extract_load/docker-compose.yml up -d",
    dag=dag,
)

# Task: start service for querying data and generating csv
up_query = BashOperator(
    task_id="docker_compose_query_up",
    bash_command=f"docker compose -f {base_directory}/query/docker-compose.yml up -d",
    dag=dag,
)

# Task: copy resulting CSV to host machine
get_csv = BashOperator(
    task_id="get_csv",
    bash_command=f"docker cp query:/app/sa_gdp.csv {base_directory}/.",
    dag=dag,
)

# Task: bring down the Docker Compose services for 1) Postgres 2) extract and load data
down_el = BashOperator(
    task_id="docker_compose_el_down",
    bash_command=f"docker compose -f {base_directory}/extract_load/docker-compose.yml down",
    dag=dag,
)

# Task: bring down the Docker Compose service for querying data and generating csv
down_query = BashOperator(
    task_id="docker_compose_query_down",
    bash_command=f"docker compose -f {base_directory}/query/docker-compose.yml down",
    dag=dag,
)


create_common_network >> up_el >> up_query >> get_csv >> [down_el, down_query]
