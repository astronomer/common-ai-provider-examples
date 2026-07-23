"""
## example_llm_branch

Demonstrates `@task.llm_branch` / `LLMBranchOperator`. The LLM picks which
downstream cargo-handling branch to run given the raw cargo manifest.
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task, chain


MANIFEST_DIR = Path("/usr/local/airflow/include/fixtures/cargo_manifests")


@dag(
    dag_id="example_llm_branch",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "llm-branch"],
    doc_md=__doc__,
)
def example_llm_branch():
    @task
    def prepare_input() -> str:
        path = random.choice(sorted(MANIFEST_DIR.glob("manifest_*.json")))
        manifest = json.loads(path.read_text())
        print(f"Selected manifest: {path.name}")
        return json.dumps(manifest, indent=2)

    @task.llm_branch(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "Route each inbound cargo "
            "manifest to exactly one handling "
            "lane. Use 'fast_lane' for "
            "properly declared, low-hazard "
            "cargo, 'customs_review' when "
            "paperwork is incomplete or items "
            "are ambiguous, and 'send_back' "
            "when payment information is missing."
        ),
        allow_multiple_branches=False,
    )
    def route_cargo(manifest_json: str) -> str:
        return f"Route this cargo manifest:\n{manifest_json}"

    @task
    def fast_lane() -> None: ...

    @task
    def customs_review() -> None: ...

    @task
    def send_back() -> None: ...

    chain(
        route_cargo(prepare_input()), 
        [
            fast_lane(),
            customs_review(),
            send_back(),
        ]
    )


example_llm_branch()
