"""
## example_hitl_branch

`HITLBranchOperator`. A reviewer picks one option, the operator runs the
matching downstream task and skips the rest.

`options_mapping` translates readable labels into task ids. Without it, every
entry in `options` would have to be a literal task id. The keys are checked
against `options` when the Dag is parsed, so a typo raises `ValueError` at parse
time.

Answer it under Browse > Required Actions.
"""

from __future__ import annotations

from datetime import timedelta

from airflow.providers.standard.operators.hitl import HITLBranchOperator
from airflow.sdk import chain, dag, task


@dag(
    tags=[
        "standard-provider",
        "feature-example",
        "HITLBranchOperator",
        "hitl-operators",
    ],
    doc_md=__doc__,
)
def example_hitl_branch():
    @task
    def scan_inbound_cargo() -> dict:
        return {
            "manifest_id": "MAN-2291",
            "origin": "Titan Yards",
            "declared_value_credits": 412_000,
            "flags": ["sealed container", "no customs stamp"],
        }

    _cargo = scan_inbound_cargo()

    _route_cargo = HITLBranchOperator(
        task_id="route_cargo",
        subject="Route inbound manifest {{ ti.xcom_pull(task_ids='scan_inbound_cargo')['manifest_id'] }}",
        body="""**Origin:** {{ ti.xcom_pull(task_ids='scan_inbound_cargo')['origin'] }}
**Declared value:** {{ ti.xcom_pull(task_ids='scan_inbound_cargo')['declared_value_credits'] }} credits
**Flags:** {{ ti.xcom_pull(task_ids='scan_inbound_cargo')['flags'] | join(', ') }}

Choose how this container clears the dock.""",
        options=["Fast lane", "Customs review", "Quarantine"],
        # Maps each label to the task id it should branch to.
        options_mapping={
            "Fast lane": "release_to_fast_lane",
            "Customs review": "send_to_customs",
            "Quarantine": "move_to_quarantine",
        },
        defaults=["Customs review"],
        response_timeout=timedelta(hours=3),
    )

    @task
    def release_to_fast_lane() -> None:
        print("Released straight to the depot floor.")

    @task
    def send_to_customs() -> None:
        print("Queued for customs inspection.")

    @task
    def move_to_quarantine() -> None:
        print("Moved to the quarantine bay pending biohazard screening.")

    chain(
        _cargo,
        _route_cargo,
        [release_to_fast_lane(), send_to_customs(), move_to_quarantine()],
    )


example_hitl_branch()
