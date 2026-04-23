"""
## example_agent_hook_toolset

Demonstrates `AgentOperator` + `HookToolset`. Any Airflow Hook's public
methods can be exposed as agent tools. Here we wrap the filesystem Hook
pointed at `include/fixtures/` and let the agent discover files.
"""

from __future__ import annotations

from datetime import datetime

from airflow.providers.common.ai.operators.agent import AgentOperator
from airflow.providers.common.ai.toolsets.hook import HookToolset
from airflow.sdk import dag, task

from include.fixtures_hook import FixturesHook


@dag(
    dag_id="example_agent_hook_toolset",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["common-ai", "example", "space", "agent", "hook-toolset"],
    doc_md=__doc__,
)
def example_agent_hook_toolset():
    @task
    def prepare_input() -> str:
        return (
            "List every cargo manifest file available under the fixtures "
            "filesystem and name the one with the highest declared hazard."
        )

    inventory_manifests = AgentOperator(
        task_id="inventory_manifests",
        prompt="{{ ti.xcom_pull(task_ids='prepare_input') }}",
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are a customs inspector. Use the filesystem hook tools to "
            "complete the task autonomously — do NOT ask the user for "
            "confirmation. Call list_files(subdir='cargo_manifests') to "
            "enumerate manifests, then read_file(relative_path=...) on each "
            "one, then answer the question with your conclusion."
        ),
        toolsets=[
            HookToolset(
                hook=FixturesHook(fs_conn_id="fixtures_fs"),
                allowed_methods=["list_files", "read_file"],
            )
        ],
    )

    @task
    def consume_output(answer: str) -> None:
        print(f"Agent answer:\n{answer}")

    question = prepare_input()
    question >> inventory_manifests
    consume_output(inventory_manifests.output)


example_agent_hook_toolset()
