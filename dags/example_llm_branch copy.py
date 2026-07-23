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


@dag(
    dag_id="select_webinar_speaker",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "webinar", "llm-branch"],
    doc_md=__doc__,
)
def select_webinar_speaker():
    @task
    def get_webinar_topic() -> str:
        return "Common AI provider in Apache Airflow"

    @task.llm_branch(
        llm_conn_id="pydanticai_default",
        system_prompt=(
            "You need to select one or more speakers for the upcoming webinar. "
        ),
        allow_multiple_branches=True,
    )
    def select_speakers(webinar_topic: str) -> str:
        return f"Select one or more speakers for the upcoming webinar: {webinar_topic}"

    @task
    def marc_lamberti() -> None:
        print("Marc Lamberti")

    @task
    def volker_janz() -> None:
        print("Volker Janz")

    @task
    def tamara_fingerlin() -> None:
        print("Tamara Fingerlin")

    chain(
        select_speakers(get_webinar_topic()),
        [marc_lamberti(), volker_janz(), tamara_fingerlin()],
    )


select_webinar_speaker()
