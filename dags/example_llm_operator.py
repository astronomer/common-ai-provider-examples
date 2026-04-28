"""
## example_llm_operator

Demonstrates `@task.llm` / `LLMOperator` with a Pydantic `output_type`.

Flow: prepare_input -> summarize (LLM) -> consume_output.
Space context: summarize a mission anomaly report into a structured
SeverityReport the next task can branch on.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task

from include.models import SeverityReport


FIXTURE = Path("/usr/local/airflow/include/fixtures/anomaly_report.md")


@dag(
    dag_id="example_llm_operator",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "llm"],
    doc_md=__doc__,
)
def example_llm_operator():
    @task
    def prepare_input() -> str:
        return FIXTURE.read_text()

    @task.llm(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a fleet safety officer. Summarize spacecraft anomaly "
            "reports into a strict SeverityReport object."
        ),
        output_type=SeverityReport,
        agent_params={},
    )
    def summarize(report_text: str) -> str:
        return (
            "Summarize the following mission anomaly report. "
            "Pick the single overall severity.\n\n"
            f"REPORT:\n{report_text}"
        )

    @task
    def consume_output(report: SeverityReport | dict) -> None:
        if isinstance(report, dict):
            report = SeverityReport.model_validate(report)
        print(f"Severity:   {report.severity}")
        print(f"Summary:    {report.summary}")
        print(f"Systems:    {', '.join(report.affected_systems)}")
        print(f"Action:     {report.recommended_action}")
        if report.severity in {"high", "critical"}:
            print("ALERT: escalating to ops.")

    consume_output(summarize(prepare_input()))


example_llm_operator()
