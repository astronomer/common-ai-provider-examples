"""Airflow task try number from the worker process environment."""

from __future__ import annotations

import os


def task_try_number() -> int:
    """Return the current task try number (1 on first run), or 1 if unset/invalid."""
    raw = os.environ.get("AIRFLOW_CTX_TRY_NUMBER") or os.environ.get(
        "AIRFLOW_CTX_TASK_TRY_NUMBER"
    )
    if raw is None:
        return 1
    try:
        return int(raw)
    except ValueError:
        return 1
