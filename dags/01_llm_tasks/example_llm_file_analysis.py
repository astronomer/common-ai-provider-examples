"""
## example_llm_file_analysis

`@task.llm_file_analysis` / `LLMFileAnalysisOperator` reading the shipped
anomaly report over a `file://` ObjectStoragePath URL and returning a
structured `FileAnalysisReport`.

To read the same report out of object storage instead, point `file_path` at an
s3://, gs:// or abfs:// URL and set `file_conn_id`.
"""

from __future__ import annotations

from pathlib import Path

from airflow.sdk import dag, task

from include.models import FileAnalysisReport


FIXTURE_PATH = "file:///usr/local/airflow/include/ship_reports/"


@dag(
    tags=[
        "common-ai",
        "feature-example",
        "task.llm_file_analysis",
        "structured-output",
    ],
    doc_md=__doc__,
)
def example_llm_file_analysis():
    @task
    def prepare_input() -> str:
        local = Path("/usr/local/airflow/include/ship_reports/")
        assert local.exists(), f"missing fixture: {local}"
        staged = sorted(p.name for p in local.rglob("*") if p.is_file())
        print(f"Staging {len(staged)} file(s) from {local}: {', '.join(staged)}")
        return FIXTURE_PATH

    # `file_conn_id` is left at its default of None: a file:// path resolves
    # through ObjectStoragePath without a connection. Point `file_path` at an
    # s3://, gs:// or abfs:// URL and set `file_conn_id` to read from object
    # storage instead -- the operator is otherwise unchanged.
    @task.llm_file_analysis(
        llm_conn_id="pydanticai_default",
        file_path=FIXTURE_PATH,
        max_files=100,
        max_file_size_bytes=1024 * 1024 * 10,
        max_text_chars=200000,
        output_type=FileAnalysisReport,
        multi_modal=True,
    )
    def analyze_log() -> str:
        return (
            "Read the mission log and return "
            "a structured FileAnalysisReport "
            "containing every distinct anomaly "
            "with an anomaly_type, a confidence "
            "score in [0, 1], and free-form notes."
        )

    @task
    def consume_output(report: FileAnalysisReport | dict) -> None:
        if isinstance(report, dict):
            report = FileAnalysisReport.model_validate(report)
        print(f"Title: {report.title}")
        for finding in report.findings:
            print(
                f" - {finding.anomaly_type} "
                f"(confidence={finding.confidence:.2f}): {finding.notes}"
            )

    staged_path = prepare_input()
    analysis = analyze_log()
    staged_path >> analysis
    consume_output(analysis)


example_llm_file_analysis()
