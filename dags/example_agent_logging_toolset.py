"""
## example_agent_logging_toolset

Demonstrates `LoggingToolset` as a wrapper around `SQLToolset` with
`@task.agent`. The wrapper intercepts every tool invocation and logs it in
real time — useful for observing agent behavior without modifying the
underlying toolset.
"""

from __future__ import annotations

from datetime import datetime

from airflow.providers.common.ai.toolsets.logging import LoggingToolset
from airflow.providers.common.ai.toolsets.sql import SQLToolset
from airflow.sdk import dag, task

from include.seed import seed_primary


@dag(
    dag_id="example_agent_logging_toolset",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "agent", "logging-toolset"],
    doc_md=__doc__,
)
def example_agent_logging_toolset():
    @task
    def prepare_input() -> str:
        seed_primary()
        return "How many spacecraft are currently 'in_transit'?"

    sql_toolset = SQLToolset(
        db_conn_id="space_logistics",
        allowed_tables=["spacecraft"],
        max_rows=100,
    )

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="Answer the user's question using SQL tools.",
        toolsets=[LoggingToolset(wrapped=sql_toolset)],
    )
    def logged_query(question: str) -> str:
        return question

    @task
    def consume_output(answer: str) -> None:
        print(f"Answer (see task logs for tool-call trace):\n{answer}")

    consume_output(logged_query(prepare_input()))


example_agent_logging_toolset()
