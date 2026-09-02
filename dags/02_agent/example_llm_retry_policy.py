"""
## example_llm_retry_policy

`LLMRetryPolicy`, a pluggable retry policy that decides retries by having a
model read the exception.

Any operator's `retry_policy` takes it. When the task raises, the policy sends
the exception to `llm_conn_id` and the model answers retry or fail.
`fallback_rules` take over if the LLM call itself fails, so the task still
behaves predictably when the model is unreachable.

The task here raises a Postgres connection-pool error, which is transient and
the sort of failure a model should recognize as worth another attempt.
"""

from __future__ import annotations

from airflow.providers.common.ai.policies.retry import LLMRetryPolicy
from airflow.sdk import dag, task
from airflow.sdk.definitions.retry_policy import RetryAction, RetryRule
from pendulum import duration

llm_policy = LLMRetryPolicy(
    llm_conn_id="pydanticai_default",
    timeout=30.0,  # max seconds to wait for the LLM's verdict
    fallback_rules=[  # consulted only when the LLM call itself fails
        RetryRule(
            exception=ConnectionError,
            action=RetryAction.RETRY,
            retry_delay=duration(seconds=10),
        ),
        RetryRule(exception=PermissionError, action=RetryAction.FAIL),
    ],
)


@dag(
    tags=[
        "common-ai",
        "feature-example",
        "LLMRetryPolicy",
        "retry-policy",
    ],
    doc_md=__doc__,
)
def example_llm_retry_policy():
    @task(
        retries=5,
        retry_delay=duration(seconds=5),
        retry_policy=llm_policy,
    )
    def load_from_warehouse(**context):
        raise Exception(
            'connection to server at "db-host" (10.0.1.5), port 5432 failed: '
            "FATAL:  sorry, too many clients already"
        )

    load_from_warehouse()


example_llm_retry_policy()
