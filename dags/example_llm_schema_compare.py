"""
## example_llm_schema_compare

Demonstrates `LLMSchemaCompareOperator`. Seeds two SQLite databases whose
`spacecraft` tables have drifted (renamed columns, changed units), then uses
the LLM to produce a compatibility report.
"""

from __future__ import annotations

from datetime import datetime

from airflow.providers.common.ai.operators.llm_schema_compare import (
    LLMSchemaCompareOperator,
)
from airflow.sdk import dag, task

from include.seed import seed_alt_with_drift, seed_primary


@dag(
    dag_id="example_llm_schema_compare",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["common-ai", "example", "space", "llm-schema-compare"],
    doc_md=__doc__,
)
def example_llm_schema_compare():
    @task
    def prepare_input() -> dict:
        primary = seed_primary()
        alt = seed_alt_with_drift()
        print(f"primary={primary}  alt={alt}")
        return {"ok": True}

    compare_schemas = LLMSchemaCompareOperator(
        task_id="compare_schemas",
        prompt=(
            "Compare the `spacecraft` table across both databases. Flag any "
            "mismatch that would break a CDC pipeline copying rows from the "
            "primary into the alternate warehouse."
        ),
        llm_conn_id="pydanticai_default",
        db_conn_ids=["space_logistics", "space_logistics_alt"],
        table_names=["spacecraft"],
        context_strategy="full",
    )

    @task
    def consume_output(report: dict) -> None:
        print(f"Compatible:   {report.get('compatible')}")
        for mismatch in report.get("mismatches", []) or []:
            print(f"  mismatch: {mismatch}")
        for action in report.get("suggested_actions", []) or []:
            print(f"  action:   {action}")
        if report.get("compatible") is False:
            print("ALERT: pipeline would break — see mismatches above.")

    seeded = prepare_input()
    seeded >> compare_schemas
    consume_output(compare_schemas.output)


example_llm_schema_compare()
