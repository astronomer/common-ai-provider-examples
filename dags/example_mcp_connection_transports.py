"""
## example_mcp_connection_transports

Demonstrates both MCP connection transports side by side: `stdio` (local
subprocess launched from `mcp_stdio_space`) and `http` (remote server at
`mcp_default`). Two agents ask the same question via different transports
and a downstream task diffs their answers.

The `http` branch requires a reachable MCP HTTP endpoint; if your demo
environment only has the stdio server, pause the `ask_via_http` task or
update the `mcp_default` connection to point at a running server.
"""

from __future__ import annotations

from datetime import datetime

import socket
from urllib.parse import urlparse

from airflow.models import Connection
from airflow.providers.common.ai.operators.agent import AgentOperator
from airflow.providers.common.ai.toolsets.mcp import MCPToolset
from airflow.providers.standard.operators.python import ShortCircuitOperator
from airflow.sdk import dag, task


QUESTION = (
    "Count operational space stations per planet and return the JSON map."
)


@dag(
    dag_id="example_mcp_connection_transports",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["common-ai", "example", "space", "mcp", "transports"],
    doc_md=__doc__,
)
def example_mcp_connection_transports():
    @task
    def prepare_input() -> str:
        return QUESTION

    ask_via_stdio = AgentOperator(
        task_id="ask_via_stdio",
        prompt="{{ ti.xcom_pull(task_ids='prepare_input') }}",
        llm_conn_id="pydanticai_default",
        system_prompt="Answer using MCP tools only.",
        toolsets=[MCPToolset(mcp_conn_id="mcp_stdio_space")],
    )

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

    http_gate = ShortCircuitOperator(
        task_id="http_gate",
        python_callable=_http_reachable,
        ignore_downstream_trigger_rules=False,
    )

    ask_via_http = AgentOperator(
        task_id="ask_via_http",
        prompt="{{ ti.xcom_pull(task_ids='prepare_input') }}",
        llm_conn_id="pydanticai_default",
        system_prompt="Answer using MCP tools only.",
        toolsets=[MCPToolset(mcp_conn_id="mcp_default")],
    )

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
    question >> ask_via_stdio
    question >> http_gate >> ask_via_http
    compare_answers(ask_via_stdio.output, ask_via_http.output)


example_mcp_connection_transports()
