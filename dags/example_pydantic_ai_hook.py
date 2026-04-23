"""
## example_pydantic_ai_hook

Demonstrates the low-level `PydanticAIHook` API. Instead of using the
dedicated operators/decorators, a plain `@task` function instantiates the
hook, builds an agent with `create_agent(...)`, and calls `run_sync(...)`.
Useful when the provider's operators do not cover an edge case (custom
streaming, fine-grained lifecycle, etc).
"""

from __future__ import annotations

from datetime import datetime

from airflow.providers.common.ai.hooks.pydantic_ai import PydanticAIHook
from airflow.sdk import dag, task

from include.models import SeverityReport


@dag(
    dag_id="example_pydantic_ai_hook",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["common-ai", "example", "space", "hook"],
    doc_md=__doc__,
)
def example_pydantic_ai_hook():
    @task
    def prepare_input() -> str:
        return (
            "The ISS reported a 3% coolant-loop pressure drop during the "
            "2026-04-15 EVA. Ground crew ran diagnostics; no physical leak "
            "was detected. Pressure returned to nominal after 42 minutes."
        )

    @task
    def run_agent(report_text: str) -> dict:
        hook = PydanticAIHook(llm_conn_id="pydanticai_default")
        agent = hook.create_agent(
            instructions=(
                "You are a mission-control safety officer. Summarize the "
                "incident into a strict SeverityReport object."
            ),
            output_type=SeverityReport,
        )
        result = agent.run_sync(f"Incident:\n{report_text}")
        return result.output.model_dump()

    @task
    def consume_output(report: SeverityReport | dict) -> None:
        if isinstance(report, dict):
            report = SeverityReport.model_validate(report)
        print(f"Severity: {report.severity}")
        print(f"Summary:  {report.summary}")
        print(f"Action:   {report.recommended_action}")

    consume_output(run_agent(prepare_input()))


example_pydantic_ai_hook()
