"""
## example_hitl_approval

`ApprovalOperator`. Approving lets the downstream tasks run, rejecting skips
them.

The two options, Approve and Reject, are hardcoded: passing `options` or
`multiple` raises `ValueError`. `ignore_downstream_trigger_rules=True` skips every downstream task. The default
skips only the direct children. No `defaults` is set here, so the task fails on
timeout.

Answer it under Browse > Required Actions.
"""

from __future__ import annotations

from datetime import timedelta

from airflow.providers.standard.operators.hitl import ApprovalOperator
from airflow.sdk import Param, chain, dag, task


@dag(
    tags=[
        "standard-provider",
        "feature-example",
        "ApprovalOperator",
        "hitl-operators",
    ],
    doc_md=__doc__,
)
def example_hitl_approval():
    @task
    def prepare_launch_manifest() -> dict:
        return {
            "flight_id": "CER-114",
            "destination": "Ceres Depot",
            "cargo_tonnes": 180,
            "window_opens": "2026-09-04T06:20:00Z",
        }

    _manifest = prepare_launch_manifest()

    _approve_launch = ApprovalOperator(
        task_id="approve_launch",
        subject="Approve launch window for {{ ti.xcom_pull(task_ids='prepare_launch_manifest')['flight_id'] }}",
        body="""**Flight:** {{ ti.xcom_pull(task_ids='prepare_launch_manifest')['flight_id'] }}
**Destination:** {{ ti.xcom_pull(task_ids='prepare_launch_manifest')['destination'] }}
**Cargo:** {{ ti.xcom_pull(task_ids='prepare_launch_manifest')['cargo_tonnes'] }} t
**Window opens:** {{ ti.xcom_pull(task_ids='prepare_launch_manifest')['window_opens'] }}

Approve to commit the window. Reject to skip the launch tasks.""",
        params={
            "reviewer_note": Param(
                "",
                type="string",
                title="Note",
                description="Optional context for the flight log.",
            ),
        },
        # Skips every downstream task, not only direct children.
        ignore_downstream_trigger_rules=True,
        # With `defaults` unset, a timeout fails the task instead of
        # auto-approving. That is the safe default for a launch gate.
        response_timeout=timedelta(hours=2),
    )

    @task
    def commit_launch_window(manifest: dict, decision: dict) -> None:
        print(f"Committing window for {manifest['flight_id']}")
        print(f"Approved by: {decision['responded_by_user']}")
        print(f"Note: {decision['params_input'].get('reviewer_note') or '(none)'}")

    @task
    def notify_flight_ops(manifest: dict) -> None:
        print(f"Flight ops notified for {manifest['flight_id']}")

    chain(
        _manifest,
        _approve_launch,
        [
            commit_launch_window(
                manifest=_manifest, decision=_approve_launch.output
            ),
            notify_flight_ops(manifest=_manifest),
        ],
    )


example_hitl_approval()
