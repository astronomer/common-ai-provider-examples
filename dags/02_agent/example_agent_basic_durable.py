"""
## example_agent_basic_durable

The `example_agent_basic` flow again, this time with `durable=True`. Three
tools run in order:

1. `get_random_number` returns a random integer as a string. The second attempt
   reuses the recorded return without running the function body, so you should
   see a single `durable_demo: get_random_number` log across both attempts.
2. `simulate_transient_error_on_first_try` raises on Airflow try 1 and succeeds
   from try 2 onward, which is what forces the retry.
3. `double_random_number` takes that same string back and doubles it.

The random number is the same before and after the retry because on Airflow 3.3
`durable=True` caches each tool result in the task state store:
https://www.astronomer.io/docs/learn/airflow-task-state-store

`durable=True` and `enable_hitl_review=True` cannot both be set.
"""

from __future__ import annotations

import logging
import random
from datetime import timedelta

from airflow.sdk import dag, task
from pydantic_ai import FunctionToolset

from include.airflow_try import task_try_number
from include.models import MissionPlan

log = logging.getLogger(__name__)


def get_random_number() -> str:
    """Return a random integer as a string. Durable replay may reuse without re-running."""
    import time
    time.sleep(10)
    num = random.randint(1, 100)
    log.info("durable_demo: get_random_number body executed num=%s", num)
    return str(num)


def simulate_transient_error_on_first_try() -> str:
    """Fail on the first Airflow task try only; succeed in task retry."""
    tn = task_try_number()
    log.info("durable_demo: simulate_transient_error_on_first_try try_number=%s", tn)
    if tn < 2:
        raise RuntimeError(
            "intentional failure on first Airflow attempt (durable demo)"
        )
    return "second_airflow_attempt_ok"


def double_random_number(random_number: str) -> str:
    """Return twice the integer from get_random_number (pass the exact same string)."""
    n = int(random_number.strip())
    doubled = n * 2
    log.info("durable_demo: double_random_number %s -> %s", n, doubled)
    return str(doubled)


durable_demo_toolset = FunctionToolset(
    id="durable_operator_demo",
    instructions=(
        "Use tools in order: (1) get_random_number — remember the returned string; "
        "(2) simulate_transient_error_on_first_try — first Airflow try will error and retry; "
        "(3) double_random_number with that same string — then return MissionPlan "
        "mentioning the original number and its double."
    ),
    tools=[
        get_random_number,
        simulate_transient_error_on_first_try,
        double_random_number,
    ],
)


@dag(
    tags=[
        "common-ai",
        "feature-example",
        "task.agent",
        "durable",
        "function-toolset",
        "structured-output",
    ],
    default_args={"retries": 2, "retry_delay": timedelta(seconds=5)},
    doc_md=__doc__,
)
def example_agent_basic_durable():
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
            "Follow the tool instructions, then return a structured MissionPlan."
        ),
        output_type=MissionPlan,
        toolsets=[durable_demo_toolset],
        durable=True,
    )
    def plan_mission(brief: dict) -> str:
        return (
            "Plan this mission step-by-step. Include refueling stops and a "
            "realistic estimated_days. After the tools, mention the random number "
            "and its doubled value in your steps.\n\n"
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


example_agent_basic_durable()
