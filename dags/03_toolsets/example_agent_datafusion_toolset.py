"""
## example_agent_datafusion_toolset

`@task.agent` with `DataFusionToolset`. A pre-task copies the shipping_routes
CSV into `/tmp/fusion/`, then the agent runs aggregate queries over it with no
warehouse involved.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from airflow.providers.common.ai.toolsets.datafusion import DataFusionToolset
from airflow.providers.common.sql.datafusion.engine import DataSourceConfig
from airflow.sdk import dag, task


FUSION_DIR = Path("/tmp/fusion")
SRC = Path("/usr/local/airflow/include/csvs/shipping_routes.csv")


@dag(
    dag_id="example_agent_datafusion_toolset",
    tags=["common-ai", "feature-example", "task.agent", "datafusion-toolset"],
    doc_md=__doc__,
)
def example_agent_datafusion_toolset():
    @task
    def prepare_input() -> str:
        FUSION_DIR.mkdir(parents=True, exist_ok=True)
        target = FUSION_DIR / "shipping_routes.csv"
        shutil.copyfile(SRC, target)
        print(f"Staged {target}")
        return (
            "Read shipping_routes.csv via the datafusion tool and return the "
            "average avg_duration_hours for routes where is_active = 'true'."
        )

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a data analyst. Use the datafusion tools to register "
            "files under /tmp/fusion and run SQL against them."
        ),
        toolsets=[
            DataFusionToolset(
                datasource_configs=[
                    DataSourceConfig(
                        conn_id="fixtures_fs",
                        table_name="shipping_routes",
                        uri="file:///tmp/fusion/shipping_routes.csv",
                        format="csv",
                    )
                ],
            )
        ],
    )
    def analyze_routes(question: str) -> str:
        return question

    @task
    def consume_output(answer: str) -> None:
        print(f"DataFusion agent answer:\n{answer}")

    consume_output(analyze_routes(prepare_input()))


example_agent_datafusion_toolset()
