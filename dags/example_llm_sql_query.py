"""
## example_llm_sql_query

Demonstrates `@task.llm_sql` / `LLMSQLQueryOperator`. Translates a natural
language question into SQL against the seeded `space_logistics` SQLite DB,
then executes the generated SQL in a downstream task.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from airflow.sdk import dag, task

from include.seed import PRIMARY_DB, seed_primary


QUESTION = (
    "Which spacecraft are currently available (current_status = 'available'), "
    "ordered by capacity_tonnes descending, limited to 5?"
)


@dag(
    dag_id="example_llm_sql_query",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "llm-sql"],
    doc_md=__doc__,
)
def example_llm_sql_query():
    @task
    def prepare_input() -> str:
        counts = seed_primary()
        print(f"Seeded tables: {counts}")
        return QUESTION

    @task.llm_sql(
        llm_conn_id="pydanticai_default",
        db_conn_id="space_logistics",
        table_names=["spacecraft"],
        dialect="sqlite",
        require_approval=True,
        allow_modifications=True,
    )
    def generate_sql(question: str) -> str:
        return question

    @task
    def consume_output(sql: str) -> list[tuple]:
        print(f"Generated SQL:\n{sql}")
        with sqlite3.connect(PRIMARY_DB) as conn:
            rows = conn.execute(sql).fetchall()
        for row in rows:
            print(row)
        return rows

    consume_output(generate_sql(prepare_input()))


example_llm_sql_query()
