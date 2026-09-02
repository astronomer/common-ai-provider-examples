"""
## example_agent_basic

`@task.agent` with nothing optional set: no toolsets, one Pydantic
`output_type` (`MissionPlan`). The agent works from a self-contained prompt and
returns a plan for a Ceres supply run.
"""

from __future__ import annotations

from airflow.sdk import dag, task

from include.models import MissionPlan


@dag(
    tags=["common-ai", "feature-example", "task.agent", "structured-output"],
    doc_md=__doc__,
)
def example_agent_basic():
    @task
    def prepare_input() -> dict:
        return {
            "mission_name": "Ceres supply run",
            "origin": "Earth Spacedock",
            "destination": "Ceres Depot",
            "cargo_tonnes": 180,
        }

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a mission planner for an interplanetary freight line. "
            "Given a mission brief, return a structured MissionPlan."
        ),
        output_type=MissionPlan,
    )
    def plan_mission(brief: dict) -> str:
        return (
            "Plan this mission step-by-step. Include refueling stops and a "
            "realistic estimated_days.\n\n"
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


example_agent_basic()
