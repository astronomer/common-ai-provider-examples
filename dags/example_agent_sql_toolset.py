"""
## example_agent_sql_toolset

Demonstrates `@task.agent` + `SQLToolset`. The agent is given access to
`list_tables`, `get_schema`, `query`, and `check_query` against the seeded
`space_logistics` SQLite DB and answers a shipping question.
"""

from __future__ import annotations

from datetime import datetime

from airflow.providers.common.ai.toolsets.sql import SQLToolset
from airflow.sdk import dag, task

from include.models import RouteAnswer
from include.seed import seed_primary


@dag(
    dag_id="example_agent_sql_toolset",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "agent", "sql-toolset"],
    doc_md=__doc__,
)
def example_agent_sql_toolset():
    @task
    def prepare_input() -> str:
        counts = seed_primary()
        print(f"Seeded: {counts}")
        return (
            "Name the top 3 longest shipping_routes that terminate at an "
            "operational space_station. Return the RouteAnswer structure."
        )

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a SQL analyst for an interplanetary freight line. "
            "Use the available tools to inspect the schema before writing "
            "queries. Return the structured RouteAnswer."
        ),
        output_type=RouteAnswer,
        toolsets=[
            SQLToolset(
                db_conn_id="space_logistics",
                allowed_tables=["shipping_routes", "space_stations"],
                max_rows=50,
            )
        ],
    )
    def answer_route_question(question: str) -> str:
        return question

    @task
    def consume_output(answer: RouteAnswer | dict) -> None:
        if isinstance(answer, dict):
            answer = RouteAnswer.model_validate(answer)
        print(f"Question: {answer.question}")
        for route in answer.top_routes:
            print(f"  - {route}")
        print(f"Rationale: {answer.rationale}")

    consume_output(answer_route_question(prepare_input()))


example_agent_sql_toolset()
