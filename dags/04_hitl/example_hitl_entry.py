"""
## example_hitl_entry

`HITLEntryOperator`, a form with nothing to decide. There is no approval step
and no branch; the operator collects structured input from a person and passes
it downstream.

Leave `options` out and the operator fills in `options=["OK"]` and
`defaults=["OK"]`, so the reviewer gets a single confirm button under the form.
Whatever they type arrives downstream under `params_input`, keyed by param
name.

Answer it under Browse > Required Actions.
"""

from __future__ import annotations

from airflow.providers.standard.operators.hitl import HITLEntryOperator
from airflow.sdk import Param, chain, dag, task


@dag(
    tags=[
        "standard-provider",
        "feature-example",
        "HITLEntryOperator",
        "hitl-operators",
    ],
    doc_md=__doc__,
)
def example_hitl_entry():
    @task
    def open_anomaly_report() -> dict:
        return {
            "anomaly_id": "ANM-0457",
            "spacecraft": "SS Meridian",
            "symptom": "3% coolant-loop pressure drop during the 2026-04-15 EVA",
        }

    _anomaly = open_anomaly_report()

    _file_findings = HITLEntryOperator(
        task_id="file_findings",
        subject="File findings for {{ ti.xcom_pull(task_ids='open_anomaly_report')['anomaly_id'] }}",
        body="""**Spacecraft:** {{ ti.xcom_pull(task_ids='open_anomaly_report')['spacecraft'] }}
**Symptom:** {{ ti.xcom_pull(task_ids='open_anomaly_report')['symptom'] }}

Record the engineer's assessment before the craft is cleared.""",
        params={
            "root_cause": Param(
                "",
                type="string",
                title="Root cause",
                description="What actually caused the pressure drop.",
            ),
            "severity": Param(
                "medium",
                type="string",
                enum=["low", "medium", "high", "critical"],
                title="Severity",
            ),
            "downtime_hours": Param(
                0,
                type="integer",
                minimum=0,
                title="Downtime (hours)",
            ),
            "grounded": Param(
                False,
                type="boolean",
                title="Ground the craft",
                description="Block further flights until re-certified.",
            ),
        },
    )

    @task
    def write_maintenance_log(anomaly: dict, entry: dict) -> None:
        findings = entry["params_input"]
        print(f"{anomaly['anomaly_id']} on {anomaly['spacecraft']}")
        print(f"  root cause:  {findings['root_cause']}")
        print(f"  severity:    {findings['severity']}")
        print(f"  downtime:    {findings['downtime_hours']}h")
        print(f"  grounded:    {findings['grounded']}")
        print(f"  filed by:    {entry['responded_by_user']}")

    chain(
        _anomaly,
        _file_findings,
        write_maintenance_log(anomaly=_anomaly, entry=_file_findings.output),
    )


example_hitl_entry()
