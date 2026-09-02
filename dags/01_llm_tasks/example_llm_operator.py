"""
## example_llm_operator

`@task.llm` / `LLMOperator` with a Pydantic `output_type` and `UsageLimits`.

A mission anomaly report goes in as free text and a structured `SeverityReport`
comes out, which the downstream task can branch on.
"""

from __future__ import annotations

from pathlib import Path

from airflow.sdk import dag, task
from pydantic_ai.usage import UsageLimits

from include.models import SeverityReport


FIXTURE = Path("/usr/local/airflow/include/fixtures/anomaly_report.md")


@dag(
    tags=[
        "common-ai",
        "feature-example",
        "task.llm",
        "structured-output",
        "usage-limits",
    ],
    doc_md=__doc__,
)
def example_llm_operator():
    @task
    def prepare_input() -> str:
        return FIXTURE.read_text()

    @task.llm(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a fleet safety officer. "
            "Summarize spacecraft anomaly "
            "reports into a strict "
            "SeverityReport object."
        ),
        output_type=SeverityReport,
        require_approval=True,
        usage_limits=UsageLimits(request_limit=3, total_tokens_limit=4000),
    )
    def summarize(report_text: str) -> str:
        return (
            "Summarize the following "
            "mission anomaly report in one paragraph. "
            "Pick the single overall "
            "severity.\n\n"
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
