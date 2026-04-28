"""
## example_agent_advanced

Demonstrates `@task.agent` with a custom PydanticAI `AbstractToolset`
(`IssOpenNotifyToolset`, ISS position via Open Notify), structured
`IssTelemetryReport` output, and the full agent
constructor knobs (`model_id`, `enable_tool_logging`, `agent_params`,
`durable`, HITL settings). The user prompt is the string returned from the
decorated callable (same contract as `AgentOperator.prompt`).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from airflow.sdk import dag, task
from pydantic import BaseModel, Field

from include.iss_open_notify_toolset import IssOpenNotifyToolset


class IssTelemetryReport(BaseModel):
    """Structured ISS pass summary after using live position tools."""

    signal_grade: Literal["a", "b", "c", "d"] = Field(
        description=(
            "Data quality for this readout: a=fresh live tool response, "
            "b=good confidence, c=marginal or delayed, d=could not verify"
        )
    )
    headline: str = Field(
        description="One-line ops-board summary (e.g. over which region)."
    )
    watch_items: list[str] = Field(
        description=(
            "2–4 short bullets: tool used, timestamp context, caveats, "
            "anything else useful for ground crew."
        )
    )
    position_line: str = Field(
        description=(
            "Latitude/longitude line exactly as returned by iss_now "
            "(verbatim substring is fine)."
        )
    )


iss_toolset = IssOpenNotifyToolset()


@dag(
    dag_id="example_agent_advanced",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "agent", "agent-advanced"],
    doc_md=__doc__,
)
def example_agent_advanced():
    @task
    def prepare_input() -> str:
        return (
            "Where is the International Space Station right now? Call "
            "iss_now for live coordinates, then return an "
            "IssTelemetryReport: signal_grade a–d from how solid the read is, "
            "headline for the pass, a few watch_items bullets for crew notes, "
            "and position_line echoing the tool output."
        )

    @task.agent(
        llm_conn_id="pydanticai_default",
        model_id=None,
        system_prompt=(
            "You are a ground-station analyst. Call tools when the user needs "
            "live telemetry. A human will review the output and may request changes."
        ),
        output_type=IssTelemetryReport,
        toolsets=[iss_toolset],
        enable_tool_logging=True,
        agent_params={"tool_timeout": 60.0},
        durable=True,
        enable_hitl_review=False,
        max_hitl_iterations=3,
        hitl_timeout=timedelta(minutes=5),
        hitl_poll_interval=5.0,
    )
    def my_agentic_task(user_prompt: str) -> str:
        return user_prompt

    @task
    def consume_output(report: IssTelemetryReport | dict) -> None:
        if isinstance(report, dict):
            report = IssTelemetryReport.model_validate(report)
        print(f"signal_grade:   {report.signal_grade}")
        print(f"headline:       {report.headline}")
        print("watch_items:")
        for item in report.watch_items:
            print(f"  - {item}")
        print(f"position_line:  {report.position_line}")

    consume_output(my_agentic_task(prepare_input()))


example_agent_advanced()
