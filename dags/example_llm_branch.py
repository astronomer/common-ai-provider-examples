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

from airflow.sdk import dag, task


MANIFEST_DIR = Path("/usr/local/airflow/include/fixtures/cargo_manifests")


@dag(
    dag_id="example_llm_branch",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
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
            "You are customs control at Earth Spacedock. Route each inbound "
            "cargo manifest to exactly one handling lane. Use 'fast_lane' for "
            "cleanly declared, low-hazard cargo, 'customs_review' when "
            "paperwork is incomplete or items are ambiguous, and 'quarantine' "
            "when hazards, expired certifications, or unregistered origins "
            "are present."
        ),
    )
    def route_cargo(manifest_json: str) -> str:
        return f"Route this cargo manifest:\n{manifest_json}"

    @task
    def fast_lane() -> None:
        print("Cargo cleared via fast lane.")

    @task
    def customs_review() -> None:
        print("Cargo held for customs review.")

    @task
    def quarantine() -> None:
        print("Cargo placed in hazmat quarantine.")

    route_cargo(prepare_input()) >> [fast_lane(), customs_review(), quarantine()]


example_llm_branch()
