"""
## example_agent_mcp_toolset

Demonstrates `@task.agent` + `MCPToolset`. The `mcp_stdio_space` connection
launches `include/mcp_server/space_server.py` as a subprocess; the agent can
call `list_planets`, `list_spacecraft`, and `count_stations_by_planet`
through the MCP protocol.
"""

from __future__ import annotations

from datetime import datetime

from airflow.providers.common.ai.toolsets.mcp import MCPToolset
from airflow.sdk import dag, task


@dag(
    dag_id="example_agent_mcp_toolset",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "agent", "mcp-toolset"],
    doc_md=__doc__,
)
def example_agent_mcp_toolset():
    @task
    def prepare_input() -> str:
        return (
            "Use the MCP tools to count operational space stations per planet "
            "and name the planet with the most stations. Include the raw "
            "counts in your answer."
        )

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a space-logistics analyst with access to the "
            "space-logistics MCP server. Prefer MCP tools over guessing."
        ),
        toolsets=[MCPToolset(mcp_conn_id="mcp_stdio_space")],
    )
    def ask_mcp_agent(question: str) -> str:
        return question

    @task
    def consume_output(answer: str) -> None:
        print(f"MCP agent answer:\n{answer}")

    consume_output(ask_mcp_agent(prepare_input()))


example_agent_mcp_toolset()
