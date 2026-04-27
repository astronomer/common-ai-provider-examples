"""
## example_agent_hitl_review

Demonstrates `@task.agent` with HITL review enabled. The agent proposes a
risky cargo-reroute action, then pauses in a polling loop until a human
approves, rejects, or requests changes via the `/hitl-review` FastAPI
plugin on the Airflow API server.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.providers.common.ai.toolsets.sql import SQLToolset
from airflow.sdk import dag, task

from include.seed import seed_primary


@dag(
    dag_id="example_agent_hitl_review",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "agent", "hitl"],
    doc_md=__doc__,
)
def example_agent_hitl_review():
    @task
    def prepare_input() -> str:
        seed_primary()
        return (
            "A solar flare has closed the Earth-Ceres corridor. Propose a "
            "reroute plan for every in_transit heavy_transport. The plan "
            "will be reviewed by a human before execution. The plan should be not longer than 100 words."
        )

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a dispatcher. Propose a concrete reroute plan; the "
            "human reviewer may approve, reject, or request changes."
        ),
        toolsets=[
            SQLToolset(
                db_conn_id="space_logistics",
                allowed_tables=["spacecraft", "shipping_routes", "space_stations"],
            )
        ],
        enable_hitl_review=True,
        max_hitl_iterations=3,
        hitl_timeout=timedelta(hours=1),
        hitl_poll_interval=10,
    )
    def review_plan(question: str) -> str:
        return question

    @task
    def consume_output(final_plan: str) -> None:
        print("HITL-approved plan:\n")
        print(final_plan)

    consume_output(review_plan(prepare_input()))


example_agent_hitl_review()
