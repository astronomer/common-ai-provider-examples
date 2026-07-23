"""
## example_agent_complex

Demonstrates every constructor parameter of `@task.agent` / `AgentOperator`
in one place: `SQLToolset` access to the seeded `space_logistics` DB,
`usage_limits`, `durable` step caching, and a tracked `message_history`
session. `code_mode` and `enable_hitl_review` are passed explicitly but left
off -- both are mutually exclusive with `durable=True` (and `code_mode` needs
the `code-mode` extra, which isn't installed in this project). Same Ceres
supply-run use case as `example_agent_basic`, with tools and knobs added.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.providers.common.ai.toolsets.sql import SQLToolset
from airflow.sdk import dag, task
from pydantic_ai.usage import UsageLimits

from include.models import MissionPlan
from include.seed import seed_primary


@dag(
    dag_id="example_agent_complex",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "agent", "agent-complex"],
    doc_md=__doc__,
)
def example_agent_complex():
    @task
    def prepare_input() -> dict:
        counts = seed_primary()
        print(f"Seeded: {counts}")
        return {
            "mission_name": "Ceres supply run",
            "origin": "Earth Spacedock",
            "destination": "Ceres Depot",
            "cargo_tonnes": 180,
        }

    @task.agent(
        llm_conn_id="pydanticai_default",
        model_id=None,
        system_prompt=(
            "You are a mission planner for an interplanetary freight line. "
            "Use the SQL tools to find a spacecraft in the spacecraft table "
            "whose capacity_tonnes covers the mission's cargo_tonnes and "
            "whose current_status is 'active', then return a structured "
            "MissionPlan whose steps name that spacecraft."
        ),
        output_type=MissionPlan,
        toolsets=[
            SQLToolset(
                db_conn_id="space_logistics",
                allowed_tables=["spacecraft"],
                max_rows=25,
            )
        ],
        enable_tool_logging=True,
        agent_params={"retries": 2, "model_settings": {"temperature": 0.2}},
        usage_limits=UsageLimits(
            request_limit=15,
            tool_calls_limit=8,
            total_tokens_limit=50_000,
        ),
        durable=True,
        # Mutually exclusive with durable=True (AgentOperator raises
        # ValueError if both are set); also requires the `code-mode` extra
        # (pydantic-ai-harness), which isn't installed here.
        code_mode=False,
        # "[]" starts a tracked session: the full transcript gets pushed to
        # this task's XCom under key "message_history" for a follow-up turn
        # to resume. The default, None, is a single-turn run with no push.
        message_history="[]",
        # Mutually exclusive with durable=True and with message_history being
        # set (AgentOperator raises ValueError for either combination) --
        # left off here. See example_agent_hitl_review.py for a working demo.
        enable_hitl_review=False,
        max_hitl_iterations=3,
        hitl_timeout=timedelta(minutes=5),
        hitl_poll_interval=5.0,
        serialize_output=True,
    )
    def plan_mission(brief: dict) -> str:
        return (
            "Plan this mission step-by-step, including a refueling stop and "
            "a realistic estimated_days.\n\n"
            f"Brief: {brief}"
        )

    @task
    def consume_output(plan: MissionPlan | dict) -> None:
        if isinstance(plan, dict):
            plan = MissionPlan.model_validate(plan)
        print(f"{plan.mission_name}: {plan.origin} -> {plan.destination}")
        print(f"Estimated days: {plan.estimated_days}")
        for i, step in enumerate(plan.steps, start=1):
            print(f"  {i}. {step}")

    consume_output(plan_mission(prepare_input()))


example_agent_complex()
