"""
## example_pydantic_ai_hook

The low-level `PydanticAIHook` API. A plain `@task` builds the hook, calls
`create_agent(...)`, and runs it with `run_sync(...)`.

Use this when the operators don't do what you need: custom streaming,
finer control over the agent lifecycle, anything the decorators don't expose.
"""

from __future__ import annotations

from airflow.providers.common.ai.hooks.pydantic_ai import PydanticAIHook
from airflow.sdk import dag, task

from include.models import SeverityReport


@dag(
    dag_id="example_pydantic_ai_hook",
    tags=["common-ai", "feature-example", "PydanticAIHook", "structured-output"],
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
