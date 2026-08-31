"""
## email_routing

Support inbox triage with `@task.llm`.

Dynamic task mapping fans each email out into a task group that classifies it
into an incident priority from P0 to P4 using a Pydantic `output_type`, then
routes it with an ordinary `@task.branch`. The model decides what the email is,
Airflow decides where it goes.

Compare with `example_llm_branch`, where the model picks the branch itself.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from airflow.sdk import chain, dag, task, task_group

from include.email_server import (
    EMAIL_CLASSIFICATION_SYSTEM_PROMPT,
    fetch_emails_from_server,
)


class EmailClassification(BaseModel):
    priority: Literal["P0", "P1", "P2", "P3", "P4"] = Field(
        description="Incident-style severity, P0 most urgent, P4 least"
    )


@dag(
    dag_id="email_routing",
    tags=[
        "common-ai",
        "use-case",
        "task.llm",
        "structured-output",
        "dynamic-task-mapping",
    ],
    doc_md=__doc__,
)
def email_routing():
    @task
    def fetch_email() -> list[str]:
        return fetch_emails_from_server()

    @task_group
    def process_email(email_text: str):
        @task.llm(
            llm_conn_id="pydanticai_default",
            system_prompt=EMAIL_CLASSIFICATION_SYSTEM_PROMPT,
            output_type=EmailClassification,
        )
        def classify_email(email_text: str) -> str:
            return f"Classify this email:\n\n{email_text}"

        @task.branch
        def route_by_priority(classification: EmailClassification) -> str:
            if classification.priority in ("P0", "P1"):
                return "process_email.alert_human"
            if classification.priority in ("P2", "P3"):
                return "process_email.draft_and_review"
            return "process_email.send_faq_response"

        @task
        def alert_human(email_text: str) -> None: ...

        @task
        def draft_and_review(email_text: str) -> None: ...

        @task
        def send_faq_response(email_text: str) -> None: ...

        _classification = classify_email(email_text)
        _route = route_by_priority(_classification)

        chain(
            _route,
            [
                alert_human(email_text),
                draft_and_review(email_text),
                send_faq_response(email_text),
            ],
        )

    _fetch_email = fetch_email()

    process_email.expand(email_text=_fetch_email)


email_routing()
