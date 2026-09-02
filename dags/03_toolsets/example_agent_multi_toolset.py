"""
## example_agent_multi_toolset

One agent, three toolsets: `SQLToolset` for the warehouse, `HookToolset` for
the fixtures filesystem, and a `LoggingToolset` wrapper so you can see which of
them the agent called.
"""

from __future__ import annotations

from airflow.providers.common.ai.toolsets.hook import HookToolset
from airflow.providers.common.ai.toolsets.logging import LoggingToolset
from airflow.providers.common.ai.toolsets.sql import SQLToolset
from airflow.providers.standard.hooks.filesystem import FSHook
from airflow.sdk import dag, task

from include.seed import seed_primary


@dag(
    tags=[
        "common-ai",
        "feature-example",
        "task.agent",
        "sql-toolset",
        "hook-toolset",
        "logging-toolset",
    ],
    doc_md=__doc__,
)
def example_agent_multi_toolset():
    @task
    def prepare_input() -> str:
        seed_primary()
        return (
            "Using SQL, list every pilot certified to fly 'heavy_transport' "
            "spacecraft. Then, using the filesystem hook, check whether a "
            "cargo manifest exists for each pilot's home station. Return a "
            "short bulleted report."
        )

    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You are an ops analyst. Use SQL tools for warehouse lookups and "
            "filesystem tools for file existence checks."
        ),
        toolsets=[
            LoggingToolset(
                wrapped=SQLToolset(
                    db_conn_id="space_logistics",
                    allowed_tables=["pilots", "spacecraft", "space_stations"],
                )
            ),
            HookToolset(
                hook=FSHook(fs_conn_id="fixtures_fs"),
                allowed_methods=["get_path"],
            ),
        ],
    )
    def cross_reference(question: str) -> str:
        return question

    @task
    def consume_output(answer: str) -> None:
        print(f"Cross-reference report:\n{answer}")

    consume_output(cross_reference(prepare_input()))


example_agent_multi_toolset()
