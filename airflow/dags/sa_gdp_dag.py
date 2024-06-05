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

# defining DAG
dag = DAG(
    "sa_gdp_dag",
    default_args=default_args,
    description="DAG for obtaining csv with South America's GDP per country over the past 5 years.",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Task: create common Docker network or skip if the network already exists. A common
# network is needed for different services, spawned by different docker-compose.yml's
# in different folders, to communicate.
create_common_network = BashOperator(
    task_id="create_common_network",
    bash_command="""
    
    NETWORK_NAME="dc_network"

    # checking if the network already exists
    if ! docker network inspect "$NETWORK_NAME" &>/dev/null; then
        # creating network
        docker network create --driver bridge "$NETWORK_NAME"
        echo "Network '$NETWORK_NAME' created."
    else
        # not doing nothing
        echo "Network '$NETWORK_NAME' already exists."
    fi
    """,
    dag=dag,
)

# Task: start services for Postgres
up_db = BashOperator(
    task_id="docker_compose_db_up",
    bash_command=f"docker compose -f {base_directory}/db/docker-compose.yml up -d",
    dag=dag,
)

# Task: start services for extract and load data
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
    bash_command=f"docker cp query:/app/sa_gdp.csv {base_directory}/results/.",
    dag=dag,
)

# Task: bring down the Docker Compose services for Postgres
down_db = BashOperator(
    task_id="docker_compose_db_down",
    bash_command=f"docker compose -f {base_directory}/db/docker-compose.yml down",
    dag=dag,
)

# Task: bring down the Docker Compose services for extract and load data
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


create_common_network >> up_db >> up_el >> up_query >> get_csv >> [down_db, down_el, down_query]
