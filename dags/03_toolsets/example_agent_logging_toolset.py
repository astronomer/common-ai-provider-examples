"""
## example_agent_logging_toolset

`LoggingToolset` wrapped around `SQLToolset`. The wrapper intercepts every tool
call and logs it as it happens, which is how you watch what an agent is doing
without touching the toolset underneath.
"""

from __future__ import annotations

from airflow.providers.common.ai.toolsets.logging import LoggingToolset
from airflow.providers.common.ai.toolsets.sql import SQLToolset
from airflow.sdk import dag, task

from include.seed import seed_primary


@dag(
    tags=[
        "common-ai",
        "feature-example",
        "task.agent",
        "logging-toolset",
        "sql-toolset",
    ],
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
