"""
## example_llm_sql_query

`@task.llm_sql` / `LLMSQLQueryOperator` turning a plain-English question into
SQL against the seeded `space_logistics` database. A downstream task then runs
the generated query.
"""

from __future__ import annotations
from sqlglot import exp

import sqlite3

from airflow.sdk import dag, task

from include.seed import PRIMARY_DB, seed_primary


QUESTION = (
    "Which spacecraft are currently available (current_status = 'available'), "
    "ordered by capacity_tonnes descending, limited to 5?"
)


@dag(
    tags=["common-ai", "feature-example", "task.llm_sql"],
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
        system_prompt=(
            "Prefer indexed columns in "
            "filters and joins. "
            "Avoid SELECT *."
        ),
        validate_sql=True,
        dialect="sqlite",
        db_conn_id="space_logistics",
        table_names=["spacecraft"],
        require_approval=True,
        allow_modifications=True,
        allowed_sql_types=(
            exp.Select,
            exp.Union,
            exp.Intersect,
            exp.Except,
            exp.Insert,
            exp.Update,
        ),
    )
    def generate_sql(question: str) -> str:
        return question

    _generate_sql = generate_sql(prepare_input())

    @task
    def consume_output(sql: str) -> list[tuple]:
        print(f"Generated SQL:\n{sql}")
        with sqlite3.connect(PRIMARY_DB) as conn:
            rows = conn.execute(sql).fetchall()
        for row in rows:
            print(row)
        return rows

    consume_output(_generate_sql)


example_llm_sql_query()
