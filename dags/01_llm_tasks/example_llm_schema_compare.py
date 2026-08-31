"""
## example_llm_schema_compare

`@task.llm_schema_compare` across two SQLite databases whose `spacecraft`
tables have drifted apart: columns renamed, units changed. The model writes up
what would break.
"""

from __future__ import annotations

from airflow.sdk import dag, task

from include.seed import seed_alt_with_drift, seed_primary


@dag(
    dag_id="example_llm_schema_compare",
    tags=["common-ai", "feature-example", "task.llm_schema_compare"],
    doc_md=__doc__,
)
def example_llm_schema_compare():
    @task
    def prepare_input() -> dict:
        primary = seed_primary()
        alt = seed_alt_with_drift()
        print(f"primary={primary}  alt={alt}")
        return {"ok": True}

    @task.llm_schema_compare(
        llm_conn_id="pydanticai_default",
        db_conn_ids=[
            "space_logistics",
            "space_logistics_alt"
        ],
        table_names=["spacecraft"],
    )
    def compare_schemas(_: dict) -> str:
        return (
            "Compare the given tables. Flag any "
            "mismatch that would break a CDC pipeline "
            "copying rows from the "
            "primary into the alternate warehouse."
        )

    @task(trigger_rule="all_done_setup_success")
    def consume_output(report: dict) -> None:
        print(f"Compatible:   {report.get('compatible')}")
        for mismatch in report.get("mismatches", []) or []:
            print(f"  mismatch: {mismatch}")
        for action in report.get("suggested_actions", []) or []:
            print(f"  action:   {action}")
        if report.get("compatible") is False:
            print("ALERT: pipeline would break — see mismatches above.")

    consume_output(compare_schemas(prepare_input()))


example_llm_schema_compare()
