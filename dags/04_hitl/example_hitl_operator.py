"""
## example_hitl_operator

`HITLOperator`, the base class the other three build on. It shows a list of
`options`, records what the reviewer picked, and pushes that to XCom. It never
skips and never branches, so every downstream task runs and reads the decision.

Uses `multiple=True` so a reviewer can hold more than one bay, plus `defaults`
and `response_timeout`. Because `defaults` is set, a timeout succeeds with the
default selected.

Answer it under Browse > Required Actions.
"""

from __future__ import annotations

from datetime import timedelta

from airflow.providers.standard.operators.hitl import HITLOperator
from airflow.sdk import Param, chain, dag, task


@dag(
    dag_id="example_hitl_operator",
    tags=[
        "standard-provider",
        "feature-example",
        "HITLOperator",
        "hitl-operators",
    ],
    doc_md=__doc__,
)
def example_hitl_operator():
    @task
    def list_available_bays() -> dict:
        return {
            "station": "Ceres Depot",
            "arrival": "2026-09-11T14:05:00Z",
            "bays_free": ["Bay A2", "Bay B1", "Bay C4"],
        }

    _bays = list_available_bays()

    _reserve_bays = HITLOperator(
        task_id="reserve_bays",
        subject="Reserve docking bays at {{ ti.xcom_pull(task_ids='list_available_bays')['station'] }}",
        body="""**Arrival:** {{ ti.xcom_pull(task_ids='list_available_bays')['arrival'] }}
**Free bays:** {{ ti.xcom_pull(task_ids='list_available_bays')['bays_free'] | join(', ') }}

Select every bay to hold for this arrival. Large hulls need two adjacent bays.""",
        options=["Bay A2", "Bay B1", "Bay C4"],
        # `multiple=True` lets a reviewer select more than one option.
        # `defaults` must be a subset of `options`.
        multiple=True,
        defaults=["Bay A2"],
        params={
            "hold_hours": Param(
                6,
                type="integer",
                minimum=1,
                maximum=48,
                title="Hold duration (hours)",
            ),
        },
        response_timeout=timedelta(hours=1),
    )

    @task
    def record_reservation(decision: dict) -> None:
        print(f"Bays held: {decision['chosen_options']}")
        print(f"Hold hours: {decision['params_input']['hold_hours']}")
        print(f"Responded by: {decision['responded_by_user']}")
        print(f"Responded at: {decision['responded_at']}")

    chain(_bays, _reserve_bays, record_reservation(decision=_reserve_bays.output))


example_hitl_operator()
