"""
## example_mcp_connection_transports

Both MCP transports side by side. `stdio` runs a local subprocess from
`mcp_stdio_space`, `http` talks to a remote server at `mcp_default`. Two agents
ask the same question over different transports and a downstream task compares
the answers.

The http half needs a reachable endpoint. If you only have the stdio server,
`gate_http_question` skips that agent. Point `mcp_default` at a real server to
see both of them run.
"""

from __future__ import annotations

import socket
from urllib.parse import urlparse

from airflow.exceptions import AirflowSkipException
from airflow.models import Connection
from airflow.providers.common.ai.toolsets.mcp import MCPToolset
from airflow.sdk import dag, task


QUESTION = (
    "Count operational space stations per planet and return the JSON map."
)


@dag(
    dag_id="example_mcp_connection_transports",
    tags=[
        "common-ai",
        "feature-example",
        "task.agent",
        "mcp-toolset",
        "mcp-transports",
    ],
    doc_md=__doc__,
)
def example_mcp_connection_transports():
    @task
    def prepare_input() -> str:
        return QUESTION

    def _http_reachable() -> bool:
        conn = Connection.get_connection_from_secrets("mcp_default")
        url = conn.host or (conn.extra_dejson or {}).get("url") or ""
        parsed = urlparse(url if "://" in url else f"http://{url}")
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if not host:
            return False
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            return False

    @task
    def gate_http_question(question: str) -> str:
        if not _http_reachable():
            raise AirflowSkipException("MCP HTTP endpoint unreachable")
        return question

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="Answer using MCP tools only.",
        toolsets=[MCPToolset(mcp_conn_id="mcp_stdio_space")],
    )
    def ask_via_stdio(question: str) -> str:
        return question

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="Answer using MCP tools only.",
        toolsets=[MCPToolset(mcp_conn_id="mcp_default")],
    )
    def ask_via_http(question: str) -> str:
        return question

    @task(trigger_rule="none_failed")
    def compare_answers(stdio_answer: str, http_answer: str | None = None) -> None:
        print("--- stdio ---")
        print(stdio_answer)
        print("--- http ---")
        print(http_answer if http_answer is not None else "(skipped: http endpoint unreachable)")
        if http_answer is None:
            return
        if stdio_answer.strip() == http_answer.strip():
            print("Both transports returned identical answers.")
        else:
            print("Answers differ — expected when only one transport is live.")

    question = prepare_input()
    stdio = ask_via_stdio(question)
    http = ask_via_http(gate_http_question(question))
    compare_answers(stdio, http)


example_mcp_connection_transports()
